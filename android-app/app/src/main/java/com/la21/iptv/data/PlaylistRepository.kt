package com.la21.iptv.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.URL

object PlaylistRepository {

    // Defaults to this repo's Full Playlist; swap for any la21-IPTV category URL.
    const val DEFAULT_PLAYLIST_URL =
        "https://raw.githubusercontent.com/luthfiadi-workspace/la21-IPTV/main/playlists/full.m3u"

    suspend fun fetchChannels(url: String = DEFAULT_PLAYLIST_URL): List<Channel> =
        withContext(Dispatchers.IO) {
            val connection = URL(url).openConnection() as HttpURLConnection
            connection.connectTimeout = 15_000
            connection.readTimeout = 15_000
            connection.inputStream.bufferedReader().use { reader ->
                M3uParser.parse(reader.readText())
            }
        }
}
