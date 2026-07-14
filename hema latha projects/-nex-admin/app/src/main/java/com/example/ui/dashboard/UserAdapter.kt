package com.example.ui.dashboard

import android.graphics.Color
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.data.model.User
import com.example.databinding.ItemUserBinding
import java.util.Locale

class UserAdapter(
    private val onUserClicked: (User) -> Unit
) : ListAdapter<User, UserAdapter.ViewHolder>(DiffCallback) {

    class ViewHolder(
        private val binding: ItemUserBinding,
        private val onUserClicked: (User) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(user: User) {
            binding.tvUserName.text = user.name
            binding.tvUserEmail.text = user.email
            binding.tvInitials.text = getInitials(user.name)

            val isActive = user.status.equals("Active", ignoreCase = true)
            binding.tvUserStatusBadge.text = if (isActive) "Active" else "Inactive"
            
            if (isActive) {
                binding.cardStatusBadge.setCardBackgroundColor(Color.parseColor("#1A10B981")) // Light transparent green
                binding.tvUserStatusBadge.setTextColor(Color.parseColor("#10B981"))
            } else {
                binding.cardStatusBadge.setCardBackgroundColor(Color.parseColor("#1AEF4444")) // Light transparent red
                binding.tvUserStatusBadge.setTextColor(Color.parseColor("#EF4444"))
            }

            binding.root.setOnClickListener {
                onUserClicked(user)
            }
        }

        private fun getInitials(name: String): String {
            if (name.isBlank()) return "--"
            val parts = name.trim().split("\\s+".toRegex())
            if (parts.size >= 2) {
                return (parts[0].take(1) + parts[1].take(1)).uppercase(Locale.getDefault())
            }
            return parts[0].take(2).uppercase(Locale.getDefault())
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemUserBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding, onUserClicked)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    companion object {
        private val DiffCallback = object : DiffUtil.ItemCallback<User>() {
            override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
                return oldItem.id == newItem.id
            }

            override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
                return oldItem == newItem
            }
        }
    }
}
