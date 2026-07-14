package com.example.data.model

import com.google.firebase.firestore.DocumentId
import com.google.firebase.firestore.IgnoreExtraProperties

@IgnoreExtraProperties
data class ActivityLog(
    @DocumentId
    val id: String = "",
    val action: String = "", // "Login", "Logout", "User Added", "User Updated", "User Deleted"
    val timestamp: Long = System.currentTimeMillis(),
    val adminEmail: String = "",
    val details: String = ""
)
