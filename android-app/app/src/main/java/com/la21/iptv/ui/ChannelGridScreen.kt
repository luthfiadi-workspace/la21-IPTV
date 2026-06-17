package com.la21.iptv.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.tv.material3.Card
import androidx.tv.material3.Text
import coil.compose.AsyncImage
import com.la21.iptv.data.Channel

/**
 * TV-style channel browser: one horizontally-scrolling row per category
 * (group-title from the M3U), mirroring how TiviMate groups channels.
 * Uses androidx.tv:tv-material's Card for D-pad focus/click handling.
 */
@Composable
fun ChannelGridScreen(channels: List<Channel>, onChannelClick: (Channel) -> Unit) {
    val byGroup = channels.groupBy { it.group }

    LazyColumn(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        byGroup.forEach { (group, groupChannels) ->
            item { Text(text = group, modifier = Modifier.padding(vertical = 8.dp)) }
            item {
                LazyRow {
                    items(groupChannels) { channel ->
                        ChannelCard(channel = channel, onClick = { onChannelClick(channel) })
                    }
                }
            }
        }
    }
}

@Composable
private fun ChannelCard(channel: Channel, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        modifier = Modifier
            .padding(8.dp)
            .size(width = 140.dp, height = 110.dp),
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            AsyncImage(
                model = channel.logoUrl,
                contentDescription = channel.name,
                modifier = Modifier.fillMaxWidth().size(72.dp),
            )
            Text(text = channel.name, modifier = Modifier.padding(4.dp))
        }
    }
}
