package com.example.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.model.ActivityLog
import com.example.data.model.SystemSettings
import com.example.data.model.User
import com.example.data.repository.BusinessRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

sealed class UserUiState {
    object Loading : UserUiState()
    data class Success(val users: List<User>) : UserUiState()
    data class Error(val message: String) : UserUiState()
    object Empty : UserUiState()
}

class BusinessViewModel : ViewModel() {
    private val repository = BusinessRepository()

    // Active admin email to populate logs
    private val _adminEmail = MutableStateFlow("admin@nexshield.com")
    val adminEmail: StateFlow<String> = _adminEmail.asStateFlow()

    fun setAdminEmail(email: String) {
        if (email.isNotEmpty()) {
            _adminEmail.value = email
        }
    }

    // Live search and filter states
    val searchQuery = MutableStateFlow("")
    val sortBy = MutableStateFlow("latest") // "latest" or "name_az"
    val filterStatus = MutableStateFlow("all") // "all", "Active", "Inactive"

    // Raw streams from Firestore
    private val _rawUsers = MutableStateFlow<List<User>>(emptyList())
    val rawUsers: StateFlow<List<User>> = _rawUsers.asStateFlow()
    private val _usersError = MutableStateFlow<String?>(null)
    private val _usersLoading = MutableStateFlow(true)

    // Combined filtered, sorted users stream
    val userUiState: StateFlow<UserUiState> = combine(
        _rawUsers,
        searchQuery,
        sortBy,
        filterStatus,
        _usersLoading,
        _usersError
    ) { array ->
        val rawUsers = array[0] as List<User>
        val query = array[1] as String
        val sort = array[2] as String
        val filter = array[3] as String
        val loading = array[4] as Boolean
        val error = array[5] as String?

        if (error != null) {
            return@combine UserUiState.Error(error)
        }
        if (loading) {
            return@combine UserUiState.Loading
        }

        var filtered = rawUsers.filter { user ->
            val matchesQuery = user.name.contains(query, ignoreCase = true) || 
                               user.email.contains(query, ignoreCase = true)
            val matchesFilter = when (filter) {
                "Active" -> user.status.equals("Active", ignoreCase = true)
                "Inactive" -> user.status.equals("Inactive", ignoreCase = true)
                else -> true
            }
            matchesQuery && matchesFilter
        }

        filtered = when (sort) {
            "name_az" -> filtered.sortedBy { it.name.lowercase() }
            else -> filtered.sortedByDescending { it.createdAt }
        }

        if (filtered.isEmpty()) {
            UserUiState.Empty
        } else {
            UserUiState.Success(filtered)
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), UserUiState.Loading)

    // Activity Logs State
    private val _activityLogs = MutableStateFlow<List<ActivityLog>>(emptyList())
    val activityLogs: StateFlow<List<ActivityLog>> = _activityLogs.asStateFlow()

    // System Settings State
    private val _systemSettings = MutableStateFlow(SystemSettings())
    val systemSettings: StateFlow<SystemSettings> = _systemSettings.asStateFlow()

    // Action Result Streams (Single Event Alerts)
    private val _crudResult = MutableSharedFlow<Result<String>>()
    val crudResult = _crudResult.asSharedFlow()

    init {
        startObservingData()
    }

    fun refreshData() {
        startObservingData()
    }

    fun startObservingData() {
        // Observe Users
        viewModelScope.launch {
            _usersLoading.value = true
            repository.observeUsers()
                .catch { e ->
                    _usersError.value = e.message ?: "Failed to load users."
                    _usersLoading.value = false
                }
                .collect { list ->
                    _rawUsers.value = list
                    _usersError.value = null
                    _usersLoading.value = false
                }
        }

        // Observe Logs
        viewModelScope.launch {
            repository.observeActivityLogs()
                .catch { e -> e.printStackTrace() }
                .collect { logs ->
                    _activityLogs.value = logs
                }
        }

        // Observe Settings
        viewModelScope.launch {
            repository.observeSettings()
                .catch { e -> e.printStackTrace() }
                .collect { settings ->
                    _systemSettings.value = settings
                }
        }
    }

    // --- CRUD User ---
    fun addUser(name: String, email: String, status: String) {
        viewModelScope.launch {
            if (name.isBlank() || email.isBlank()) {
                _crudResult.emit(Result.failure(Exception("All fields must be filled.")))
                return@launch
            }
            if (repository.checkEmailExists(email)) {
                _crudResult.emit(Result.failure(Exception("Email is already registered.")))
                return@launch
            }

            val newUser = User(name = name, email = email, status = status, createdAt = System.currentTimeMillis())
            val res = repository.addUser(newUser)
            if (res.isSuccess) {
                logActivity("User Added", "Created account for $name ($email)")
                _crudResult.emit(Result.success("User added successfully."))
            } else {
                _crudResult.emit(Result.failure(res.exceptionOrNull() ?: Exception("Failed to add user.")))
            }
        }
    }

    fun updateUser(userId: String, name: String, email: String, status: String) {
        viewModelScope.launch {
            if (name.isBlank() || email.isBlank()) {
                _crudResult.emit(Result.failure(Exception("All fields must be filled.")))
                return@launch
            }
            if (repository.checkEmailExists(email, userId)) {
                _crudResult.emit(Result.failure(Exception("Email is already registered.")))
                return@launch
            }

            val updatedUser = User(id = userId, name = name, email = email, status = status)
            val res = repository.updateUser(updatedUser)
            if (res.isSuccess) {
                logActivity("User Updated", "Modified profile details for $name")
                _crudResult.emit(Result.success("User updated successfully."))
            } else {
                _crudResult.emit(Result.failure(res.exceptionOrNull() ?: Exception("Failed to update user.")))
            }
        }
    }

    fun deleteUser(userId: String, name: String, email: String) {
        viewModelScope.launch {
            val res = repository.deleteUser(userId)
            if (res.isSuccess) {
                logActivity("User Deleted", "Removed account of $name ($email)")
                _crudResult.emit(Result.success("User deleted successfully."))
            } else {
                _crudResult.emit(Result.failure(res.exceptionOrNull() ?: Exception("Failed to delete user.")))
            }
        }
    }

    // --- Action Logs ---
    fun logActivity(action: String, details: String) {
        viewModelScope.launch {
            val log = ActivityLog(
                action = action,
                timestamp = System.currentTimeMillis(),
                adminEmail = _adminEmail.value,
                details = details
            )
            repository.addActivityLog(log)
        }
    }

    // --- Settings CRUD ---
    fun updateSystemSettings(theme: Boolean, critical: Boolean, stateAlert: Boolean) {
        viewModelScope.launch {
            val config = SystemSettings(
                themeEnforced = theme,
                criticalAlertsEnabled = critical,
                stateAlertsEnabled = stateAlert,
                updatedBy = _adminEmail.value,
                updatedAt = System.currentTimeMillis()
            )
            repository.saveSettings(config)
        }
    }
}
