package com.example.data.model

import com.google.firebase.firestore.DocumentId
import com.google.firebase.firestore.IgnoreExtraProperties

@IgnoreExtraProperties
data class User(
    @DocumentId
    val id: String = "",
    val name: String = "",
    val email: String = "",
    val status: String = "Active", // "Active" or "Inactive"
    val createdAt: Long = System.currentTimeMillis()
)
