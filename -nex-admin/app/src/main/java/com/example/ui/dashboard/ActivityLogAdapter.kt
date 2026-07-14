package com.example.ui.dashboard

import android.graphics.Color
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.data.model.ActivityLog
import com.example.databinding.ItemActivityLogBinding
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone

class ActivityLogAdapter : ListAdapter<ActivityLog, ActivityLogAdapter.ViewHolder>(DiffCallback) {

    class ViewHolder(private val binding: ItemActivityLogBinding) : RecyclerView.ViewHolder(binding.root) {

        fun bind(log: ActivityLog) {
            binding.tvLogEvent.text = log.action
            binding.tvLogDescription.text = log.details
            binding.tvLogActor.text = "By: ${log.adminEmail}"
            binding.tvLogTimestamp.text = formatTimestamp(log.timestamp)

            // Dynamic iconography & tinting based on log event type
            val context = binding.root.context
            when {
                log.action.contains("LOGIN", ignoreCase = true) || log.action.contains("LOGOUT", ignoreCase = true) -> {
                    binding.ivLogIcon.setImageResource(android.graphics.drawable.Icon.createWithResource(
                        context, android.R.drawable.ic_lock_idle_lock
                    ).resId)
                    binding.ivLogIcon.setColorFilter(Color.parseColor("#10B981")) // Green for auth
                    binding.cardLogIcon.setCardBackgroundColor(Color.parseColor("#1A10B981"))
                }
                log.action.contains("SETTINGS", ignoreCase = true) || log.action.contains("THEME", ignoreCase = true) -> {
                    binding.ivLogIcon.setImageResource(android.graphics.drawable.Icon.createWithResource(
                        context, android.R.drawable.ic_menu_preferences
                    ).resId)
                    binding.ivLogIcon.setColorFilter(Color.parseColor("#2979FF")) // Blue for settings
                    binding.cardLogIcon.setCardBackgroundColor(Color.parseColor("#1A2979FF"))
                }
                log.action.contains("DELETE", ignoreCase = true) -> {
                    binding.ivLogIcon.setImageResource(android.graphics.drawable.Icon.createWithResource(
                        context, android.R.drawable.ic_menu_delete
                    ).resId)
                    binding.ivLogIcon.setColorFilter(Color.parseColor("#EF4444")) // Red for delete
                    binding.cardLogIcon.setCardBackgroundColor(Color.parseColor("#1AEF4444"))
                }
                else -> {
                    binding.ivLogIcon.setImageResource(android.graphics.drawable.Icon.createWithResource(
                        context, android.R.drawable.ic_menu_myplaces
                    ).resId)
                    binding.ivLogIcon.setColorFilter(Color.parseColor("#F59E0B")) // Orange for updates/creations
                    binding.cardLogIcon.setCardBackgroundColor(Color.parseColor("#1AF59E0B"))
                }
            }
        }

        private fun formatTimestamp(timestampMs: Long): String {
            if (timestampMs <= 0) return "N/A"
            return try {
                val date = java.util.Date(timestampMs)
                val outputFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
                outputFormat.format(date)
            } catch (e: Exception) {
                "N/A"
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemActivityLogBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    companion object {
        private val DiffCallback = object : DiffUtil.ItemCallback<ActivityLog>() {
            override fun areItemsTheSame(oldItem: ActivityLog, newItem: ActivityLog): Boolean {
                return oldItem.id == newItem.id
            }

            override fun areContentsTheSame(oldItem: ActivityLog, newItem: ActivityLog): Boolean {
                return oldItem == newItem
            }
        }
    }
}
