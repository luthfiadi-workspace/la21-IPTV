"""
LA21-IPTV Auto Update Script
Fetch channel data from iptv-org (master branch, real working stream URLs)
and rebuild category playlists, with logos and curated rankings.
"""
import csv
import os
import re
import time
import urllib.request

UA = "LA21-IPTV/1.0"
STREAMS_URL = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/{}.m3u"
CHANNELS_CSV = "https://raw.githubusercontent.com/iptv-org/database/master/data/channels.csv"
LOGOS_CSV = "https://raw.githubusercontent.com/iptv-org/database/master/data/logos.csv"

# Countries fetched to build country playlists and category playlists
COUNTRIES = ["id", "kr", "ru", "us", "uk", "qa", "ae", "fr", "de", "in",
             "sa", "eg", "my", "pk", "tr", "es", "it", "br",
             "cz", "nl", "ch", "at", "be", "pt", "pl", "ca", "mx", "cn", "jp", "au", "za"]

# Full iptv-org category taxonomy mapped to our playlists.
# "general", "interactive", "shop" and "xxx" are intentionally excluded:
# general/interactive are mostly low-value junk/shopping channels, xxx is adult content.
CATEGORY_PLAYLISTS = {
    "news.m3u": ({"news"}, "📰 News"),
    "religious.m3u": ({"religious"}, "🛐 Religious"),
    "stocks-trade.m3u": ({"business"}, "📈 Business & Stocks"),
    "education.m3u": ({"education"}, "🎓 Edukasi"),
    "science.m3u": ({"science"}, "🔬 Science"),
    "sports.m3u": ({"sports"}, "⚽ Sports"),
    "movies.m3u": ({"movies"}, "🎬 Movies"),
    "kids.m3u": ({"kids"}, "🧒 Kids"),
    "music.m3u": ({"music"}, "🎵 Music"),
    "documentary.m3u": ({"documentary"}, "🎥 Documentary"),
    "comedy.m3u": ({"comedy"}, "😂 Comedy"),
    "animation.m3u": ({"animation"}, "🎨 Animation"),
    "culture.m3u": ({"culture"}, "🎭 Culture"),
    "entertainment.m3u": ({"entertainment"}, "🎉 Entertainment"),
    "family.m3u": ({"family"}, "👨‍👩‍👧 Family"),
    "lifestyle.m3u": ({"lifestyle"}, "🌿 Lifestyle"),
    "series.m3u": ({"series"}, "📺 Series & Drama"),
    "travel.m3u": ({"travel"}, "✈️ Travel"),
    "weather.m3u": ({"weather"}, "🌦️ Weather"),
    "outdoor.m3u": ({"outdoor"}, "🏔️ Outdoor"),
    "cooking.m3u": ({"cooking"}, "🍳 Cooking"),
    "classic.m3u": ({"classic"}, "📼 Classic TV"),
    "auto.m3u": ({"auto"}, "🚗 Auto"),
    "public.m3u": ({"public"}, "📡 Public Access"),
    "legislative.m3u": ({"legislative"}, "🏛️ Legislative"),
}

COUNTRY_PLAYLISTS = {
    "indonesia.m3u": ("id", "🇮🇩 Indonesia"),
    "korea.m3u": ("kr", "🇰🇷 Korea"),
    "russia.m3u": ("ru", "🇷🇺 Russia"),
}

# Official free-to-air World Cup 2026 broadcasters per country.
# Verified against the actual iptv-org stream lists: many flagship broadcasters
# (BBC iPlayer feeds, ITV, ARD, ZDF, RT, CCTV, MBC, SBS Korea, VRT TV) are either
# absent from the free public dataset or marked [Geo-blocked] (only playable from
# their home country), so only channels that are genuinely free and unrestricted
# are included here. This list is broadcasters ONLY — no general sports channels.
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

# Manual popularity ranking for Indonesian free-to-air channels (most-watched first).
# Anything not in this list keeps its original order, appended after ranked channels.
INDONESIA_RANK = [
    "RCTI", "SCTV", "Indosiar", "Trans TV", "Trans7", "ANTV", "MNCTV",
    "GTV", "Global TV", "tvOne", "TV One", "Metro TV", "Kompas TV", "NET",
    "iNews", "TVRI Nasional", "TVRI Sport", "TVRI", "BeritaSatu",
    "CNN Indonesia", "CNBC Indonesia", "Trans 7",
]

# Channels upstream mistags into education/science categories that are clearly
# something else by name (verified against general knowledge, not live browsing —
# this sandbox can only reach GitHub domains, so very obscure local channels
# cannot be fully fact-checked).
MISCATEGORIZED_EXCLUDE = {
    "AyenehTV.us",       # Bahá'í religious channel, not education
    "PayamJavanTV.us",   # Iranian diaspora political channel, not education
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


def set_logo(extinf, logo_url):
    if not logo_url:
        return extinf
    if "tvg-logo=" in extinf:
        return re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{logo_url}"', extinf)
    return extinf.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{logo_url}"', 1)


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


def channel_name(ch):
    m = re.search(r',(.+)$', ch["extinf"])
    return m.group(1) if m else ""


def rank_indonesia(channels):
    def rank_key(ch):
        name = channel_name(ch)
        for idx, keyword in enumerate(INDONESIA_RANK):
            if keyword.lower() in name.lower():
                return (0, idx)
        return (1, 0)
    indexed = list(enumerate(channels))
    indexed.sort(key=lambda pair: (rank_key(pair[1]), pair[0]))
    return [ch for _, ch in indexed]


def main():
    print("🚀 LA21-IPTV Auto Update")
    print("=" * 40)
    os.makedirs("playlists", exist_ok=True)

    print("📡 Fetching channel categories...")
    cat_of_id = {}
    csv_text = fetch(CHANNELS_CSV)
    for row in csv.DictReader(csv_text.splitlines()):
        cat_of_id[row["id"]] = set((row.get("categories") or "").split(";")) if row.get("categories") else set()

    print("📡 Fetching logos...")
    logo_of_id = {}
    logos_text = fetch(LOGOS_CSV)
    for row in csv.DictReader(logos_text.splitlines()):
        cid = row["channel"]
        if cid in logo_of_id:
            continue
        if row.get("feed"):
            continue
        if row.get("in_use", "").upper() != "TRUE":
            continue
        logo_of_id[cid] = row["url"]

    country_channels = {}
    for cc in COUNTRIES:
        print(f"📡 Fetching {cc} ...")
        text = fetch(STREAMS_URL.format(cc))
        chans = dedup(parse_m3u(text))
        for ch in chans:
            ch["extinf"] = set_logo(ch["extinf"], logo_of_id.get(ch["id"]))
        country_channels[cc] = chans
        print(f"  → {len(chans)} channels")

    all_groups = []

    for filename, (cc, label) in COUNTRY_PLAYLISTS.items():
        chans = [dict(ch, extinf=set_group(ch["extinf"], label)) for ch in country_channels.get(cc, [])]
        if filename == "indonesia.m3u":
            chans = rank_indonesia(chans)
        write_playlist(f"playlists/{filename}", chans)
        all_groups.append(chans)

    # Curated free-to-air World Cup 2026 broadcasters (matched by channel name, not category)
    worldcup_2026 = []
    seen_wc = set()
    for cc, names in WORLD_CUP_2026_BROADCASTERS.items():
        for ch in country_channels.get(cc, []):
            name = channel_name(ch)
            if (any(n.lower() in name.lower() for n in names)
                    and "[geo-blocked]" not in ch["extinf"].lower()
                    and ch["url"] not in seen_wc):
                seen_wc.add(ch["url"])
                worldcup_2026.append(dict(ch, extinf=set_group(ch["extinf"], "🏆 World Cup 2026")))
    write_playlist(
        "playlists/world-cup.m3u", worldcup_2026,
        "Curated official free-to-air World Cup 2026 broadcasters only (no general sports "
        "channels). Paid broadcasters (beIN Sports, Zee Sports, SuperSport) and broadcasters "
        "with no free public stream available (BBC iPlayer, ITV, ARD, ZDF, RT, CCTV, MBC/SBS "
        "Korea, VRT) are not included."
    )
    all_groups.append(worldcup_2026)

    for filename, (cats, label) in CATEGORY_PLAYLISTS.items():
        result = []
        seen = set()
        for cc in COUNTRIES:
            for ch in country_channels.get(cc, []):
                if (cat_of_id.get(ch["id"], set()) & cats and ch["url"] not in seen
                        and ch["id"] not in MISCATEGORIZED_EXCLUDE):
                    seen.add(ch["url"])
                    result.append(dict(ch, extinf=set_group(ch["extinf"], label)))
        write_playlist(f"playlists/{filename}", result)
        all_groups.append(result)

    full = dedup([ch for group in all_groups for ch in group])
    write_playlist("playlists/full.m3u", full, "Full playlist — semua kategori")
    print(f"\n🎉 Selesai! Total: {len(full)} channels")


if __name__ == "__main__":
    main()
