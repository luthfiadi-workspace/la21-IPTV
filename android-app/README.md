# LA21 IPTV — Android TV / Google TV App (Scaffold)

A minimal TiviMate-style player for Google TV / Android TV, built on Compose for TV
and Media3 ExoPlayer. Loads an M3U playlist (defaults to this repo's `full.m3u`),
groups channels by category (`group-title`), and plays the selected stream.

## What's included
- `MainActivity` — fetches the playlist and renders a category-grouped channel browser.
- `PlayerActivity` — ExoPlayer-based HLS player, launched on channel selection.
- `data/M3uParser.kt` — parses `#EXTINF` lines (`tvg-logo`, `group-title`, name, URL).
- `data/PlaylistRepository.kt` — fetches the playlist over HTTP; URL is swappable.

## What's NOT included (left for follow-up work)
- EPG (XMLTV) parsing/guide UI
- Multiple playlist management / settings screen
- Favorites, parental lock, recording, Chromecast
- Play Store listing assets / billing integration

## Build & run

Requires [Android Studio](https://developer.android.com/studio) (Ladybug or newer)
with the Android TV SDK components.

Easiest path: **open the `android-app` folder directly in Android Studio** — it
will detect the Gradle project, generate the `gradlew` wrapper script/jar on
first sync, and download dependencies automatically. (The wrapper binary isn't
checked into this repo since it requires network access to generate.)

Once synced, you can also build from the command line:
```bash
cd android-app
./gradlew assembleDebug
```

## Previewing on a TV screen from your laptop (no physical TV needed)

1. In Android Studio: **Tools → Device Manager → Create Device**.
2. Pick a TV form factor — category **TV**, e.g. "Television (1080p)" or
   "Google TV (1080p)". This gives you the real 10-foot TV UI, not a phone UI.
3. Launch the virtual device, then hit **Run ▶** on the `app` module — it installs
   and launches directly into the emulator window.
4. Navigate with your keyboard arrow keys + Enter to simulate the remote D-pad
   (this is exactly how Google TV remote navigation works).

## Testing on a real Google TV device instead

1. On the Google TV device: **Settings → System → About → Developer mode**
   (click build number repeatedly to enable), then **Developer options → Network debugging**.
2. Note the device's IP address (**Settings → Network & Internet**).
3. From your laptop, with both on the same Wi-Fi:
   ```bash
   adb connect <google-tv-ip>:5555
   ```
4. Run the app from Android Studio — it will install/launch directly on the TV.
