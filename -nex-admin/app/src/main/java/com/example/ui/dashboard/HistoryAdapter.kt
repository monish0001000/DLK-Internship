package com.example.ui.dashboard

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.data.model.ModeHistoryEntry
import com.example.databinding.ItemModeHistoryBinding
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone

class HistoryAdapter : ListAdapter<ModeHistoryEntry, HistoryAdapter.ViewHolder>(DiffCallback) {

    class ViewHolder(private val binding: ItemModeHistoryBinding) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(entry: ModeHistoryEntry) {
            binding.tvHistoryMode.text = "Mode: ${entry.mode}"
            
            // Render changed_at beautifully. Format the ISO date nicely for the UI.
            val formattedTime = formatIsoToReadable(entry.changed_at)
            binding.tvHistoryTime.text = "Enforced: $formattedTime"
        }

        private fun formatIsoToReadable(isoString: String): String {
            if (isoString.isEmpty()) return "N/A"
            return try {
                val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
                    timeZone = TimeZone.getTimeZone("UTC")
                }
                val date = inputFormat.parse(isoString) ?: return isoString
                
                // Format in user's default locale/timezone for supreme usability
                val outputFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
                outputFormat.format(date)
            } catch (e: Exception) {
                isoString
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemModeHistoryBinding.inflate(
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
        private val DiffCallback = object : DiffUtil.ItemCallback<ModeHistoryEntry>() {
            override fun areItemsTheSame(oldItem: ModeHistoryEntry, newItem: ModeHistoryEntry): Boolean {
                return oldItem.changed_at == newItem.changed_at
            }

            override fun areContentsTheSame(oldItem: ModeHistoryEntry, newItem: ModeHistoryEntry): Boolean {
                return oldItem == newItem
            }
        }
    }
}
