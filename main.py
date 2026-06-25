#!/usr/bin/env python3
# main.py – Startpunkt für den Bookmark-Organisator

import sys
from pathlib import Path

# Füge das Verzeichnis, in dem diese main.py liegt, zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from bookmark_organisator.constants import VERSION, STYLE
from bookmark_organisator.i18n import AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE
from bookmark_organisator.widgets.main_window import BookmarkViewer


def main():
    settings = QSettings("computer-experte", "BookmarkOrganisator")
    lang_code = settings.value("language", DEFAULT_LANGUAGE)
    if lang_code not in AVAILABLE_LANGUAGES.values():
        lang_code = DEFAULT_LANGUAGE

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)

    win = BookmarkViewer(lang_code=lang_code)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()