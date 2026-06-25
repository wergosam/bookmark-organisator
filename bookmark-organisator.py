import sys
import os
import sqlite3
import shutil
import json
import csv
import html
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, QFileDialog,
    QStatusBar, QMessageBox,
    QLineEdit, QAbstractItemView, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QDrag, QKeySequence, QShortcut

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

STYLE = f"""
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
"""


# ── Vergleichs-Baum mit Drag & Drop ───────────────────────────────────────────
class CmpTree(QTreeWidget):
    """QTreeWidget, dessen Lesezeichen und Ordner per Maus verschoben werden
    können – innerhalb einer Seite (oben ↔ unten) und zwischen den beiden
    Seiten (links ↔ rechts). Das eigentliche Verschieben übernimmt der
    Callback ``on_drop(source_tree, target_tree, items, target_item, indicator)``."""

    MIME = "application/x-qabstractitemmodeldatalist"

    def __init__(self, on_drop, parent=None):
        super().__init__(parent)
        self._on_drop = on_drop
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropOverwriteMode(False)

    def startDrag(self, supportedActions):
        # Eigener Drag-Start: KEIN automatisches Entfernen der Quelle –
        # das Verschieben erledigt vollständig dropEvent (per take/insert).
        indexes = self.selectedIndexes()
        if not indexes:
            return
        mime = self.model().mimeData(indexes)
        if mime is None:
            return
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.MoveAction)

    def dropEvent(self, event):
        source = event.source()
        if not isinstance(source, CmpTree):
            event.ignore()
            return
        target_item = self.itemAt(event.position().toPoint())
        indicator = self.dropIndicatorPosition()
        moved = self._on_drop(source, self, source.selectedItems(),
                              target_item, indicator)
        if moved:
            event.acceptProposedAction()
        else:
            event.ignore()


# ── Netscape-Bookmark-HTML-Parser ─────────────────────────────────────────────
class _BookmarkHTMLParser(HTMLParser):
    """Robuster Parser für das Netscape-Bookmark-Format (Browser-Export).

    Arbeitet ereignisbasiert statt zeilenweise und kommt damit auch mit mehreren
    Lesezeichen pro Zeile, über Zeilen umbrochenen Tags und beliebig tiefer
    Ordner­verschachtelung zurecht. Die Ordnerstruktur ergibt sich aus den
    ``<DL>``-Blöcken: Ein ``<H3>`` benennt den Ordner, dessen Inhalt im direkt
    folgenden ``<DL>`` steht. Zeichen-Entities (``&amp;`` …) werden von
    HTMLParser automatisch dekodiert (in Daten und Attributwerten)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bookmarks = []
        self._stack = []            # Ordnernamen je DL-Ebene (None = namenlos/Wurzel)
        self._pending_folder = None  # zuletzt gelesener H3-Name, wartet auf sein <DL>
        self._in_h3 = False
        self._h3_text = []
        self._in_a = False
        self._a_href = None
        self._a_text = []

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
                self.bookmarks.append({
                    "path":  " / ".join(f for f in self._stack if f),
                    "title": "".join(self._a_text).strip(),
                    "url":   self._a_href,
                })
            self._in_a, self._a_href = False, None

    def handle_data(self, data):
        if self._in_h3:
            self._h3_text.append(data)
        elif self._in_a:
            self._a_text.append(data)


# ── Hauptfenster ──────────────────────────────────────────────────────────────
class BookmarkViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bookmark-Organisator")
        self.setMinimumSize(1100, 720)
        self._fullscreen_mode = False
        self._edit_syncing = False
        # Geändert-Status pro Seite (für die Speichern-Abfrage beim Beenden)
        self._cmp_dirty = {"left": False, "right": False}
        self._cmp_base_label = {"left": "", "right": ""}
        # Undo/Redo-Verlauf: Liste von Zustands-Schnappschüssen, _hist_idx zeigt
        # auf den aktuell dargestellten Stand. _restoring unterdrückt das Aufzeichnen
        # neuer Schritte, während ein Schnappschuss wiederhergestellt wird.
        self._history = []
        self._hist_idx = -1
        self._restoring = False
        self._build_ui()
        self._history_reset()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.root_layout = QVBoxLayout(central)
        self.root_layout.setContentsMargins(20, 18, 20, 10)
        self.root_layout.setSpacing(14)

        # ── Header ────────────────────────────────────────────────────────────
        self.header_widget = QWidget()
        hdr = QHBoxLayout(self.header_widget)
        hdr.setContentsMargins(0, 0, 0, 0)
        left = QVBoxLayout()
        left.setSpacing(2)
        title = QLabel("🔖  Bookmark-Organisator")
        title.setObjectName("title")
        self.lbl_sub = QLabel("Lesezeichen aus Dateien oder Browsern vergleichen & zusammenführen")
        self.lbl_sub.setObjectName("subtitle")
        left.addWidget(title)
        left.addWidget(self.lbl_sub)
        hdr.addLayout(left)
        hdr.addStretch()
        self.root_layout.addWidget(self.header_widget)

        # ── Hauptbereich ──────────────────────────────────────────────────────
        self._build_vergleichen()

        self.setStatusBar(QStatusBar())

    # ── Vergleichen ───────────────────────────────────────────────────────────
    def _build_vergleichen(self):
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(12, 12, 12, 12)
        vl.setSpacing(8)

        # ── Datei-Toolbar ──────────────────────────────────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        self._cmp_lbl_left  = QLabel("")
        self._cmp_lbl_right = QLabel("")
        for lbl in (self._cmp_lbl_left, self._cmp_lbl_right):
            lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:12px;")
        btn_ol = QPushButton("Datei öffnen")
        btn_ol.setFixedHeight(34)
        btn_ol.clicked.connect(lambda: self._cmp_open_file("left"))
        btn_nl = QPushButton("Neu/Leer")
        btn_nl.setFixedHeight(34)
        btn_nl.setToolTip("Leere Datei anlegen – auf dieser Seite von Grund auf sammeln")
        btn_nl.clicked.connect(lambda: self._cmp_new_empty("left"))
        btn_bl = QPushButton("Aus Browser  ▾")
        btn_bl.setFixedHeight(34)
        btn_bl.clicked.connect(lambda: self._cmp_browser_menu("left", btn_bl))
        btn_or = QPushButton("Datei öffnen")
        btn_or.setFixedHeight(34)
        btn_or.clicked.connect(lambda: self._cmp_open_file("right"))
        btn_nr = QPushButton("Neu/Leer")
        btn_nr.setFixedHeight(34)
        btn_nr.setToolTip("Leere Datei anlegen – auf dieser Seite von Grund auf sammeln")
        btn_nr.clicked.connect(lambda: self._cmp_new_empty("right"))
        btn_br = QPushButton("Aus Browser  ▾")
        btn_br.setFixedHeight(34)
        btn_br.clicked.connect(lambda: self._cmp_browser_menu("right", btn_br))
        top_row.addWidget(btn_ol)
        top_row.addWidget(btn_nl)
        top_row.addWidget(btn_bl)
        top_row.addWidget(self._cmp_lbl_left,  stretch=1)
        top_row.addSpacing(52)
        top_row.addWidget(btn_or)
        top_row.addWidget(btn_nr)
        top_row.addWidget(btn_br)
        top_row.addWidget(self._cmp_lbl_right, stretch=1)
        vl.addLayout(top_row)

        # ── Haupt-Splitter (links | mitte | rechts) ────────────────────────────
        outer = QHBoxLayout()
        outer.setSpacing(0)

        self._cmp_panel_left  = self._make_cmp_panel("left")
        self._cmp_panel_right = self._make_cmp_panel("right")

        # ── Mitte-Buttons ──────────────────────────────────────────────────────
        mid = QWidget()
        mid.setFixedWidth(62)
        ml = QVBoxLayout(mid)
        ml.setContentsMargins(6, 0, 6, 0)
        ml.setSpacing(6)
        ml.addStretch()

        def mid_btn(label, tip, slot, name="btnMid", h=40):
            b = QPushButton(label)
            b.setToolTip(tip)
            b.setFixedSize(50, h)
            b.setObjectName(name)
            b.clicked.connect(slot)
            return b

        ml.addWidget(mid_btn("🗑", "Ausgewählte Einträge/Ordner auf beiden Seiten löschen",
                             self._cmp_delete_both))
        ml.addSpacing(10)
        self._btn_undo = mid_btn("↶", "Rückgängig (Strg+Z)", self._undo, "btnMid", 34)
        self._btn_undo.setEnabled(False)
        ml.addWidget(self._btn_undo)
        self._btn_redo = mid_btn("↷", "Wiederherstellen (Strg+Y)", self._redo, "btnMid", 34)
        self._btn_redo.setEnabled(False)
        ml.addWidget(self._btn_redo)
        ml.addStretch()

        QShortcut(QKeySequence.StandardKey.Undo, self, activated=self._undo)
        QShortcut(QKeySequence.StandardKey.Redo, self, activated=self._redo)
        QShortcut(QKeySequence("Ctrl+Y"), self, activated=self._redo)

        outer.addWidget(self._cmp_panel_left,  stretch=1)
        outer.addWidget(mid)
        outer.addWidget(self._cmp_panel_right, stretch=1)
        vl.addLayout(outer, stretch=1)

        # ── Unterleiste ────────────────────────────────────────────────────────
        bot = QHBoxLayout()
        bot.setSpacing(8)
        self._cmp_cnt_left  = QLabel("0 Einträge")
        self._cmp_cnt_right = QLabel("0 Einträge")
        for lbl in (self._cmp_cnt_left, self._cmp_cnt_right):
            lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:12px;")

        def bot_btn(label, slot, name="btnHtml"):
            b = QPushButton(label); b.setObjectName(name)
            b.setFixedHeight(34); b.clicked.connect(slot); return b

        bot.addWidget(self._cmp_cnt_left)
        bot.addWidget(bot_btn("💾  Links speichern",   lambda: self._cmp_save("left")))
        bot.addStretch()
        self.btn_fullscreen = QPushButton("⛶  Vollbild")
        self.btn_fullscreen.setFixedHeight(34)
        self.btn_fullscreen.clicked.connect(self._toggle_fullscreen)
        bot.addWidget(self.btn_fullscreen)
        bot.addStretch()
        bot.addWidget(self._cmp_cnt_right)
        bot.addWidget(bot_btn("💾  Rechts speichern",  lambda: self._cmp_save("right")))
        vl.addLayout(bot)

        self.root_layout.addWidget(w, stretch=1)

    # ── Panel (kombinierter Baum: Ordner + Lesezeichen) ───────────────────────
    def _make_cmp_panel(self, side):
        """Gibt ein QWidget zurück mit Suchleiste oben und einem kombinierten
        Baum (Ordner als aufklappbare Knoten, Lesezeichen als Blätter) darunter."""
        panel = QWidget()
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(4)

        # Suchleiste – ein gemeinsamer, gerahmter Container, damit der Rahmen
        # durchgehend ist (Lupe + Feld darin sind randlos/transparent).
        sw = QWidget()
        sw.setObjectName("searchBox")
        sw.setFixedHeight(30)
        sw.setStyleSheet(
            f"#searchBox {{ background:{SURFACE}; border:1px solid {BORDER}; "
            f"border-radius:8px; }}")
        swl = QHBoxLayout(sw); swl.setContentsMargins(8, 0, 6, 0); swl.setSpacing(4)
        lupe = QLabel("🔍")
        lupe.setStyleSheet(
            f"border:none; background:transparent; color:{SUBTEXT}; font-size:12px;")
        inp = QLineEdit()
        inp.setPlaceholderText("Suchen …")
        inp.setStyleSheet(
            f"QLineEdit {{ border:none; background:transparent; color:{TEXT}; "
            f"font-size:12px; padding:0; }}"
            f"QLineEdit:focus {{ border:none; }}")
        swl.addWidget(lupe); swl.addWidget(inp)

        # Kombinierter Baum (Ordner + einzelne Lesezeichen), per Drag & Drop
        # verschiebbar – links↔rechts und oben↔unten.
        tree = CmpTree(self._cmp_handle_drop)
        tree.setHeaderLabels(["Titel", "URL"])
        tree.setColumnWidth(0, 240)
        tree.setAlternatingRowColors(True)
        tree.setAnimated(True)
        tree.setToolTip("Tipp: Titel/URL per Doppelklick bearbeiten · Lesezeichen "
                        "oder Ordner mit der Maus ziehen – zwischen den Seiten oder "
                        "zum Umsortieren innerhalb einer Seite.")
        tree.setStyleSheet(
            f"QTreeWidget {{ border-radius: 8px; font-size: 12px; }}"
            f"QTreeWidget::item {{ padding: 3px 6px; }}"
            # Inline-Editor (Doppelklick): gerade Ecken, feine Linie, normale,
            # nicht abgeschnittene Schrift ohne zusätzlichen Innenabstand.
            f"QTreeWidget QLineEdit {{"
            f"  border: 1px solid {ACCENT};"
            f"  border-radius: 0px;"
            f"  margin: 0px;"
            f"  padding: 0px 2px;"
            f"  font-weight: normal;"
            f"  font-size: 12px;"
            f"  min-height: 0px;"
            f"  background: {SURFACE};"
            f"  color: {TEXT};"
            f"}}"
            f"QTreeWidget QLineEdit:focus {{"
            f"  border: 1px solid {ACCENT};"
            f"  border-radius: 0px;"
            f"}}"
        )
        tree.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.SelectedClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed)
        tree.itemChanged.connect(self._edit_item_changed)

        pl.addWidget(sw)
        pl.addWidget(tree, stretch=1)

        # Verknüpfungen speichern
        if side == "left":
            self._cmp_tree_left   = tree
            self._cmp_search_left = inp
            inp.textChanged.connect(lambda t: self._cmp_filter("left",  t))
        else:
            self._cmp_tree_right   = tree
            self._cmp_search_right = inp
            inp.textChanged.connect(lambda t: self._cmp_filter("right", t))

        return panel

    def _cmp_widgets(self, side):
        """Liefert (tree, count-label, datei-label, suchfeld) der gewählten Seite."""
        if side == "left":
            return (self._cmp_tree_left, self._cmp_cnt_left,
                    self._cmp_lbl_left, self._cmp_search_left)
        return (self._cmp_tree_right, self._cmp_cnt_right,
                self._cmp_lbl_right, self._cmp_search_right)

    def _cmp_side_of(self, tree):
        return "left" if tree is self._cmp_tree_left else "right"

    @staticmethod
    def _cmp_parent_and_index(tree, item):
        """Liefert (Eltern-Item, Index) – für oberste Ebene den unsichtbaren Wurzel-Item."""
        parent = item.parent() or tree.invisibleRootItem()
        return parent, parent.indexOfChild(item)

    def _cmp_drop_position(self, target_tree, target_item, indicator):
        """Ermittelt (Eltern-Item, Einfüge-Index) für einen Drop. Beim Verschieben
        innerhalb eines Baums erst nach dem Herauslösen der Quell-Items aufrufen,
        damit die Indizes stimmen."""
        Pos = QAbstractItemView.DropIndicatorPosition
        root_item = target_tree.invisibleRootItem()
        if target_item is None:
            return root_item, root_item.childCount()
        data = target_item.data(0, Qt.ItemDataRole.UserRole) or {}
        is_folder = data.get("type") == "folder"
        if indicator == Pos.OnItem and is_folder:
            return target_item, target_item.childCount()
        if indicator == Pos.AboveItem:
            return self._cmp_parent_and_index(target_tree, target_item)
        if indicator == Pos.BelowItem:
            parent, idx = self._cmp_parent_and_index(target_tree, target_item)
            return parent, idx + 1
        if indicator == Pos.OnItem:   # auf ein Lesezeichen → dahinter einfügen
            parent, idx = self._cmp_parent_and_index(target_tree, target_item)
            return parent, idx + 1
        return root_item, root_item.childCount()   # OnViewport

    def _cmp_clone_item(self, item):
        """Erzeugt eine eigenständige Kopie eines Item-Teilbaums (Ordner + Blätter)
        inklusive Daten, Formatierung und Editier-Flag – für das Kopieren per Drag."""
        d = dict(item.data(0, Qt.ItemDataRole.UserRole) or {})
        clone = QTreeWidgetItem([item.text(0), item.text(1)])
        clone.setData(0, Qt.ItemDataRole.UserRole, d)
        if d.get("type") == "folder":
            clone.setForeground(0, QColor(FOLDER_C))
            fnt = clone.font(0); fnt.setBold(True); clone.setFont(0, fnt)
        else:
            clone.setForeground(0, QColor(TEXT))
            clone.setForeground(1, QColor(SUBTEXT))
            clone.setToolTip(1, item.text(1))
            clone.setFlags(clone.flags() | Qt.ItemFlag.ItemIsEditable)
        for i in range(item.childCount()):
            clone.addChild(self._cmp_clone_item(item.child(i)))
        return clone

    def _cmp_top_level_roots(self, items):
        """Behält nur die „obersten" gezogenen Items – Items, deren Vorfahr
        ebenfalls gezogen wird, kommen mit ihrem Ordner automatisch mit."""
        dragged_ids = set(id(it) for it in items)
        roots = []
        for it in items:
            anc, nested = it.parent(), False
            while anc is not None:
                if id(anc) in dragged_ids:
                    nested = True
                    break
                anc = anc.parent()
            if not nested:
                roots.append(it)
        return roots

    def _tree_move_items(self, source, target_tree, items, target_item, indicator):
        """Kernlogik: Verschiebt die gezogenen Items (Lesezeichen und/oder Ordner
        – inkl. ihrer Unterelemente) an die Drop-Position. Funktioniert innerhalb
        eines Baums (umsortieren) und zwischen zwei Bäumen. Gibt True bei Erfolg.
        Aktualisiert KEINE Zähler – das übernimmt der jeweilige Aufrufer."""
        if not items:
            return False

        dragged_ids = set(id(it) for it in items)
        roots = self._cmp_top_level_roots(items)
        if not roots:
            return False

        # Nicht in sich selbst / einen gezogenen Ordner hinein ablegen.
        anc = target_item
        while anc is not None:
            if id(anc) in dragged_ids:
                self.statusBar().showMessage(
                    "Ein Ordner kann nicht in sich selbst verschoben werden.", 3000)
                return False
            anc = anc.parent()

        # Quell-Items aus ihren bisherigen Bäumen herauslösen.
        def detach(it):
            parent = it.parent()
            if parent is None:   # oberste Ebene – gehört immer zum Quellbaum
                return source.takeTopLevelItem(source.indexOfTopLevelItem(it))
            return parent.takeChild(parent.indexOfChild(it))

        detached = [detach(it) for it in roots]

        # Zielposition bestimmen (nach dem Herauslösen, damit Indizes stimmen).
        parent, index = self._cmp_drop_position(target_tree, target_item, indicator)
        root_item = target_tree.invisibleRootItem()

        for offset, it in enumerate(detached):
            parent.insertChild(index + offset, it)
        if parent is not root_item:
            parent.setExpanded(True)
        for it in detached:
            it.setSelected(True)
        return True

    def _tree_copy_items(self, source, target_tree, items, target_item, indicator):
        """Kopiert die gezogenen Items (Lesezeichen und/oder Ordner inkl. Inhalt)
        an die Drop-Position im Zielbaum. Die Quelle bleibt unverändert erhalten.
        Gibt True bei Erfolg. Aktualisiert KEINE Zähler – das erledigt der Aufrufer."""
        if not items:
            return False
        roots = self._cmp_top_level_roots(items)
        if not roots:
            return False

        clones = [self._cmp_clone_item(it) for it in roots]
        root_item = target_tree.invisibleRootItem()

        # Beim Kopieren:
        #   • auf einen Ordner            → hinein (ans Ende)
        #   • auf ein Lesezeichen         → an die angezeigte Drop-Linie (über/unter)
        #   • ins Leere / oberste Ebene   → oberste Ebene
        data = (target_item.data(0, Qt.ItemDataRole.UserRole) or {}) if target_item else {}
        if target_item is not None and data.get("type") == "folder":
            parent, index = target_item, target_item.childCount()
        else:
            parent, index = self._cmp_drop_position(target_tree, target_item, indicator)

        for offset, it in enumerate(clones):
            parent.insertChild(index + offset, it)
        if parent is not root_item:
            parent.setExpanded(True)
        target_tree.clearSelection()
        for it in clones:
            it.setSelected(True)
        return True

    def _cmp_handle_drop(self, source, target_tree, items, target_item, indicator):
        """Drop-Handler der beiden Vergleichen-Bäume.

        Innerhalb einer Seite wird umsortiert (verschoben), zwischen den beiden
        Seiten wird nur kopiert – die Quelle bleibt dabei erhalten."""
        if source is target_tree:
            ok = self._tree_move_items(source, target_tree, items, target_item, indicator)
        else:
            ok = self._tree_copy_items(source, target_tree, items, target_item, indicator)
        if not ok:
            return False
        src_side, dst_side = self._cmp_side_of(source), self._cmp_side_of(target_tree)
        self._cmp_refresh(src_side)
        self._cmp_refresh(dst_side)
        self._cmp_set_dirty(src_side)
        self._cmp_set_dirty(dst_side)
        self._history_push()
        return True

    # ── Datei laden ───────────────────────────────────────────────────────────
    def _cmp_load_into(self, side, bookmarks, label):
        """Baut den kombinierten Baum einer Seite neu auf und aktualisiert Labels."""
        tree, cnt, lbl, search = self._cmp_widgets(side)
        self._cmp_build_combined_tree(tree, bookmarks)
        self._cmp_base_label[side] = label
        lbl.setText(label)
        cnt.setText(f"{len(bookmarks)} Einträge")
        search.clear()
        self._cmp_set_dirty(side, False)
        # Frisch geladener Stand wird zur neuen Verlaufs-Basis (Undo/Redo geleert).
        self._history_reset()

    def _cmp_set_dirty(self, side, dirty=True):
        """Merkt sich, ob eine Seite seit dem Laden/Speichern geändert wurde, und
        zeigt das mit einem «●» vor dem Datei-Label an."""
        self._cmp_dirty[side] = dirty
        _, _, lbl, _ = self._cmp_widgets(side)
        base = self._cmp_base_label.get(side, "")
        lbl.setText(("●  " + base) if dirty else base)

    def _cmp_new_empty(self, side):
        """Legt eine leere (neue) Datei auf der gewählten Seite an. Danach lassen
        sich per Drag & Drop oder den Kopier-Pfeilen Lesezeichen sammeln und
        anschließend über «Speichern» als neue Datei sichern."""
        tree, *_ = self._cmp_widgets(side)
        if self._cmp_tree_to_list(tree):
            if QMessageBox.question(
                    self, "Neue leere Datei",
                    "Die aktuelle Seite enthält Einträge. Wirklich leeren und "
                    "eine neue, leere Datei anlegen?") != QMessageBox.StandardButton.Yes:
                return
        self._cmp_load_into(side, [], "📄  (neue Datei)")
        self.statusBar().showMessage(
            "✓  Leere Datei angelegt – Lesezeichen hierher ziehen oder kopieren", 4000)

    def _cmp_open_file(self, side):
        path, _ = QFileDialog.getOpenFileName(
            self, "Lesezeichen-Datei öffnen", str(Path.home()),
            "Lesezeichen (*.html *.json *.csv);;Alle Dateien (*)")
        if not path:
            return
        try:
            bookmarks = self._cmp_load_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Datei konnte nicht geladen werden:\n{e}")
            return
        short = Path(path).name
        self._cmp_load_into(side, bookmarks, short)
        self.statusBar().showMessage(
            f"✓  {len(bookmarks)} Lesezeichen aus «{short}» geladen", 4000)

    # ── Aus Browser laden ───────────────────────────────────────────────────────
    def _cmp_browser_menu(self, side, button):
        """Dropdown mit allen installierten Browsern, deren Lesezeichen gefunden
        wurden. Die Auswahl lädt sie direkt in die jeweilige Vergleichsseite."""
        browsers = self._detect_browsers()
        menu = QMenu(self)
        menu.setStyleSheet(f"""
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
        """)
        acts = {}
        if not browsers:
            a = menu.addAction("Kein Browser mit Lesezeichen gefunden")
            a.setEnabled(False)
        else:
            for label, kind, src in browsers:
                a = menu.addAction(f"🌐  {label}")
                acts[a] = (label, kind, src)
        pos = button.mapToGlobal(button.rect().bottomLeft())
        chosen = menu.exec(pos)
        if chosen in acts:
            label, kind, src = acts[chosen]
            self._cmp_open_browser(side, label, kind, src)

    def _cmp_open_browser(self, side, label, kind, src):
        try:
            bookmarks = self._load_browser_bookmarks(kind, src)
        except Exception as e:
            QMessageBox.critical(
                self, "Fehler",
                f"Lesezeichen aus {label} konnten nicht geladen werden:\n{e}")
            return
        if not bookmarks:
            self.statusBar().showMessage(
                f"Keine Lesezeichen in {label} gefunden.", 4000)
            return
        self._cmp_load_into(side, bookmarks, f"🌐  {label}")
        self.statusBar().showMessage(
            f"✓  {len(bookmarks)} Lesezeichen aus {label} geladen", 4000)

    def _detect_browsers(self):
        """Sucht installierte Browser anhand bekannter Profilpfade und gibt eine
        Liste (Anzeigename, Typ, Lesezeichen-Datei) zurück. Bei mehreren Profilen
        wird das mit der größten Lesezeichen-Datei gewählt."""
        home = Path.home()
        found = []

        # Firefox-artige Browser (places.sqlite)
        firefox_bases = [
            ("Firefox",            home / ".mozilla/firefox"),
            ("Firefox (Flatpak)",  home / ".var/app/org.mozilla.firefox/.mozilla/firefox"),
            ("Firefox (Snap)",     home / "snap/firefox/common/.mozilla/firefox"),
            ("LibreWolf",          home / ".librewolf"),
            ("LibreWolf (Flatpak)", home / ".var/app/io.gitlab.librewolf-community/.librewolf"),
            ("Zen Browser",        home / ".zen"),
            ("Zen Browser (Flatpak)", home / ".var/app/app.zen_browser.zen/.zen"),
            ("Tor Browser",        home / ".local/share/torbrowser"),
            ("Tor Browser",        home / "tor-browser"),
            ("Tor Browser",        home / ".tor-browser"),
            ("Tor Browser (Flatpak)", home / ".var/app/com.github.micahflee.torbrowser_launcher/data/torbrowser"),
        ]
        for label, base in firefox_bases:
            if not base.exists():
                continue
            cands = [c for c in base.rglob("places.sqlite") if c.is_file()]
            if cands:
                src = max(cands, key=lambda p: p.stat().st_size)
                found.append((label, "firefox", src))

        # Chromium-artige Browser (JSON-Datei "Bookmarks")
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
            cands = [c for c in (list(base.glob("*/Bookmarks")) + list(base.glob("Bookmarks")))
                     if c.is_file()]
            if cands:
                src = max(cands, key=lambda p: p.stat().st_size)
                found.append((label, "chromium", src))

        # Falkon (profiles/<name>/bookmarks.json – Aufbau wie Chromium)
        falkon_bases = [
            ("Falkon",            home / ".config/falkon"),
            ("Falkon (Flatpak)",  home / ".var/app/org.kde.falkon/config/falkon"),
        ]
        for label, base in falkon_bases:
            if not base.exists():
                continue
            cands = [c for c in base.glob("profiles/*/bookmarks.json") if c.is_file()]
            if cands:
                src = max(cands, key=lambda p: p.stat().st_size)
                found.append((label, "chromium", src))

        # Dubletten entfernen (gleiche Datei über mehrere Pfade gefunden)
        seen, unique = set(), []
        for label, kind, src in found:
            key = str(src.resolve())
            if key in seen:
                continue
            seen.add(key)
            unique.append((label, kind, src))
        return unique

    def _load_browser_bookmarks(self, kind, src):
        if kind == "firefox":
            return self._load_firefox_bookmarks(src)
        return self._load_chromium_bookmarks(src)

    def _load_firefox_bookmarks(self, places_path):
        """Liest Lesezeichen direkt aus einer Firefox-places.sqlite (über eine
        Kopie, da die Datei bei laufendem Browser gesperrt sein kann)."""
        fd, tmp_name = tempfile.mkstemp(prefix="places_cmp_", suffix=".sqlite")
        os.close(fd)
        tmp = Path(tmp_name)
        shutil.copy2(places_path, tmp)
        conn = sqlite3.connect(tmp)
        cur = conn.cursor()
        roots = {2: "Lesezeichen-Menü", 3: "Lesezeichen-Symbolleiste",
                 5: "Nicht abgelegt", 6: "Mobil"}
        result = []

        def walk(parent_id, parts):
            cur.execute(
                "SELECT b.title, p.url FROM moz_bookmarks b "
                "JOIN moz_places p ON b.fk = p.id "
                "WHERE b.type=1 AND b.parent=? AND p.url NOT LIKE 'place:%' "
                "ORDER BY b.position", (parent_id,))
            for title, url in cur.fetchall():
                result.append({"path": " / ".join(p for p in parts if p),
                               "title": title or url, "url": url})
            cur.execute(
                "SELECT id, title FROM moz_bookmarks "
                "WHERE type=2 AND parent=? ORDER BY position", (parent_id,))
            for fid, ftitle in cur.fetchall():
                walk(fid, parts + [ftitle or "(kein Name)"])

        try:
            for rid, rname in roots.items():
                walk(rid, [rname])
        finally:
            conn.close()
            tmp.unlink(missing_ok=True)
        return result

    def _load_chromium_bookmarks(self, bookmarks_path):
        """Liest die JSON-Datei 'Bookmarks' eines Chromium-basierten Browsers."""
        with open(bookmarks_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = []
        label_map = {
            "bookmark_bar":  "Lesezeichen-Symbolleiste",
            "bookmark_menu": "Lesezeichen-Menü",
            "other":         "Weitere Lesezeichen",
            "synced":        "Mobil",
        }

        def walk(node, parts):
            if not isinstance(node, dict):
                return
            if node.get("type") == "url":
                result.append({"path": " / ".join(p for p in parts if p),
                               "title": node.get("name", "") or node.get("url", ""),
                               "url": node.get("url", "")})
            else:
                for child in node.get("children", []):
                    walk(child, parts + [node.get("name", "")])

        for key, node in (data.get("roots", {}) or {}).items():
            if isinstance(node, dict) and node.get("children"):
                top = label_map.get(key, node.get("name", "") or key)
                for child in node["children"]:
                    walk(child, [top])
        return result

    def _cmp_load_file(self, path):
        p = Path(path)
        if p.suffix.lower() == ".json":
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                # Verschachtelte Browser-Exporte (Chromium "Bookmarks" mit
                # "roots", Firefox-JSON-Backup mit "children") flach machen.
                flat = self._cmp_flatten_json(data)
                if flat:
                    return flat
            raise ValueError("JSON muss eine Liste von Lesezeichen-Objekten "
                             "oder ein Browser-Export sein.")
        elif p.suffix.lower() == ".html":
            return self._cmp_parse_html(p)
        elif p.suffix.lower() == ".csv":
            with open(p, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return list(reader)
        raise ValueError("Nicht unterstütztes Format.")

    def _cmp_flatten_json(self, data):
        """Macht einen verschachtelten Browser-JSON-Export flach zu einer Liste
        von {path, title, url}-Objekten. Erkennt das Chromium-Format
        ("roots" / type "url") und das Firefox-JSON-Backup ("children" /
        "uri")."""
        result = []
        label_map = {
            "bookmark_bar":  "Lesezeichen-Symbolleiste",
            "bookmark_menu": "Lesezeichen-Menü",
            "other":         "Weitere Lesezeichen",
            "synced":        "Mobil",
        }

        def walk(node, parts):
            if not isinstance(node, dict):
                return
            # Chromium: {"type": "url", "name", "url"} – Firefox: {"uri", "title"}
            url = node.get("url") or node.get("uri")
            is_leaf = node.get("type") == "url" or (
                url and node.get("type") != "text/x-moz-place-container")
            if url and is_leaf:
                result.append({"path": " / ".join(p for p in parts if p),
                               "title": node.get("name")
                                        or node.get("title", "") or url,
                               "url": url})
                return
            name = node.get("name") or node.get("title", "")
            for child in node.get("children", []):
                walk(child, parts + [name])

        if isinstance(data.get("roots"), dict):          # Chromium "Bookmarks"
            for key, node in data["roots"].items():
                if isinstance(node, dict) and node.get("children"):
                    top = label_map.get(key, node.get("name", "") or key)
                    for child in node["children"]:
                        walk(child, [top])
        elif data.get("children") is not None:           # Firefox-JSON-Backup
            for child in data["children"]:
                walk(child, [])
        else:                                            # Unbekannte Struktur
            walk(data, [])
        return result

    def _cmp_parse_html(self, path):
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        parser = _BookmarkHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.bookmarks

    # ── Kombinierten Baum aufbauen / auslesen ─────────────────────────────────
    def _cmp_build_combined_tree(self, tree, bookmarks, editable=True):
        """Baut aus der flachen Liste einen Baum: Ordner als Knoten,
        Lesezeichen als Blätter darunter. Ordner starten zugeklappt.
        Bei ``editable=True`` lassen sich Titel und URL der Lesezeichen direkt
        im Baum bearbeiten (Doppelklick)."""
        tree.blockSignals(True)   # itemChanged-Sync während des Aufbaus aus
        tree.clear()
        folder_items = {}   # pfad-key → QTreeWidgetItem

        def get_folder(path):
            parent = tree.invisibleRootItem()
            key = ""
            for part in [p.strip() for p in (path or "").split("/") if p.strip()]:
                key = (key + " / " + part) if key else part
                node = folder_items.get(key)
                if node is None:
                    node = QTreeWidgetItem(parent, [f"📁  {part}", ""])
                    node.setForeground(0, QColor(FOLDER_C))
                    fnt = node.font(0); fnt.setBold(True); node.setFont(0, fnt)
                    node.setData(0, Qt.ItemDataRole.UserRole,
                                 {"type": "folder", "name": part})
                    folder_items[key] = node
                parent = node
            return parent

        for bm in bookmarks:
            parent = get_folder(bm.get("path", "") or "")
            title  = bm.get("title", "") or ""
            url    = bm.get("url", "") or ""
            leaf = QTreeWidgetItem(parent, [title, url])
            leaf.setForeground(0, QColor(TEXT))
            leaf.setForeground(1, QColor(SUBTEXT))
            leaf.setData(0, Qt.ItemDataRole.UserRole,
                         {"type": "bookmark", "title": title, "url": url})
            leaf.setToolTip(1, url)
            if editable:
                leaf.setFlags(leaf.flags() | Qt.ItemFlag.ItemIsEditable)

        tree.collapseAll()   # Ordner beim Öffnen minimiert/zugeklappt
        tree.blockSignals(False)

    def _cmp_tree_to_list(self, tree):
        """Wandelt den kombinierten Baum zurück in eine flache Lesezeichen-Liste
        (Pfad aus der Ordnerhierarchie zusammengesetzt)."""
        result = []

        def walk(item, parts):
            for i in range(item.childCount()):
                child = item.child(i)
                d = child.data(0, Qt.ItemDataRole.UserRole) or {}
                if d.get("type") == "bookmark":
                    result.append({"path": " / ".join(parts),
                                   "title": d.get("title", ""),
                                   "url": d.get("url", "")})
                else:
                    walk(child, parts + [d.get("name", "")])

        walk(tree.invisibleRootItem(), [])
        return result

    def _cmp_refresh(self, side):
        """Aktualisiert den Eintrag-Zähler einer Seite anhand des Baums."""
        tree, cnt, _, _ = self._cmp_widgets(side)
        cnt.setText(f"{len(self._cmp_tree_to_list(tree))} Einträge")

    def _cmp_selected_leaves(self, tree):
        """Alle ausgewählten Lesezeichen-Blätter (inkl. derer unter ausgewählten
        Ordnern), ohne Duplikate – nur Titel + URL."""
        result, seen = [], set()

        def collect(item):
            d = item.data(0, Qt.ItemDataRole.UserRole) or {}
            if d.get("type") == "bookmark":
                if id(item) not in seen:
                    seen.add(id(item))
                    result.append({"title": d.get("title", ""), "url": d.get("url", "")})
            else:
                for i in range(item.childCount()):
                    collect(item.child(i))

        for it in tree.selectedItems():
            collect(it)
        return result

    # ── Suche / Filter ─────────────────────────────────────────────────────────
    def _cmp_filter(self, side, text):
        tree, *_ = self._cmp_widgets(side)
        text = text.strip().lower()

        def show_all(item):
            """Macht ein Element samt allen Nachfahren sichtbar."""
            item.setHidden(False)
            for i in range(item.childCount()):
                show_all(item.child(i))

        def visit(item):
            d = item.data(0, Qt.ItemDataRole.UserRole) or {}
            if d.get("type") == "bookmark":
                vis = (not text or text in item.text(0).lower()
                       or text in item.text(1).lower())
                item.setHidden(not vis)
                return vis
            # Ordner: trifft der Suchtext auf den Ordnernamen selbst?
            self_match = bool(text) and text in (d.get("name", "") or "").lower()
            if self_match:
                # Ganzen Ordnerinhalt zeigen und aufklappen
                show_all(item)
                item.setExpanded(True)
                return True
            any_vis = False
            for i in range(item.childCount()):
                if visit(item.child(i)):
                    any_vis = True
            vis = any_vis or not text
            item.setHidden(not vis)
            # Bei aktiver Suche Treffer aufklappen, sonst (leeres Feld) zuklappen
            item.setExpanded(bool(text) and vis)
            return vis

        root = tree.invisibleRootItem()
        for i in range(root.childCount()):
            visit(root.child(i))

    def _cmp_delete_both(self):
        """Löscht die ausgewählten Einträge/Ordner auf beiden Seiten. Seiten ohne
        Auswahl bleiben unangetastet. Der Schritt landet im Undo/Redo-Verlauf."""
        n = 0
        for side in ("left", "right"):
            n += self._cmp_delete(side)
        if not n:
            self.statusBar().showMessage(
                "Bitte zuerst Einträge oder Ordner auswählen.", 3000)
            return
        self._history_push()
        self.statusBar().showMessage(
            f"🗑  {n} Element(e) gelöscht  ·  «↶» macht es rückgängig", 4000)

    def _cmp_delete(self, side):
        """Entfernt die auf einer Seite ausgewählten Einträge/Ordner direkt aus dem
        Baum (ohne Neuaufbau – offene Ordner bleiben offen). Gibt die Anzahl der
        entfernten obersten Elemente zurück (0, wenn nichts ausgewählt war)."""
        tree, *_ = self._cmp_widgets(side)
        roots = self._cmp_top_level_roots(tree.selectedItems())
        if not roots:
            return 0
        for it in roots:
            parent = it.parent() or tree.invisibleRootItem()
            parent.takeChild(parent.indexOfChild(it))
        self._cmp_refresh(side)
        self._cmp_set_dirty(side)
        return len(roots)

    # ── Undo / Redo (Zustands-Schnappschüsse beider Seiten) ────────────────────
    def _cmp_expanded_paths(self, tree):
        """Pfad-Schlüssel aller aktuell aufgeklappten Ordner einer Seite."""
        paths = set()

        def walk(item, parts):
            for i in range(item.childCount()):
                child = item.child(i)
                d = child.data(0, Qt.ItemDataRole.UserRole) or {}
                if d.get("type") == "folder":
                    key = " / ".join(parts + [d.get("name", "")])
                    if child.isExpanded():
                        paths.add(key)
                    walk(child, parts + [d.get("name", "")])

        walk(tree.invisibleRootItem(), [])
        return paths

    def _cmp_apply_expanded(self, tree, paths):
        """Stellt den Aufklapp-Zustand der Ordner gemäß ``paths`` wieder her."""
        def walk(item, parts):
            for i in range(item.childCount()):
                child = item.child(i)
                d = child.data(0, Qt.ItemDataRole.UserRole) or {}
                if d.get("type") == "folder":
                    key = " / ".join(parts + [d.get("name", "")])
                    child.setExpanded(key in paths)
                    walk(child, parts + [d.get("name", "")])

        walk(tree.invisibleRootItem(), [])

    def _snapshot(self):
        """Vollständiger Zustand beider Seiten (Einträge, offene Ordner, Status)."""
        snap = {}
        for side in ("left", "right"):
            tree, *_ = self._cmp_widgets(side)
            snap[side] = {
                "items":    self._cmp_tree_to_list(tree),
                "expanded": self._cmp_expanded_paths(tree),
                "dirty":    self._cmp_dirty.get(side, False),
                "base":     self._cmp_base_label.get(side, ""),
            }
        return snap

    def _history_reset(self):
        """Verwirft den Verlauf und macht den aktuellen Stand zur neuen Basis."""
        self._history = [self._snapshot()]
        self._hist_idx = 0
        self._update_history_buttons()

    def _history_push(self):
        """Hängt den aktuellen Stand als neuen Verlaufsschritt an (eine evtl.
        vorhandene Redo-Zukunft wird dabei verworfen)."""
        if self._restoring:
            return
        del self._history[self._hist_idx + 1:]
        self._history.append(self._snapshot())
        self._hist_idx = len(self._history) - 1
        self._update_history_buttons()

    def _history_restore(self, snap):
        self._restoring = True
        try:
            for side in ("left", "right"):
                s = snap[side]
                tree, *_ = self._cmp_widgets(side)
                self._cmp_build_combined_tree(tree, s["items"])
                self._cmp_apply_expanded(tree, s["expanded"])
                self._cmp_base_label[side] = s["base"]
                self._cmp_refresh(side)
                self._cmp_set_dirty(side, s["dirty"])
        finally:
            self._restoring = False

    def _undo(self):
        if self._hist_idx <= 0:
            return
        self._hist_idx -= 1
        self._history_restore(self._history[self._hist_idx])
        self._update_history_buttons()
        self.statusBar().showMessage("↶  Rückgängig", 2000)

    def _redo(self):
        if self._hist_idx >= len(self._history) - 1:
            return
        self._hist_idx += 1
        self._history_restore(self._history[self._hist_idx])
        self._update_history_buttons()
        self.statusBar().showMessage("↷  Wiederhergestellt", 2000)

    def _update_history_buttons(self):
        self._btn_undo.setEnabled(self._hist_idx > 0)
        self._btn_redo.setEnabled(self._hist_idx < len(self._history) - 1)

    def _cmp_save(self, side):
        """Speichert die Seite als Datei. Gibt True bei erfolgreichem Speichern
        zurück, sonst False (leer oder Dialog abgebrochen)."""
        tree, *_ = self._cmp_widgets(side)
        data  = self._cmp_tree_to_list(tree)
        if not data:
            QMessageBox.warning(self, "Leer", "Keine Einträge zum Speichern.")
            return False
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path, selected = QFileDialog.getSaveFileName(
            self, "Speichern als",
            str(Path.home() / f"lesezeichen_{side}_{ts}.json"),
            "JSON (*.json);;CSV (*.csv);;HTML (*.html)")
        if not path:
            return False
        p = Path(path)
        # Fehlt eine (bekannte) Endung, automatisch die des gewählten Filters anhängen
        filter_ext = {"JSON (*.json)": ".json", "CSV (*.csv)": ".csv",
                      "HTML (*.html)": ".html"}
        if p.suffix.lower() not in (".json", ".csv", ".html"):
            p = p.with_suffix(filter_ext.get(selected, ".json"))
        if p.suffix.lower() == ".json":
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif p.suffix.lower() == ".csv":
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["path","title","url"])
                w.writeheader(); w.writerows(data)
        else:
            def get_or_create(node, key):
                if key not in node["_folders"]:
                    node["_folders"][key] = {"_bookmarks":[], "_folders":{}}
                return node["_folders"][key]
            root_node = {"_bookmarks":[], "_folders":{}}
            for bm in data:
                parts = [x.strip() for x in bm["path"].split("/") if x.strip()]
                node  = root_node
                for part in parts:
                    node = get_or_create(node, part)
                node["_bookmarks"].append(bm)
            def render(node, indent=0):
                pad = "    " * indent; out = ""
                for bm in node["_bookmarks"]:
                    url   = html.escape(bm["url"], quote=True)
                    title = html.escape(bm["title"])
                    out += f'{pad}<DT><A HREF="{url}">{title}</A>\n'
                for fname, child in node["_folders"].items():
                    out += f'{pad}<DT><H3>{html.escape(fname)}</H3>\n{pad}<DL><p>\n'
                    out += render(child, indent+1)
                    out += f'{pad}</DL><p>\n'
                return out
            html_out = (f'<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
                        f'<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
                        f'<TITLE>Bookmarks</TITLE>\n<H1>Lesezeichen-Menü</H1>\n<DL><p>\n'
                        f'{render(root_node)}</DL><p>\n')
            p.write_text(html_out, encoding="utf-8")
        # Gespeicherte Datei wird zur neuen Basis – Geändert-Markierung zurücksetzen
        self._cmp_base_label[side] = p.name
        self._cmp_set_dirty(side, False)
        self.statusBar().showMessage(f"✓  Gespeichert: {p}", 4000)
        return True

    # ── Vollbild umschalten ───────────────────────────────────────────────────
    def _toggle_fullscreen(self):
        if not self._fullscreen_mode:
            self._prev_size = self.size()
            self._prev_pos  = self.pos()
            self.header_widget.hide()
            self.showMaximized()
            self.btn_fullscreen.setText("✕  Vollbild beenden")
            self._fullscreen_mode = True
        else:
            self.header_widget.show()
            self.showNormal()
            self.resize(self._prev_size)
            self.move(self._prev_pos)
            self.btn_fullscreen.setText("⛶  Vollbild")
            self._fullscreen_mode = False

    def _edit_item_changed(self, item, column):
        """Hält das UserRole-Datenobjekt eines Lesezeichens mit dem (per
        Doppelklick) bearbeiteten Text synchron, damit Export & Co. die
        Änderungen übernehmen."""
        if self._edit_syncing:
            return
        d = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(d, dict) and d.get("type") == "bookmark":
            d["title"] = item.text(0)
            d["url"]   = item.text(1)
            self._edit_syncing = True
            item.setData(0, Qt.ItemDataRole.UserRole, d)
            item.setToolTip(1, item.text(1))
            self._edit_syncing = False
            tree = item.treeWidget()
            if tree is not None:
                self._cmp_set_dirty(self._cmp_side_of(tree))
            self._history_push()

    # ── Beenden mit Speichern-Abfrage ──────────────────────────────────────────
    def closeEvent(self, event):
        """Fragt vor dem Beenden für jede geänderte Seite, ob (und wohin) die
        Lesezeichen gespeichert werden sollen. Abbrechen verhindert das Beenden."""
        labels = {"left": "linke", "right": "rechte"}
        for side in ("left", "right"):
            if not self._cmp_dirty.get(side):
                continue
            if not self._cmp_tree_to_list(self._cmp_widgets(side)[0]):
                continue   # nichts (mehr) zu speichern

            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Question)
            box.setWindowTitle("Vor dem Beenden speichern?")
            box.setText(f"Die {labels[side]} Seite «{self._cmp_base_label.get(side, '')}» "
                        f"wurde geändert.\nÄnderungen speichern?")
            box.setStandardButtons(
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel)
            box.setDefaultButton(QMessageBox.StandardButton.Save)
            box.button(QMessageBox.StandardButton.Save).setText("Speichern …")
            box.button(QMessageBox.StandardButton.Discard).setText("Verwerfen")
            box.button(QMessageBox.StandardButton.Cancel).setText("Abbrechen")
            choice = box.exec()

            if choice == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            if choice == QMessageBox.StandardButton.Discard:
                continue
            # Speichern – wird der Datei-Dialog abgebrochen, bricht auch das
            # Beenden ab, damit nichts ungewollt verloren geht.
            if not self._cmp_save(side):
                event.ignore()
                return
        event.accept()


# ── Start ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    win = BookmarkViewer()
    win.show()
    sys.exit(app.exec())
