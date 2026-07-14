package com.example.data.model

import com.google.firebase.database.IgnoreExtraProperties

@IgnoreExtraProperties
data class ModeHistoryEntry(
    val mode: String = "",
    val changed_at: String = ""
)
