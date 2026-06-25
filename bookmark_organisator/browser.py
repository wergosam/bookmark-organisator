# bookmark_organisator/browser.py
"""Browser-Erkennung und -Laden von Lesezeichen."""

import os
import sqlite3
import shutil
import tempfile
import json
from pathlib import Path
from typing import List, Tuple, Optional

from .models import Bookmark
from .parsers import flatten_chromium_json


def detect_browsers() -> List[Tuple[str, str, Path]]:
    """Erkennt installierte Browser und gibt eine Liste zurück:
    (Anzeigename, Typ, Pfad zur Lesezeichen-Datei)."""
    home = Path.home()
    found: List[Tuple[str, str, Path]] = []

    # Firefox-basierte Browser
    firefox_bases = [
        ("Firefox",               home / ".mozilla/firefox"),
        ("Firefox (Flatpak)",     home / ".var/app/org.mozilla.firefox/.mozilla/firefox"),
        ("Firefox (Snap)",        home / "snap/firefox/common/.mozilla/firefox"),
        ("LibreWolf",             home / ".librewolf"),
        ("LibreWolf (Flatpak)",   home / ".var/app/io.gitlab.librewolf-community/.librewolf"),
        ("Zen Browser",           home / ".zen"),
        ("Zen Browser (Flatpak)", home / ".var/app/app.zen_browser.zen/.zen"),
        ("Tor Browser",           home / ".local/share/torbrowser"),
        ("Tor Browser",           home / "tor-browser"),
        ("Tor Browser",           home / ".tor-browser"),
        ("Tor Browser (Flatpak)", home / ".var/app/com.github.micahflee.torbrowser_launcher/data/torbrowser"),
    ]
    for label, base in firefox_bases:
        if not base.exists():
            continue
        candidates = [c for c in base.rglob("places.sqlite") if c.is_file()]
        if candidates:
            src = max(candidates, key=lambda p: p.stat().st_size)
            found.append((label, "firefox", src))

    # Chromium-basierte Browser
    chromium_bases = [
        ("Google Chrome",            home / ".config/google-chrome"),
        ("Chromium",                 home / ".config/chromium"),
        ("Brave",                    home / ".config/BraveSoftware/Brave-Browser"),
        ("Microsoft Edge",           home / ".config/microsoft-edge"),
        ("Vivaldi",                  home / ".config/vivaldi"),
        ("Opera",                    home / ".config/opera"),
        ("Opera GX",                 home / ".config/opera-gx"),
        ("Google Chrome (Flatpak)",  home / ".var/app/com.google.Chrome/config/google-chrome"),
        ("Chromium (Flatpak)",       home / ".var/app/org.chromium.Chromium/config/chromium"),
        ("Brave (Flatpak)",          home / ".var/app/com.brave.Browser/config/BraveSoftware/Brave-Browser"),
        ("Microsoft Edge (Flatpak)", home / ".var/app/com.microsoft.Edge/config/microsoft-edge"),
        ("Vivaldi (Flatpak)",        home / ".var/app/com.vivaldi.Vivaldi/config/vivaldi"),
    ]
    for label, base in chromium_bases:
        if not base.exists():
            continue
        candidates = [c for c in (list(base.glob("*/Bookmarks")) + list(base.glob("Bookmarks")))
                      if c.is_file()]
        if candidates:
            src = max(candidates, key=lambda p: p.stat().st_size)
            found.append((label, "chromium", src))

    # Falkon
    falkon_bases = [
        ("Falkon",           home / ".config/falkon"),
        ("Falkon (Flatpak)", home / ".var/app/org.kde.falkon/config/falkon"),
    ]
    for label, base in falkon_bases:
        if not base.exists():
            continue
        candidates = [c for c in base.glob("profiles/*/bookmarks.json") if c.is_file()]
        if candidates:
            src = max(candidates, key=lambda p: p.stat().st_size)
            found.append((label, "chromium", src))

    # Duplikate entfernen
    seen, unique = set(), []
    for label, kind, src in found:
        key = str(src.resolve())
        if key not in seen:
            seen.add(key)
            unique.append((label, kind, src))
    return unique


def load_firefox_bookmarks(places_path: Path) -> List[Bookmark]:
    """Lädt Firefox-Lesezeichen aus einer places.sqlite-Datei."""
    from .i18n import load_language
    tr = load_language("de")  # Fallback; wird später durch GUI-Übersetzung ersetzt

    fd, tmp_name = tempfile.mkstemp(prefix="places_cmp_", suffix=".sqlite")
    os.close(fd)
    tmp = Path(tmp_name)
    shutil.copy2(places_path, tmp)

    conn = sqlite3.connect(tmp)
    cur = conn.cursor()

    roots = {
        2: tr.get("ff_menu", "Bookmarks Menu"),
        3: tr.get("ff_toolbar", "Bookmarks Toolbar"),
        5: tr.get("ff_unsorted", "Unsorted Bookmarks"),
        6: tr.get("ff_mobile", "Mobile Bookmarks"),
    }
    result: List[Bookmark] = []

    def walk(parent_id: int, parts: List[str]) -> None:
        cur.execute(
            "SELECT b.title, p.url FROM moz_bookmarks b "
            "JOIN moz_places p ON b.fk = p.id "
            "WHERE b.type=1 AND b.parent=? AND p.url NOT LIKE 'place:%' "
            "ORDER BY b.position", (parent_id,))
        for title, url in cur.fetchall():
            result.append(Bookmark(
                title=title or url,
                url=url,
                path=" / ".join(p for p in parts if p),
            ))
        cur.execute(
            "SELECT id, title FROM moz_bookmarks "
            "WHERE type=2 AND parent=? ORDER BY position", (parent_id,))
        for fid, ftitle in cur.fetchall():
            walk(fid, parts + [ftitle or tr.get("ff_no_name", "(no name)")])

    try:
        for rid, rname in roots.items():
            walk(rid, [rname])
    finally:
        conn.close()
        tmp.unlink(missing_ok=True)
    return result


def load_chromium_bookmarks(bookmarks_path: Path) -> List[Bookmark]:
    """Lädt Chromium-basierte Lesezeichen aus einer JSON-Datei."""
    with open(bookmarks_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return flatten_chromium_json(data)


def load_browser_bookmarks(kind: str, src: Path) -> List[Bookmark]:
    """Lädt Lesezeichen aus einem Browser (Firefox oder Chromium)."""
    if kind == "firefox":
        return load_firefox_bookmarks(src)
    return load_chromium_bookmarks(src)