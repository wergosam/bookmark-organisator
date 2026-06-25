# bookmark_organisator/models.py
"""Datenmodelle für Lesezeichen und Ordner."""

from typing import List, Dict, Any, Optional, Set, Tuple


class Bookmark:
    """Ein einzelnes Lesezeichen."""
    def __init__(self, title: str, url: str, path: str = ""):
        self.title = title
        self.url = url
        self.path = path

    def to_dict(self) -> Dict[str, str]:
        return {"title": self.title, "url": self.url, "path": self.path}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Bookmark":
        return cls(
            title=data.get("title", ""),
            url=data.get("url", ""),
            path=data.get("path", ""),
        )

    def __repr__(self) -> str:
        return f"Bookmark(title={self.title!r}, url={self.url!r}, path={self.path!r})"


class Folder:
    """Ein Ordner, der Lesezeichen und Unterordner enthält."""
    def __init__(self, name: str):
        self.name = name
        self.bookmarks: List[Bookmark] = []
        self.subfolders: List["Folder"] = []

    def add_bookmark(self, bookmark: Bookmark) -> None:
        self.bookmarks.append(bookmark)

    def add_folder(self, folder: "Folder") -> None:
        self.subfolders.append(folder)

    def find_or_create_subfolder(self, name: str) -> "Folder":
        for f in self.subfolders:
            if f.name == name:
                return f
        new = Folder(name)
        self.subfolders.append(new)
        return new

    def to_flat_list(self, prefix: str = "") -> List[Dict[str, str]]:
        result = []
        for bm in self.bookmarks:
            result.append({"path": prefix, "title": bm.title, "url": bm.url})
        for sub in self.subfolders:
            new_prefix = f"{prefix} / {sub.name}" if prefix else sub.name
            result.extend(sub.to_flat_list(new_prefix))
        return result

    def __repr__(self) -> str:
        return f"Folder(name={self.name!r}, bookmarks={len(self.bookmarks)}, subfolders={len(self.subfolders)})"


# ── Duplikat-Funktionen ──────────────────────────────────────────────────────

def find_duplicates(bookmarks: List[Bookmark]) -> List[List[Bookmark]]:
    """
    Findet Duplikate anhand der URL (Groß-/Kleinschreibung wird beachtet).
    Gibt eine Liste von Gruppen zurück, jede Gruppe enthält alle Bookmark-Objekte mit gleicher URL.
    """
    url_map: Dict[str, List[Bookmark]] = {}
    for bm in bookmarks:
        url_map.setdefault(bm.url, []).append(bm)
    return [group for group in url_map.values() if len(group) > 1]


def merge_duplicates(bookmarks: List[Bookmark]) -> List[Bookmark]:
    """
    Entfernt Duplikate: behält von jeder URL-Gruppe das erste Vorkommen.
    Die Reihenfolge der verbleibenden Elemente bleibt erhalten.
    """
    seen: Set[str] = set()
    result: List[Bookmark] = []
    for bm in bookmarks:
        if bm.url not in seen:
            seen.add(bm.url)
            result.append(bm)
    return result