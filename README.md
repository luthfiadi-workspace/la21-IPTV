# 📡 LA21-IPTV

Koleksi playlist IPTV terorganisir oleh **Luthfiadi** — Indonesia, Korea, Russia, Muslim, News, Stocks & Trade, AI Edu, dan lebih banyak lagi.

🌐 **Preview Page:** https://luthfiadi-workspace.github.io/la21-IPTV/

---

## 📋 Daftar Playlist

| Playlist | URL |
|---|---|
| 🌐 **Full** (semua) | `https://raw.githubusercontent.com/luthfiadi-workspace/la21-IPTV/main/playlists/full.m3u` |
| 🇮🇩 **Indonesia** | `https://raw.githubusercontent.com/luthfiadi-workspace/la21-IPTV/main/playlists/indonesia.m3u` |
| ☪️ **Muslim** | `https://raw.githubusercontent.com/luthfiadi-workspace/la21-IPTV/main/playlists/muslim.m3u` |
| 🇰🇷 **Korea** | `https://raw.githubusercontent.com/luthfiadi-workspace/la21-IPTV/main/playlists/korea.m3u` |
| 🇷🇺 **Russia** | `https://raw.githubusercontent.com/luthfiadi-workspace/la21-IPTV/main/playlists/russia.m3u` |
| 📰 **News** | `https://raw.githubusercontent.com/luthfiadi-workspace/la21-IPTV/main/playlists/news.m3u` |
| 📈 **Stocks & Trade** | `https://raw.githubusercontent.com/luthfiadi-workspace/la21-IPTV/main/playlists/stocks-trade.m3u` |
| 🤖 **AI Edu** | `https://raw.githubusercontent.com/luthfiadi-workspace/la21-IPTV/main/playlists/ai-edu.m3u` |

---

## 📱 Cara Pakai di BrowseHere (Google TV)

1. Copy URL playlist dari tabel di atas
2. Buka **BrowseHere** → Add Playlist → Paste URL
3. Channel otomatis terkelompok per kategori

---

## 🔄 Auto Update

Playlist diperbarui otomatis setiap hari **pukul 08.00 WIB** via GitHub Actions dari sumber [iptv-org](https://github.com/iptv-org/iptv).

---

## 📂 Struktur Repo

```
la21-IPTV/
├── playlists/
│   ├── full.m3u           ← Semua kategori
│   ├── indonesia.m3u      ← Channel Indonesia
│   ├── muslim.m3u         ← Channel Muslim/Islami
│   ├── korea.m3u          ← Channel Korea
│   ├── russia.m3u         ← Channel Russia
│   ├── news.m3u           ← Berita Global
│   ├── stocks-trade.m3u   ← Bloomberg, CNBC, BFM
│   └── ai-edu.m3u         ← NASA, Discovery, Science
├── scripts/
│   └── update_playlists.py
├── .github/workflows/
│   └── update.yml
├── index.html             ← Preview page (GitHub Pages)
└── README.md
```

---

*Untuk penggunaan pribadi. Semua stream dari broadcaster publik resmi.*
