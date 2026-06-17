package com.la21.iptv.data

/**
 * Minimal M3U/M3U8 parser for #EXTINF entries with tvg-logo and group-title attributes,
 * matching the format produced by scripts/update_playlists.py in this repo.
 */
object M3uParser {

    private val groupRegex = Regex("""group-title="([^"]*)"""")
    private val logoRegex = Regex("""tvg-logo="([^"]*)"""")
    private val nameRegex = Regex(""",(.+)$""")

    fun parse(text: String): List<Channel> {
        val lines = text.lines()
        val channels = mutableListOf<Channel>()
        var i = 0
        while (i < lines.size) {
            val line = lines[i].trim()
            if (line.startsWith("#EXTINF")) {
                val group = groupRegex.find(line)?.groupValues?.get(1) ?: "Lainnya"
                val logo = logoRegex.find(line)?.groupValues?.get(1)
                val name = nameRegex.find(line)?.groupValues?.get(1)?.trim() ?: "Unknown"

                var j = i + 1
                while (j < lines.size && !lines[j].trim().startsWith("http")) j++
                if (j < lines.size) {
                    channels += Channel(
                        name = name,
                        group = group,
                        logoUrl = logo?.takeIf { it.isNotBlank() },
                        streamUrl = lines[j].trim(),
                    )
                    i = j
                }
            }
            i++
        }
        return channels
    }
}
