package com.example.data.model

import com.google.firebase.firestore.DocumentId
import com.google.firebase.firestore.IgnoreExtraProperties

@IgnoreExtraProperties
data class SystemSettings(
    @DocumentId
    val id: String = "app_config",
    val themeEnforced: Boolean = true,
    val criticalAlertsEnabled: Boolean = true,
    val stateAlertsEnabled: Boolean = true,
    val updatedBy: String = "",
    val updatedAt: Long = System.currentTimeMillis()
)
