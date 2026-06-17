package com.la21.iptv.data

data class Channel(
    val name: String,
    val group: String,
    val logoUrl: String?,
    val streamUrl: String,
)
