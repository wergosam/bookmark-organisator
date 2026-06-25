# bookmark_organisator/validator.py
"""Lesezeichen-Validierung – prüft URLs auf Erreichbarkeit."""

import threading
import concurrent.futures
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Tuple, Callable
from urllib.parse import urlparse

from .models import Bookmark


class BookmarkValidator:
    """Prüft Lesezeichen-URLs parallel und liefert Status-Codes."""

    def __init__(self, timeout: int = 10, max_workers: int = 10):
        self.timeout = timeout
        self.max_workers = max_workers
        self._results: Dict[str, int] = {}  # url -> status_code (0 bei Fehler)
        self._errors: Dict[str, str] = {}    # url -> Fehlermeldung
        self._lock = threading.Lock()
        self._progress = 0
        self._total = 0
        self._callback: Optional[Callable[[int, int], None]] = None

    def check_bookmarks(self, bookmarks: List[Bookmark],
                        progress_callback: Optional[Callable[[int, int], None]] = None) -> Dict[str, int]:
        """
        Prüft alle Lesezeichen parallel.
        progress_callback wird mit (fertig, gesamt) aufgerufen.
        Gibt ein Dict zurück: url -> status_code (0 bei Fehler).
        """
        self._results.clear()
        self._errors.clear()
        self._total = len(bookmarks)
        self._progress = 0
        self._callback = progress_callback

        # URLs eindeutig machen, aber wir prüfen jede einmal
        # Für die Anzeige brauchen wir pro Bookmark den Status, aber wir speichern pro URL
        unique_urls = list({bm.url for bm in bookmarks if bm.url})
        self._total = len(unique_urls)
        self._progress = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self._check_url, url): url for url in unique_urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    status = future.result()
                    with self._lock:
                        self._results[url] = status
                        self._progress += 1
                        if self._callback:
                            self._callback(self._progress, self._total)
                except Exception:
                    with self._lock:
                        self._results[url] = 0
                        self._progress += 1
                        if self._callback:
                            self._callback(self._progress, self._total)

        return self._results

    def _check_url(self, url: str) -> int:
        """Prüft eine einzelne URL und gibt den Status-Code zurück (0 bei Fehler)."""
        if not url or not url.startswith(('http://', 'https://')):
            return 0
        try:
            # HEAD-Request mit Timeout
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.getcode()
        except urllib.error.HTTPError as e:
            return e.code if hasattr(e, 'code') else 0
        except Exception:
            return 0

    def get_status(self, url: str) -> int:
        """Gibt den Status für eine URL zurück (0 wenn nicht geprüft oder Fehler)."""
        return self._results.get(url, 0)

    def is_valid(self, url: str) -> bool:
        """True, wenn Status 200-299 (oder 3xx?) – wir betrachten 200-399 als gültig."""
        status = self.get_status(url)
        return 200 <= status < 400

    def is_error(self, url: str) -> bool:
        """True, wenn Status >= 400 oder 0 (Fehler)."""
        status = self.get_status(url)
        return status == 0 or status >= 400