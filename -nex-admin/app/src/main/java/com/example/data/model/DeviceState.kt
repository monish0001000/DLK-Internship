package com.example.data.model

import com.google.firebase.database.IgnoreExtraProperties

@IgnoreExtraProperties
data class DeviceState(
    val device_id: String = "laptop_01",
    val active_mode: String = "mode1",
    val last_ping: String = "",
    val admin_uid: String = "",
    val mode_history: List<ModeHistoryEntry> = emptyList()
)
