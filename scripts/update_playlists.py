"""
LA21-IPTV Auto Update Script
Fetch dari iptv-org dan merge ke playlist yang sudah ada
"""
import requests
import os
from datetime import datetime

IPTV_ORG_SOURCES = {
    "indonesia": "https://iptv-org.github.io/iptv/countries/id.m3u",
    "korea": "https://iptv-org.github.io/iptv/countries/kr.m3u",
    "russia": "https://iptv-org.github.io/iptv/countries/ru.m3u",
    "news": "https://iptv-org.github.io/iptv/categories/news.m3u",
    "sports": "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "movies": "https://iptv-org.github.io/iptv/categories/movies.m3u",
    "kids": "https://iptv-org.github.io/iptv/categories/kids.m3u",
    "music": "https://iptv-org.github.io/iptv/categories/music.m3u",
    "documentary": "https://iptv-org.github.io/iptv/categories/documentary.m3u",
    "comedy": "https://iptv-org.github.io/iptv/categories/comedy.m3u",
    "business": "https://iptv-org.github.io/iptv/categories/business.m3u",
    "muslim": "https://iptv-org.github.io/iptv/categories/religious.m3u",
    "arabic": "https://iptv-org.github.io/iptv/languages/ara.m3u",
}

CATEGORY_LABELS = {
    "indonesia": "🇮🇩 Indonesia",
    "korea": "🇰🇷 Korea",
    "russia": "🇷🇺 Russia",
    "news": "📰 News",
    "sports": "⚽ Sports",
    "movies": "🎬 Movies",
    "kids": "🧒 Kids",
    "music": "🎵 Music",
    "documentary": "🎥 Documentary",
    "comedy": "😂 Comedy",
    "business": "📈 Stocks & Trade",
    "muslim": "☪️ Muslim",
    "arabic": "☪️ Muslim",
}

def fetch(url):
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "LA21-IPTV/1.0"})
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  ⚠ Gagal fetch {url}: {e}")
        return ""

def parse_m3u(text, override_group=None):
    """Parse M3U text, return list of (extinf_line, url_line)"""
    channels = []
    lines = text.strip().split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            extinf = line
            # Override group-title if needed
            if override_group:
                import re
                extinf = re.sub(r'group-title="[^"]*"', f'group-title="{override_group}"', extinf)
                if 'group-title=' not in extinf:
                    extinf = extinf.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{override_group}"')
            # Look for URL on next line
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("http"):
                j += 1
            if j < len(lines) and lines[j].strip().startswith("http"):
                channels.append((extinf, lines[j].strip()))
                i = j + 1
                continue
        i += 1
    return channels

def read_manual_playlist(filepath):
    """Read existing manual playlist"""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return parse_m3u(f.read())

def write_playlist(filepath, channels, header_comment=""):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f'#EXTM3U x-tvg-url="https://iptv-org.github.io/epg/guides/id/mola.tv.epg.xml"\n')
        f.write(f'# Updated: {ts}\n')
        if header_comment:
            f.write(f'# {header_comment}\n')
        f.write('\n')
        for extinf, url in channels:
            f.write(extinf + '\n')
            f.write(url + '\n')
    print(f"  ✅ {filepath} → {len(channels)} channels")

def main():
    print("🚀 LA21-IPTV Auto Update")
    print("=" * 40)

    os.makedirs("playlists", exist_ok=True)
    os.makedirs("scripts", exist_ok=True)

    all_channels = []
    seen_urls = set()

    # Category order for full.m3u
    cat_order = [
        "indonesia", "korea", "russia", "muslim", "arabic",
        "news", "business", "sports", "movies", "kids",
        "music", "documentary", "comedy"
    ]

    per_cat_channels = {}

    for cat in cat_order:
        url = IPTV_ORG_SOURCES.get(cat)
        if not url:
            continue
        print(f"\n📡 Fetching: {cat}")
        text = fetch(url)
        if not text:
            per_cat_channels[cat] = []
            continue

        label = CATEGORY_LABELS.get(cat, cat.title())
        channels = parse_m3u(text, override_group=label)
        unique = [(e, u) for e, u in channels if u not in seen_urls]
        for _, u in unique:
            seen_urls.add(u)

        per_cat_channels[cat] = unique
        print(f"  → {len(unique)} channels")

        # Write individual playlist (merge muslim + arabic)
        playlist_file = f"playlists/{cat}.m3u"
        if cat == "arabic":
            # Append arabic to muslim playlist
            existing = read_manual_playlist("playlists/muslim.m3u")
            existing_urls = {u for _, u in existing}
            new_arabic = [(e, u) for e, u in unique if u not in existing_urls]
            write_playlist("playlists/muslim.m3u", existing + new_arabic, "Muslim + Arabic channels")
        elif cat == "business":
            write_playlist("playlists/stocks-trade.m3u", unique, "Stocks & Trade channels")
        else:
            write_playlist(playlist_file, unique)

    # Merge all into full.m3u (manual entries first, then iptv-org)
    print("\n📦 Building full.m3u...")
    for cat in cat_order:
        chs = per_cat_channels.get(cat, [])
        for ch in chs:
            if ch[1] not in {u for _, u in all_channels}:
                all_channels.append(ch)

    write_playlist("playlists/full.m3u", all_channels, "Full playlist — semua kategori")
    print(f"\n🎉 Selesai! Total: {len(all_channels)} channels")

if __name__ == "__main__":
    main()
