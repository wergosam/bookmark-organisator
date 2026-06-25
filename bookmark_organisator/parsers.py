# bookmark_organisator/parsers.py
"""Parser für verschiedene Lesezeichen-Formate."""

import json
import plistlib
import configparser
from html.parser import HTMLParser
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Bookmark


class BookmarkHTMLParser(HTMLParser):
    """Parser für Netscape-Bookmark-HTML-Dateien."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bookmarks: List[Bookmark] = []
        self._stack: List[str] = []
        self._pending_folder: Optional[str] = None
        self._in_h3 = False
        self._h3_text: List[str] = []
        self._in_a = False
        self._a_href: Optional[str] = None
        self._a_text: List[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "dl":
            self._stack.append(self._pending_folder)
            self._pending_folder = None
        elif tag == "h3":
            self._in_h3, self._h3_text = True, []
        elif tag == "a":
            self._a_href = dict((k.lower(), v) for k, v in attrs).get("href")
            self._in_a, self._a_text = True, []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "dl":
            if self._stack:
                self._stack.pop()
        elif tag == "h3":
            self._in_h3 = False
            self._pending_folder = "".join(self._h3_text).strip()
        elif tag == "a":
            if self._in_a and self._a_href:
                self.bookmarks.append(Bookmark(
                    title="".join(self._a_text).strip(),
                    url=self._a_href,
                    path=" / ".join(f for f in self._stack if f),
                ))
            self._in_a, self._a_href = False, None

    def handle_data(self, data):
        if self._in_h3:
            self._h3_text.append(data)
        elif self._in_a:
            self._a_text.append(data)


def parse_bookmark_html(path: Path) -> List[Bookmark]:
    """Parst eine Netscape-Bookmark-HTML-Datei und gibt eine Liste von Bookmark-Objekten zurück."""
    text = path.read_text(encoding="utf-8", errors="replace")
    parser = BookmarkHTMLParser()
    parser.feed(text)
    parser.close()
    return parser.bookmarks


def flatten_chromium_json(data: Dict[str, Any]) -> List[Bookmark]:
    """Flacht ein Chromium-Bookmarks-JSON zu einer Liste von Bookmark-Objekten ab."""
    from .i18n import load_language
    tr = load_language("de")

    label_map = {
        "bookmark_bar":  tr.get("cr_toolbar", "Bookmarks Bar"),
        "bookmark_menu": tr.get("cr_menu", "Bookmarks Menu"),
        "other":         tr.get("cr_other", "Other Bookmarks"),
        "synced":        tr.get("cr_mobile", "Mobile Bookmarks"),
    }
    result: List[Bookmark] = []

    def walk(node: Any, parts: List[str]) -> None:
        if not isinstance(node, dict):
            return
        if node.get("type") == "url":
            result.append(Bookmark(
                title=node.get("name", "") or node.get("url", ""),
                url=node.get("url", ""),
                path=" / ".join(p for p in parts if p),
            ))
        else:
            name = node.get("name", "")
            for child in node.get("children", []):
                walk(child, parts + [name])

    roots = data.get("roots", {})
    for key, node in roots.items():
        if isinstance(node, dict) and node.get("children"):
            top = label_map.get(key, node.get("name", "") or key)
            for child in node["children"]:
                walk(child, [top])
    return result


def parse_firefox_json(data: Dict[str, Any]) -> List[Bookmark]:
    """Parst Firefox-Bookmark-JSON (neues Export-Format)."""
    result = []

    def walk(node, path_parts):
        if not isinstance(node, dict):
            return
        typ = node.get("type")
        if typ == "text/x-moz-place":
            # Lesezeichen
            title = node.get("title", "")
            uri = node.get("uri", "")
            if uri:
                result.append(Bookmark(
                    title=title or uri,
                    url=uri,
                    path=" / ".join(path_parts)
                ))
        elif typ == "text/x-moz-place-container":
            # Ordner
            title = node.get("title", "")
            if "children" in node:
                for child in node["children"]:
                    walk(child, path_parts + [title] if title else path_parts)
        else:
            # Falls keine Typangabe, prüfen wir auf children
            if "children" in node:
                for child in node["children"]:
                    walk(child, path_parts)

    walk(data, [])
    return result


def parse_opera_adr(file_path: Path) -> List[Bookmark]:
    """Parst Opera .adr-Datei (altes Format)."""
    bookmarks = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    i = 0
    current = {}
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("#URL"):
            # nächste Zeile ist URL
            i += 1
            if i < len(lines):
                url = lines[i].strip()
                current["url"] = url
            # nächste Zeile könnte #TITLE sein
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("#"):
                i += 1
            # Titel könnte folgen
            if i < len(lines) and lines[i].strip().startswith("#TITLE"):
                i += 1
                if i < len(lines):
                    title = lines[i].strip()
                    current["title"] = title
                i += 1
            # Jetzt Eintrag hinzufügen
            if "url" in current:
                bookmarks.append(Bookmark(
                    title=current.get("title", current["url"]),
                    url=current["url"],
                    path=""
                ))
            current = {}
        else:
            # Versuche Schlüssel=Wert zu parsen
            if "=" in line:
                key, val = line.split("=", 1)
                if key.strip().upper() == "URL":
                    current["url"] = val.strip()
                elif key.strip().upper() == "TITLE":
                    current["title"] = val.strip()
            i += 1
    return bookmarks


def parse_safari_plist(file_path: Path) -> List[Bookmark]:
    """Parst Safari Bookmarks.plist."""
    with open(file_path, "rb") as f:
        plist = plistlib.load(f)

    bookmarks = []

    def walk(node, path_parts):
        if isinstance(node, dict):
            if "WebBookmarkType" in node:
                typ = node["WebBookmarkType"]
                if typ == "WebBookmarkTypeLeaf":
                    # Lesezeichen
                    title = node.get("WebBookmarkTitle", "")
                    url = node.get("WebBookmarkURL", "")
                    if url:
                        bookmarks.append(Bookmark(
                            title=title or url,
                            url=url,
                            path=" / ".join(path_parts)
                        ))
                elif typ == "WebBookmarkTypeList":
                    # Ordner
                    title = node.get("WebBookmarkTitle", "")
                    if "WebBookmarkChildren" in node:
                        for child in node["WebBookmarkChildren"]:
                            walk(child, path_parts + [title] if title else path_parts)
            else:
                # Durchsuche alle Werte
                for value in node.values():
                    walk(value, path_parts)
        elif isinstance(node, list):
            for item in node:
                walk(item, path_parts)

    walk(plist, [])
    return bookmarks


def parse_ie_url(file_path: Path) -> List[Bookmark]:
    """Parst Internet Explorer .url-Datei."""
    config = configparser.ConfigParser()
    config.read(file_path, encoding="utf-8")
    if "InternetShortcut" in config and "URL" in config["InternetShortcut"]:
        url = config["InternetShortcut"]["URL"]
        title = file_path.stem
        return [Bookmark(title=title, url=url, path="")]
    return []