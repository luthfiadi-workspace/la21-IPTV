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
             "sa", "eg", "my", "pk", "tr", "es", "it", "br",
             "cz", "nl", "ch", "at", "be", "pt", "pl", "ca", "mx", "cn", "jp", "au", "za"]

# Official free-to-air World Cup 2026 broadcasters per country.
# Verified against the actual iptv-org stream lists: many flagship broadcasters
# (BBC iPlayer feeds, ITV, ARD, ZDF, RT, CCTV, MBC, SBS Korea, VRT TV) are either
# absent from the free public dataset or marked [Geo-blocked] (only playable from
# their home country), so only channels that are genuinely free and unrestricted
# are included here. Exact name match, case-insensitive.
WORLD_CUP_2026_BROADCASTERS = {
    "uk": ["BBC One", "BBC Two"],
    "cz": ["ČT Sport"],
    "fr": ["M6 SD"],
    "it": ["Rai Sport HD", "Rai Sport 2"],
    "es": ["La 1 ("],
    "pt": ["RTP 1"],
    "pl": ["TVP Sport"],
    "ca": ["TSN The Ocho"],
    "mx": ["Azteca Internacional"],
    "br": ["Rede Globo", "CazeTV"],
    "id": ["TVRI Nasional", "TVRI Sport"],
    "kr": ["KBS World"],
    "jp": ["NHK World-Japan"],
    "qa": ["Al Jazeera English"],
}

CATEGORY_PLAYLISTS = {
    "news.m3u": ({"news"}, "📰 News"),
    "muslim.m3u": ({"religious"}, "☪️ Muslim"),
    "stocks-trade.m3u": ({"business"}, "📈 Stocks & Trade"),
    "ai-edu.m3u": ({"education", "science"}, "🎓 Edukasi & Sains"),
    "world-cup.m3u": ({"sports"}, "🏆 World Cup / Sports"),
    "movies.m3u": ({"movies"}, "🎬 Movies"),
    "kids.m3u": ({"kids"}, "🧒 Kids"),
    "music.m3u": ({"music"}, "🎵 Music"),
    "documentary.m3u": ({"documentary"}, "🎥 Documentary"),
    "comedy.m3u": ({"comedy"}, "😂 Comedy"),
    "animation.m3u": ({"animation"}, "🎨 Animation"),
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

    # Curated free-to-air World Cup 2026 broadcasters (matched by channel name, not category)
    worldcup_2026 = []
    seen_wc = set()
    for cc, names in WORLD_CUP_2026_BROADCASTERS.items():
        for ch in country_channels.get(cc, []):
            name_m = re.search(r',(.+)$', ch["extinf"])
            chan_name = name_m.group(1) if name_m else ""
            if (any(n.lower() in chan_name.lower() for n in names)
                    and "[geo-blocked]" not in ch["extinf"].lower()
                    and ch["url"] not in seen_wc):
                seen_wc.add(ch["url"])
                worldcup_2026.append(dict(ch, extinf=set_group(ch["extinf"], "🏆 World Cup 2026 Broadcasters")))

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
            result = dedup(worldcup_2026 + result)
            note = ("Includes curated official free-to-air World Cup 2026 broadcasters "
                     "(BBC, ARD/ZDF, TF1, TVRI, KBS/MBC/SBS, FOX, etc.) plus general sports "
                     "channels. Paid broadcasters (beIN Sports, Zee Sports, SuperSport) are not "
                     "included since they require a subscription.")
        write_playlist(f"playlists/{filename}", result, note)
        all_groups.append(result)

    full = dedup([ch for group in all_groups for ch in group])
    write_playlist("playlists/full.m3u", full, "Full playlist — semua kategori")
    print(f"\n🎉 Selesai! Total: {len(full)} channels")


if __name__ == "__main__":
    main()
