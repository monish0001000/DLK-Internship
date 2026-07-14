package com.example.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.model.DeviceState
import com.example.data.repository.DeviceRepository
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

class DashboardViewModel(
    private val deviceRepository: DeviceRepository = DeviceRepository()
) : ViewModel() {

    private val _deviceState = MutableStateFlow<DeviceState>(DeviceState())
    val deviceState: StateFlow<DeviceState> = _deviceState.asStateFlow()

    private val _isDeviceOnline = MutableStateFlow(false)
    val isDeviceOnline: StateFlow<Boolean> = _isDeviceOnline.asStateFlow()

    private val _modeChangeResult = MutableStateFlow<Result<Unit>?>(null)
    val modeChangeResult: StateFlow<Result<Unit>?> = _modeChangeResult.asStateFlow()

    private var heartbeatCheckJob: Job? = null
    private var observeJob: Job? = null

    init {
        // Start periodic liveness updates to dynamically toggle status on UI
        startLivenessTicker()
    }

    fun startObserving() {
        if (observeJob?.isActive == true) return

        observeJob = viewModelScope.launch {
            try {
                deviceRepository.observeDeviceState().collectLatest { state ->
                    _deviceState.value = state
                    checkDeviceLiveness(state.last_ping)
                }
            } catch (e: Exception) {
                // Prevent crash from permission denied or other database exceptions
                e.printStackTrace()
            }
        }
    }

    fun stopObserving() {
        observeJob?.cancel()
        observeJob = null
    }

    private fun startLivenessTicker() {
        heartbeatCheckJob?.cancel()
        heartbeatCheckJob = viewModelScope.launch {
            while (true) {
                checkDeviceLiveness(_deviceState.value.last_ping)
                delay(10000) // Re-evaluate status every 10 seconds
            }
        }
    }

    /**
     * Parses the ISO 8601 UTC timestamp and compares it to current system time.
     * Threshold is 90 seconds (3 missed heartbeats).
     */
    fun checkDeviceLiveness(lastPingIso: String) {
        if (lastPingIso.isEmpty()) {
            _isDeviceOnline.value = false
            return
        }

        try {
            val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
                timeZone = TimeZone.getTimeZone("UTC")
            }
            val lastPingDate = sdf.parse(lastPingIso)
            if (lastPingDate != null) {
                val lastPingMs = lastPingDate.time
                val currentMs = System.currentTimeMillis()
                
                // Difference in seconds
                val diffSeconds = (currentMs - lastPingMs) / 1000
                
                // Offline threshold is 90 seconds (3 missed heartbeats)
                _isDeviceOnline.value = diffSeconds < 90
            } else {
                _isDeviceOnline.value = false
            }
        } catch (e: Exception) {
            _isDeviceOnline.value = false
        }
    }

    /**
     * Trigger a secure state update to Firebase Realtime Database
     */
    fun changeActiveMode(mode: String, adminUid: String) {
        viewModelScope.launch {
            deviceRepository.updateActiveMode(mode, adminUid) { result ->
                _modeChangeResult.value = result
            }
        }
    }

    fun clearModeChangeResult() {
        _modeChangeResult.value = null
    }

    override fun onCleared() {
        super.onCleared()
        heartbeatCheckJob?.cancel()
    }
}
