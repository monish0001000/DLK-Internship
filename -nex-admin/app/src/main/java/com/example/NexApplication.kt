package com.example

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import com.google.firebase.FirebaseApp
import com.google.firebase.database.FirebaseDatabase

class NexApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        
        // 1. Initialize Firebase
        var app: FirebaseApp? = null
        try {
            app = FirebaseApp.initializeApp(this)
        } catch (e: Exception) {
            e.printStackTrace()
        }

        if (app == null || FirebaseApp.getApps(this).isEmpty()) {
            try {
                val options = com.google.firebase.FirebaseOptions.Builder()
                    .setApplicationId("1:1234567890:android:abcdef123456")
                    .setApiKey("AIzaSyDummyApiKeyForCompilationAndPreview")
                    .setDatabaseUrl("https://nex-launcher-default-rtdb.firebaseio.com")
                    .setProjectId("nex-launcher-default")
                    .build()
                FirebaseApp.initializeApp(this, options)
            } catch (ex: Exception) {
                ex.printStackTrace()
            }
        }
        
        // 2. Enable Firebase Database Offline Persistence for offline resiliency
        try {
            FirebaseDatabase.getInstance().setPersistenceEnabled(true)
        } catch (e: Exception) {
            // Keep going if already set or initialization fails in test environments
        }
        
        // 3. Create FCM Notification Channel
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channelId = getString(R.string.notification_channel_id)
            val channelName = getString(R.string.notification_channel_name)
            val channelDescription = getString(R.string.notification_channel_desc)
            val importance = NotificationManager.IMPORTANCE_HIGH
            
            val channel = NotificationChannel(channelId, channelName, importance).apply {
                description = channelDescription
                enableLights(true)
                enableVibration(true)
            }
            
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }
}
