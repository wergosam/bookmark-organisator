# bookmark_organisator/constants.py
"""Farben, Styles und Versionsinformationen."""

VERSION = "1.0.5"

# ── Claude-Helltheme Palette ──────────────────────────────────────────────────
BG        = "#f7f4ef"
SURFACE   = "#ffffff"
BORDER    = "#e8e3db"
TEXT      = "#1a1713"
SUBTEXT   = "#6b6560"
ACCENT    = "#d97757"
ACCENT_DK = "#e75000"
ACCENT_LT = "#fdf1ec"
FOLDER_C  = "#8b6f47"
GREEN     = "#2d7d46"
RED       = "#c0392b"


def get_style() -> str:
    """Gibt den vollständigen Style-Sheet-String zurück."""
    return f"""
QMainWindow, QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: 'Noto Sans', 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}
QTreeWidget {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
    outline: none;
    alternate-background-color: #faf8f4;
}}
QTreeWidget::item {{
    padding: 5px 8px;
    border-radius: 6px;
    min-height: 22px;
}}
QTreeWidget::item:selected {{
    background-color: {ACCENT_LT};
    color: {ACCENT};
}}
QTreeWidget::item:hover:!selected {{
    background-color: #f0ece5;
}}
QTreeWidget QHeaderView::section {{
    background-color: {BG};
    color: {SUBTEXT};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 6px 10px;
    font-weight: 600;
    font-size: 12px;
}}
QPushButton {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 7px 16px;
    font-weight: 400;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: #f0ece5;
    border-color: #c9c0b5;
}}
QPushButton:pressed {{
    background-color: {BORDER};
}}
QPushButton#btnHtml {{ color: {ACCENT};  border: 1.5px solid {ACCENT}; }}
QPushButton#btnHtml:hover {{ background-color: {ACCENT_LT}; }}
QPushButton#btnGreen {{ background-color: {GREEN}; color: white; border: none; }}
QPushButton#btnGreen:hover {{ background-color: #256b3a; }}
QPushButton#btnRed {{ background-color: {RED}; color: white; border: none; }}
QPushButton#btnRed:hover {{ background-color: #a93226; }}
QPushButton#btnMid {{
    background-color: {SURFACE};
    color: {ACCENT_DK};
    border: 1px solid {BORDER};
    border-radius: 8px;
    font-size: 19px;
    font-weight: 700;
    padding: 0;
}}
QPushButton#btnMid:hover {{ background-color: {ACCENT_LT}; border-color: {ACCENT}; }}
QPushButton#btnMid:pressed {{ background-color: {BORDER}; }}
QPushButton:disabled {{ color: #b0a89e; border-color: {BORDER};
                        background-color: {SURFACE}; }}
QLineEdit {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    selection-background-color: {ACCENT_LT};
}}
QLineEdit:focus {{
    border: 1.5px solid {ACCENT};
}}
QLabel#title {{
    color: {TEXT};
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -0.3px;
}}
QLabel#subtitle {{ color: {SUBTEXT}; font-size: 12px; }}
QStatusBar {{
    background-color: {SURFACE};
    color: {SUBTEXT};
    border-top: 1px solid {BORDER};
    font-size: 12px;
    padding: 2px 8px;
}}
QScrollBar:vertical {{
    background: transparent; width: 8px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 4px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: #c9c0b5; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QFrame[frameShape="4"], QFrame[frameShape="5"] {{ color: {BORDER}; }}
QMenuBar {{
    background-color: {BG};
    color: {TEXT};
    border-bottom: 1px solid {BORDER};
    font-size: 13px;
    padding: 2px 4px;
}}
QMenuBar::item:selected {{
    background-color: {ACCENT_LT};
    color: {ACCENT};
    border-radius: 5px;
}}
QMenu {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 4px;
}}
QMenu::item {{
    padding: 7px 18px; border-radius: 5px;
    color: {TEXT}; font-size: 13px;
}}
QMenu::item:selected {{ background: {ACCENT_LT}; color: {ACCENT}; }}
QMenu::item:disabled {{ color: #b0a89e; }}
QMenu::indicator {{ width: 14px; height: 14px; margin-left: 4px; }}
"""

STYLE = get_style()
