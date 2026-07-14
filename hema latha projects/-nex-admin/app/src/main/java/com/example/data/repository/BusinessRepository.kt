package com.example.data.repository

import com.example.data.model.ActivityLog
import com.example.data.model.SystemSettings
import com.example.data.model.User
import com.google.android.gms.tasks.Task
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.Query
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

class BusinessRepository {
    private val firestore = FirebaseFirestore.getInstance()

    // Helper to safely await Google Task results using coroutines
    private suspend fun <T> Task<T>.awaitTask(): T = suspendCancellableCoroutine { continuation ->
        addOnCompleteListener { task ->
            if (task.isSuccessful) {
                continuation.resume(task.result)
            } else {
                continuation.resumeWithException(task.exception ?: RuntimeException("Firestore task failed"))
            }
        }
    }

    // --- Users Collection ---
    fun observeUsers(): Flow<List<User>> = callbackFlow {
        val listenerRegistration = firestore.collection("users")
            .orderBy("createdAt", Query.Direction.DESCENDING)
            .addSnapshotListener { snapshot, error ->
                if (error != null) {
                    close(error)
                    return@addSnapshotListener
                }
                val usersList = snapshot?.documents?.mapNotNull { doc ->
                    doc.toObject(User::class.java)?.copy(id = doc.id)
                } ?: emptyList()
                trySend(usersList)
            }
        awaitClose { listenerRegistration.remove() }
    }

    suspend fun addUser(user: User): Result<Unit> = runCatching {
        firestore.collection("users")
            .add(user)
            .awaitTask()
        Unit
    }

    suspend fun updateUser(user: User): Result<Unit> = runCatching {
        firestore.collection("users")
            .document(user.id)
            .set(user)
            .awaitTask()
        Unit
    }

    suspend fun deleteUser(userId: String): Result<Unit> = runCatching {
        firestore.collection("users")
            .document(userId)
            .delete()
            .awaitTask()
        Unit
    }

    suspend fun checkEmailExists(email: String, excludeUserId: String? = null): Boolean {
        return try {
            val snapshot = firestore.collection("users")
                .whereEqualTo("email", email)
                .get()
                .awaitTask()
            val docs = snapshot.documents
            if (excludeUserId != null) {
                docs.any { it.id != excludeUserId }
            } else {
                docs.isNotEmpty()
            }
        } catch (e: Exception) {
            false
        }
    }

    // --- Activity Logs Collection ---
    fun observeActivityLogs(): Flow<List<ActivityLog>> = callbackFlow {
        val listenerRegistration = firestore.collection("activity_logs")
            .orderBy("timestamp", Query.Direction.DESCENDING)
            .addSnapshotListener { snapshot, error ->
                if (error != null) {
                    close(error)
                    return@addSnapshotListener
                }
                val logsList = snapshot?.documents?.mapNotNull { doc ->
                    doc.toObject(ActivityLog::class.java)?.copy(id = doc.id)
                } ?: emptyList()
                trySend(logsList)
            }
        awaitClose { listenerRegistration.remove() }
    }

    suspend fun addActivityLog(log: ActivityLog): Result<Unit> = runCatching {
        firestore.collection("activity_logs")
            .add(log)
            .awaitTask()
        Unit
    }

    // --- Settings Collection ---
    fun observeSettings(): Flow<SystemSettings> = callbackFlow {
        val listenerRegistration = firestore.collection("settings")
            .document("app_config")
            .addSnapshotListener { snapshot, error ->
                if (error != null) {
                    close(error)
                    return@addSnapshotListener
                }
                val settings = snapshot?.toObject(SystemSettings::class.java) ?: SystemSettings()
                trySend(settings)
            }
        awaitClose { listenerRegistration.remove() }
    }

    suspend fun saveSettings(settings: SystemSettings): Result<Unit> = runCatching {
        firestore.collection("settings")
            .document("app_config")
            .set(settings)
            .awaitTask()
        Unit
    }
}
