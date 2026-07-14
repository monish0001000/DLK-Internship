package com.example.data.repository

import com.example.data.model.DeviceState
import com.example.data.model.ModeHistoryEntry
import com.google.firebase.database.DataSnapshot
import com.google.firebase.database.DatabaseError
import com.google.firebase.database.DatabaseReference
import com.google.firebase.database.FirebaseDatabase
import com.google.firebase.database.ValueEventListener
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

class DeviceRepository {

    private val database: FirebaseDatabase by lazy { FirebaseDatabase.getInstance() }
    private val rootRef: DatabaseReference by lazy { database.reference }

    /**
     * Listens to the entire DeviceState real-time node.
     */
    fun observeDeviceState(): Flow<DeviceState> = callbackFlow {
        val listener = object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                try {
                    val deviceId = snapshot.child("device_id").getValue(String::class.java) ?: "laptop_01"
                    val activeMode = snapshot.child("active_mode").getValue(String::class.java) ?: "mode1"
                    val lastPing = snapshot.child("last_ping").getValue(String::class.java) ?: ""
                    val adminUid = snapshot.child("admin_uid").getValue(String::class.java) ?: ""

                    // De-serialize history safely since list structures in Firebase can be lists or maps
                    val historyList = mutableListOf<ModeHistoryEntry>()
                    val historySnapshot = snapshot.child("mode_history")
                    if (historySnapshot.exists()) {
                        if (historySnapshot.hasChildren()) {
                            for (child in historySnapshot.children) {
                                val entry = child.getValue(ModeHistoryEntry::class.java)
                                if (entry != null) {
                                    historyList.add(entry)
                                }
                            }
                        }
                    }

                    val deviceState = DeviceState(
                        device_id = deviceId,
                        active_mode = activeMode,
                        last_ping = lastPing,
                        admin_uid = adminUid,
                        mode_history = historyList
                    )
                    trySend(deviceState)
                } catch (e: Exception) {
                    // Fallback to default state
                    trySend(DeviceState())
                }
            }

            override fun onCancelled(error: DatabaseError) {
                close(error.toException())
            }
        }

        rootRef.addValueEventListener(listener)
        awaitClose { rootRef.removeEventListener(listener) }
    }

    /**
     * Updates active_mode and records to mode_history.
     */
    fun updateActiveMode(mode: String, adminUid: String, onComplete: (Result<Unit>) -> Unit) {
        val updates = HashMap<String, Any>()
        updates["active_mode"] = mode
        updates["admin_uid"] = adminUid

        // Create the audit log timestamp in standard ISO 8601 UTC format
        val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
            timeZone = TimeZone.getTimeZone("UTC")
        }
        val currentTimestamp = sdf.format(Date())

        // Fetch current history, append to it, and update root
        rootRef.child("mode_history").get().addOnCompleteListener { task ->
            if (task.isSuccessful) {
                val snapshot = task.result
                val historyList = mutableListOf<Map<String, String>>()
                
                // Read existing entries
                if (snapshot.exists()) {
                    for (child in snapshot.children) {
                        val m = child.child("mode").getValue(String::class.java) ?: ""
                        val c = child.child("changed_at").getValue(String::class.java) ?: ""
                        if (m.isNotEmpty()) {
                            historyList.add(mapOf("mode" to m, "changed_at" to c))
                        }
                    }
                }

                // Add the new state transition entry
                historyList.add(mapOf("mode" to mode, "changed_at" to currentTimestamp))

                // Keep only the last 50 history entries to keep database node size elegant
                val limitedHistory = if (historyList.size > 50) historyList.takeLast(50) else historyList
                updates["mode_history"] = limitedHistory

                // Perform the atomic multi-path update
                rootRef.updateChildren(updates).addOnCompleteListener { updateTask ->
                    if (updateTask.isSuccessful) {
                        onComplete(Result.success(Unit))
                    } else {
                        onComplete(Result.failure(updateTask.exception ?: Exception("Failed to update active mode.")))
                    }
                }
            } else {
                // If history retrieval fails, just write the active mode itself
                updates["mode_history"] = listOf(mapOf("mode" to mode, "changed_at" to currentTimestamp))
                rootRef.updateChildren(updates).addOnCompleteListener { updateTask ->
                    if (updateTask.isSuccessful) {
                        onComplete(Result.success(Unit))
                    } else {
                        onComplete(Result.failure(updateTask.exception ?: Exception("Failed to update active mode.")))
                    }
                }
            }
        }
    }
}
