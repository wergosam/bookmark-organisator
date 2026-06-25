# bookmark_organisator/file_handler.py
"""Laden und Speichern von Lesezeichen-Dateien und Sitzungen."""

import csv
import json
import html
import plistlib
import configparser
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

from .models import Bookmark, Folder
from .parsers import (
    parse_bookmark_html,
    flatten_chromium_json,
    parse_firefox_json,
    parse_opera_adr,
    parse_safari_plist,
    parse_ie_url
)
from .i18n import load_language


# ── Lesezeichen laden / speichern (bisher) ──────────────────────────────────

def load_bookmarks_from_file(path: Path) -> List[Bookmark]:
    """Lädt Lesezeichen aus einer Datei (JSON, HTML, CSV, Opera ADR, Safari plist, IE url)."""
    tr = load_language("de")

    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "children" in data and "type" in data:
            return parse_firefox_json(data)
        if isinstance(data, dict) and "roots" in data:
            return flatten_chromium_json(data)
        if isinstance(data, list):
            return [Bookmark.from_dict(item) for item in data]
        raise ValueError(tr.get("err_json", "Invalid JSON format"))
    elif suffix == ".html":
        return parse_bookmark_html(path)
    elif suffix == ".csv":
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [Bookmark.from_dict(row) for row in reader]
    elif suffix == ".adr":
        return parse_opera_adr(path)
    elif suffix == ".plist":
        return parse_safari_plist(path)
    elif suffix == ".url":
        return parse_ie_url(path)
    else:
        raise ValueError(tr.get("err_format", "Unsupported format"))


def save_bookmarks_to_file(
    bookmarks: List[Bookmark],
    path: Path,
    selected_filter: str = "JSON (*.json)"
) -> None:
    """Speichert Lesezeichen im angegebenen Format (JSON, CSV, HTML, ADR, URL)."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump([bm.to_dict() for bm in bookmarks], f, ensure_ascii=False, indent=2)
    elif suffix == ".csv":
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["path", "title", "url"])
            writer.writeheader()
            writer.writerows([bm.to_dict() for bm in bookmarks])
    elif suffix == ".html":
        root = Folder("")
        for bm in bookmarks:
            parts = [p.strip() for p in bm.path.split("/") if p.strip()]
            node = root
            for part in parts:
                node = node.find_or_create_subfolder(part)
            node.add_bookmark(bm)

        def render(node: Folder, indent: int = 0) -> str:
            pad = "    " * indent
            out = ""
            for bm in node.bookmarks:
                url = html.escape(bm.url, quote=True)
                title = html.escape(bm.title)
                out += f'{pad}<DT><A HREF="{url}">{title}</A>\n'
            for sub in node.subfolders:
                out += f'{pad}<DT><H3>{html.escape(sub.name)}</H3>\n{pad}<DL><p>\n'
                out += render(sub, indent + 1)
                out += f'{pad}</DL><p>\n'
            return out

        tr = load_language("de")
        html_content = (
            f'<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
            f'<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
            f'<TITLE>{html.escape(tr.get("html_title", "Bookmarks"))}</TITLE>\n'
            f'<H1>{html.escape(tr.get("html_h1", "Bookmarks"))}</H1>\n<DL><p>\n'
            f'{render(root)}</DL><p>\n'
        )
        path.write_text(html_content, encoding="utf-8")
    elif suffix == ".adr":
        with open(path, "w", encoding="utf-8") as f:
            for bm in bookmarks:
                f.write(f"#URL\n{bm.url}\n#TITLE\n{bm.title}\n\n")
    elif suffix == ".url":
        if bookmarks:
            with open(path, "w", encoding="utf-8") as f:
                f.write("[InternetShortcut]\n")
                f.write(f"URL={bookmarks[0].url}\n")
    else:
        with open(path.with_suffix(".json"), "w", encoding="utf-8") as f:
            json.dump([bm.to_dict() for bm in bookmarks], f, ensure_ascii=False, indent=2)


# ── Sitzungen (.bmo) speichern / laden ──────────────────────────────────────

def save_session_to_file(
    path: Path,
    left_items: List[Dict[str, str]],
    right_items: List[Dict[str, str]],
    left_label: str = "",
    right_label: str = ""
) -> None:
    """Speichert den aktuellen Zustand beider Seiten als .bmo-Datei."""
    data = {
        "version": 1,
        "left": {
            "items": left_items,
            "label": left_label
        },
        "right": {
            "items": right_items,
            "label": right_label
        }
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_session_from_file(path: Path) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], str, str]:
    """Lädt eine .bmo-Sitzungsdatei und gibt (left_items, right_items, left_label, right_label) zurück."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    version = data.get("version", 1)
    left = data.get("left", {})
    right = data.get("right", {})
    left_items = left.get("items", [])
    right_items = right.get("items", [])
    left_label = left.get("label", "")
    right_label = right.get("label", "")
    return left_items, right_items, left_label, right_label