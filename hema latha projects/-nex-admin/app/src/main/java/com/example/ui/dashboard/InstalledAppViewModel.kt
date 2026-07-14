package com.example.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.model.InstalledApp
import com.example.data.repository.InstalledAppRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

sealed class InstalledAppsUiState {
    object Loading : InstalledAppsUiState()
    data class Success(val apps: List<InstalledApp>) : InstalledAppsUiState()
    data class Error(val message: String) : InstalledAppsUiState()
}

class InstalledAppViewModel(
    private val repository: InstalledAppRepository = InstalledAppRepository()
) : ViewModel() {

    private val _uiState = MutableStateFlow<InstalledAppsUiState>(InstalledAppsUiState.Loading)
    val uiState: StateFlow<InstalledAppsUiState> = _uiState.asStateFlow()

    private val _actionResult = MutableStateFlow<Result<Unit>?>(null)
    val actionResult: StateFlow<Result<Unit>?> = _actionResult.asStateFlow()

    private val _isActionLoading = MutableStateFlow(false)
    val isActionLoading: StateFlow<Boolean> = _isActionLoading.asStateFlow()

    init {
        observeInstalledApps()
    }

    fun observeInstalledApps() {
        _uiState.value = InstalledAppsUiState.Loading
        viewModelScope.launch {
            try {
                repository.observeInstalledApps().collectLatest { apps ->
                    _uiState.value = InstalledAppsUiState.Success(apps)
                }
            } catch (e: Exception) {
                _uiState.value = InstalledAppsUiState.Error(e.message ?: "Unknown error loading apps")
            }
        }
    }

    fun blockApp(appName: String) {
        _isActionLoading.value = true
        _actionResult.value = null
        viewModelScope.launch {
            repository.blockApp(appName) { result ->
                _isActionLoading.value = false
                _actionResult.value = result
            }
        }
    }

    fun uninstallApp(appName: String) {
        _isActionLoading.value = true
        _actionResult.value = null
        viewModelScope.launch {
            repository.uninstallApp(appName) { result ->
                _isActionLoading.value = false
                _actionResult.value = result
            }
        }
    }

    fun clearActionResult() {
        _actionResult.value = null
    }
}
