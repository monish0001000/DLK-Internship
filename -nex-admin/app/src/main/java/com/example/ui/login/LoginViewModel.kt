package com.example.ui.login

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.repository.AuthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class LoginViewModel(
    private val authRepository: AuthRepository = AuthRepository()
) : ViewModel() {

    private val _loginState = MutableStateFlow<LoginState>(LoginState.Idle)
    val loginState: StateFlow<LoginState> = _loginState.asStateFlow()

    private val _passwordResetState = MutableStateFlow<LoginState>(LoginState.Idle)
    val passwordResetState: StateFlow<LoginState> = _passwordResetState.asStateFlow()

    fun isUserLoggedIn(): Boolean {
        return authRepository.getCurrentUser() != null
    }

    fun getCurrentUserId(): String {
        return authRepository.getCurrentUser()?.uid ?: ""
    }

    fun getCurrentUserEmail(): String {
        return authRepository.getCurrentUser()?.email ?: "admin@nexshield.com"
    }

    fun login(email: String, password: String) {
        if (!isEmailValid(email)) {
            _loginState.value = LoginState.Error("Invalid email address format.")
            return
        }
        if (password.length < 6) {
            _loginState.value = LoginState.Error("Password must be at least 6 characters.")
            return
        }

        _loginState.value = LoginState.Loading
        viewModelScope.launch {
            authRepository.login(email, password)
                .onSuccess { user ->
                    _loginState.value = LoginState.Success(user.uid)
                }
                .onFailure { exception ->
                    _loginState.value = LoginState.Error(exception.localizedMessage ?: "Authentication failed.")
                }
        }
    }

    fun sendPasswordReset(email: String) {
        if (!isEmailValid(email)) {
            _passwordResetState.value = LoginState.Error("Please provide a valid email address.")
            return
        }

        _passwordResetState.value = LoginState.Loading
        viewModelScope.launch {
            authRepository.sendPasswordResetEmail(email)
                .onSuccess {
                    _passwordResetState.value = LoginState.Success("")
                }
                .onFailure { exception ->
                    _passwordResetState.value = LoginState.Error(exception.localizedMessage ?: "Failed to send reset email.")
                }
        }
    }

    fun logout() {
        authRepository.logout()
        _loginState.value = LoginState.Idle
    }

    fun resetState() {
        _loginState.value = LoginState.Idle
        _passwordResetState.value = LoginState.Idle
    }

    private fun isEmailValid(email: String): Boolean {
        return email.isNotEmpty() && android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
}
