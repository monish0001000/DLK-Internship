package com.example.data.repository

import com.example.data.model.InstalledApp
import com.google.firebase.database.DataSnapshot
import com.google.firebase.database.DatabaseError
import com.google.firebase.database.DatabaseReference
import com.google.firebase.database.FirebaseDatabase
import com.google.firebase.database.ServerValue
import com.google.firebase.database.ValueEventListener
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

class InstalledAppRepository {

    private val database: FirebaseDatabase by lazy { FirebaseDatabase.getInstance() }
    private val installedAppsRef: DatabaseReference by lazy { database.getReference("installed_apps") }
    private val appCommandsRef: DatabaseReference by lazy { database.getReference("app_commands") }

    fun observeInstalledApps(): Flow<List<InstalledApp>> = callbackFlow {
        val listener = object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                try {
                    val appsList = mutableListOf<InstalledApp>()
                    if (snapshot.exists() && snapshot.hasChildren()) {
                        for (child in snapshot.children) {
                            val id = child.key ?: ""
                            val name = child.child("name").getValue(String::class.java) ?: ""
                            val publisher = child.child("publisher").getValue(String::class.java) ?: ""
                            val version = child.child("version").getValue(String::class.java) ?: ""
                            val status = child.child("status").getValue(String::class.java) ?: ""
                            val iconUrl = child.child("iconUrl").getValue(String::class.java) ?: ""

                            if (name.isNotEmpty()) {
                                appsList.add(
                                    InstalledApp(
                                        id = id,
                                        name = name,
                                        publisher = publisher,
                                        version = version,
                                        status = status,
                                        iconUrl = iconUrl
                                    )
                                )
                            }
                        }
                    }
                    trySend(appsList)
                } catch (e: Exception) {
                    trySend(emptyList())
                }
            }

            override fun onCancelled(error: DatabaseError) {
                close(error.toException())
            }
        }

        installedAppsRef.addValueEventListener(listener)
        awaitClose { installedAppsRef.removeEventListener(listener) }
    }

    fun blockApp(appName: String, onComplete: (Result<Unit>) -> Unit) {
        val commandData = hashMapOf<String, Any>(
            "command" to "block",
            "app" to appName,
            "timestamp" to ServerValue.TIMESTAMP
        )
        appCommandsRef.push().setValue(commandData).addOnCompleteListener { task ->
            if (task.isSuccessful) {
                onComplete(Result.success(Unit))
            } else {
                onComplete(Result.failure(task.exception ?: Exception("Failed to push block command")))
            }
        }
    }

    fun uninstallApp(appName: String, onComplete: (Result<Unit>) -> Unit) {
        val commandData = hashMapOf<String, Any>(
            "command" to "delete",
            "app" to appName,
            "timestamp" to ServerValue.TIMESTAMP
        )
        appCommandsRef.push().setValue(commandData).addOnCompleteListener { task ->
            if (task.isSuccessful) {
                onComplete(Result.success(Unit))
            } else {
                onComplete(Result.failure(task.exception ?: Exception("Failed to push delete command")))
            }
        }
    }
}
