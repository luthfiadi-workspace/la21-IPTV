package com.la21.iptv

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.lifecycleScope
import com.la21.iptv.data.Channel
import com.la21.iptv.data.PlaylistRepository
import com.la21.iptv.ui.ChannelGridScreen
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            var channels by remember { mutableStateOf<List<Channel>?>(null) }

            lifecycleScope.launch {
                if (channels == null) {
                    channels = runCatching { PlaylistRepository.fetchChannels() }.getOrDefault(emptyList())
                }
            }

            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                val loaded = channels
                if (loaded == null) {
                    CircularProgressIndicator()
                } else {
                    ChannelGridScreen(channels = loaded) { channel ->
                        startActivity(
                            Intent(this@MainActivity, PlayerActivity::class.java)
                                .putExtra(PlayerActivity.EXTRA_STREAM_URL, channel.streamUrl)
                                .putExtra(PlayerActivity.EXTRA_CHANNEL_NAME, channel.name)
                        )
                    }
                }
            }
        }
    }
}
