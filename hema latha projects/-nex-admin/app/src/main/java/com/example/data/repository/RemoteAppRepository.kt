package com.example.data.repository

import com.google.firebase.database.DatabaseReference
import com.google.firebase.database.FirebaseDatabase
import com.google.firebase.database.ServerValue

class RemoteAppRepository {
    private val database: FirebaseDatabase by lazy { FirebaseDatabase.getInstance() }
    private val remoteAppLinkRef: DatabaseReference by lazy { database.getReference("remote_app_link") }

    fun updateRemoteAppLink(downloadUrl: String, updatedBy: String, onComplete: (Result<Unit>) -> Unit) {
        val data = hashMapOf<String, Any>(
            "downloadUrl" to downloadUrl,
            "updatedBy" to updatedBy,
            "updatedAt" to ServerValue.TIMESTAMP
        )
        remoteAppLinkRef.setValue(data).addOnCompleteListener { task ->
            if (task.isSuccessful) {
                onComplete(Result.success(Unit))
            } else {
                onComplete(Result.failure(task.exception ?: Exception("Failed to update remote app link")))
            }
        }
    }
}
