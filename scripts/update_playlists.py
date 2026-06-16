"""
LA21-IPTV Auto Update Script
Fetch channel data from iptv-org (master branch, real working stream URLs)
and rebuild category playlists.
"""
import csv
import os
import re
import time
import urllib.request

UA = "LA21-IPTV/1.0"
STREAMS_URL = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/{}.m3u"
CHANNELS_CSV = "https://raw.githubusercontent.com/iptv-org/database/master/data/channels.csv"

# Countries fetched to build both country playlists and category playlists
COUNTRIES = ["id", "kr", "ru", "us", "uk", "qa", "ae", "fr", "de", "in",
             "sa", "eg", "my", "pk", "tr", "es", "it", "br"]

CATEGORY_PLAYLISTS = {
    "news.m3u": ({"news"}, "📰 News"),
    "muslim.m3u": ({"religious"}, "☪️ Muslim"),
    "stocks-trade.m3u": ({"business"}, "📈 Stocks & Trade"),
    "ai-edu.m3u": ({"education", "science"}, "🤖 AI & Edukasi"),
    "world-cup.m3u": ({"sports"}, "🏆 World Cup / Sports"),
}

COUNTRY_PLAYLISTS = {
    "indonesia.m3u": ("id", "🇮🇩 Indonesia"),
    "korea.m3u": ("kr", "🇰🇷 Korea"),
    "russia.m3u": ("ru", "🇷🇺 Russia"),
}


def fetch(url, retries=3):
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            print(f"  ⚠ retry {url}: {e}")
            time.sleep(2)
    return ""


def parse_m3u(text):
    channels = []
    lines = [l.rstrip("\n") for l in text.split("\n")]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            extinf = line
            m = re.search(r'tvg-id="([^"]*)"', extinf)
            cid = m.group(1).split("@")[0] if m else ""
            extras = []
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("http"):
                if lines[j].strip().startswith(("#EXTVLCOPT", "#EXTGRP")):
                    extras.append(lines[j].strip())
                j += 1
            if j < len(lines) and lines[j].strip().startswith("http"):
                channels.append({"id": cid, "extinf": extinf, "extras": extras, "url": lines[j].strip()})
                i = j + 1
                continue
        i += 1
    return channels


def set_group(extinf, group):
    if "group-title=" in extinf:
        return re.sub(r'group-title="[^"]*"', f'group-title="{group}"', extinf)
    return extinf.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{group}"', 1)


def write_playlist(path, channels, note=""):
    with open(path, "w", encoding="utf-8") as f:
        f.write('#EXTM3U x-tvg-url="https://epg.pw/xmltv/epg.xml"\n')
        if note:
            f.write(f"# {note}\n")
        f.write("\n")
        for ch in channels:
            f.write(ch["extinf"] + "\n")
            for e in ch["extras"]:
                f.write(e + "\n")
            f.write(ch["url"] + "\n\n")
    print(f"  ✅ {path} → {len(channels)} channels")


def dedup(channels):
    seen, out = set(), []
    for ch in channels:
        if ch["url"] not in seen:
            seen.add(ch["url"])
            out.append(ch)
    return out


def main():
    print("🚀 LA21-IPTV Auto Update")
    print("=" * 40)
    os.makedirs("playlists", exist_ok=True)

    print("📡 Fetching channel categories...")
    cat_of_id = {}
    csv_text = fetch(CHANNELS_CSV)
    for row in csv.DictReader(csv_text.splitlines()):
        cat_of_id[row["id"]] = set((row.get("categories") or "").split(";")) if row.get("categories") else set()

    country_channels = {}
    for cc in COUNTRIES:
        print(f"📡 Fetching {cc} ...")
        text = fetch(STREAMS_URL.format(cc))
        country_channels[cc] = dedup(parse_m3u(text))
        print(f"  → {len(country_channels[cc])} channels")

    all_groups = []

    for filename, (cc, label) in COUNTRY_PLAYLISTS.items():
        chans = [dict(ch, extinf=set_group(ch["extinf"], label)) for ch in country_channels.get(cc, [])]
        write_playlist(f"playlists/{filename}", chans)
        all_groups.append(chans)

    for filename, (cats, label) in CATEGORY_PLAYLISTS.items():
        result = []
        seen = set()
        for cc in COUNTRIES:
            for ch in country_channels.get(cc, []):
                if cat_of_id.get(ch["id"], set()) & cats and ch["url"] not in seen:
                    seen.add(ch["url"])
                    result.append(dict(ch, extinf=set_group(ch["extinf"], label)))
        note = ""
        if filename == "world-cup.m3u":
            note = ("General sports channels that commonly broadcast football/World Cup matches. "
                    "Exclusive World Cup rights are usually geo-restricted/paid; this is general "
                    "free-to-air sports coverage.")
        write_playlist(f"playlists/{filename}", result, note)
        all_groups.append(result)

    full = dedup([ch for group in all_groups for ch in group])
    write_playlist("playlists/full.m3u", full, "Full playlist — semua kategori")
    print(f"\n🎉 Selesai! Total: {len(full)} channels")


if __name__ == "__main__":
    main()
