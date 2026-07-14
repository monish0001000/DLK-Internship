package com.example.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.repository.RemoteAppRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class AppPushViewModel(
    private val repository: RemoteAppRepository = RemoteAppRepository()
) : ViewModel() {

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _pushResult = MutableStateFlow<Result<Unit>?>(null)
    val pushResult: StateFlow<Result<Unit>?> = _pushResult.asStateFlow()

    fun pushAppLink(downloadUrl: String, updatedBy: String) {
        if (downloadUrl.isBlank()) {
            _pushResult.value = Result.failure(Exception("URL cannot be empty"))
            return
        }
        if (!downloadUrl.startsWith("https://", ignoreCase = true)) {
            _pushResult.value = Result.failure(Exception("URL must start with https://"))
            return
        }

        _isLoading.value = true
        _pushResult.value = null

        viewModelScope.launch {
            repository.updateRemoteAppLink(downloadUrl, updatedBy) { result ->
                _isLoading.value = false
                _pushResult.value = result
            }
        }
    }

    fun clearResult() {
        _pushResult.value = null
    }
}
