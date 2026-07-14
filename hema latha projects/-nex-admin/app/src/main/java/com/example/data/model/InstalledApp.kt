package com.example.data.model

import com.google.firebase.database.IgnoreExtraProperties

@IgnoreExtraProperties
data class InstalledApp(
    val id: String = "",
    val name: String = "",
    val publisher: String = "",
    val version: String = "",
    val status: String = "",
    val iconUrl: String = ""
)
