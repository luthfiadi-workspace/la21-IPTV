package com.la21.iptv

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView

class PlayerActivity : ComponentActivity() {

    private var player: ExoPlayer? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val streamUrl = intent.getStringExtra(EXTRA_STREAM_URL) ?: return finish()

        val playerView = PlayerView(this).apply {
            useController = true
        }
        setContentView(playerView)

        val exoPlayer = ExoPlayer.Builder(this).build().also {
            playerView.player = it
            it.setMediaItem(MediaItem.fromUri(streamUrl))
            it.prepare()
            it.playWhenReady = true
        }
        player = exoPlayer
    }

    override fun onDestroy() {
        player?.release()
        player = null
        super.onDestroy()
    }

    companion object {
        const val EXTRA_STREAM_URL = "extra_stream_url"
        const val EXTRA_CHANNEL_NAME = "extra_channel_name"
    }
}
