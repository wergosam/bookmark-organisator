# bookmark_organisator/widgets/main_window.py
"""BookmarkViewer – Hauptfenster der Anwendung."""

import shutil
import tempfile
import re
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import webbrowser

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, QFileDialog,
    QStatusBar, QMessageBox, QLineEdit, QAbstractItemView, QMenu,
    QDialog, QTextBrowser, QToolButton, QApplication, QProgressDialog
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QActionGroup, QColor, QKeySequence, QShortcut, QClipboard

from ..constants import VERSION, FOLDER_C, TEXT, SUBTEXT, ACCENT, SURFACE, BORDER, ACCENT_LT
from ..i18n import load_language, AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE
from ..models import Bookmark, find_duplicates, merge_duplicates
from ..browser import detect_browsers, load_browser_bookmarks
from ..file_handler import (
    load_bookmarks_from_file, save_bookmarks_to_file,
    save_session_to_file, load_session_from_file
)
from ..validator import BookmarkValidator
from .cmp_tree import CmpTree


class BookmarkViewer(QMainWindow):
    def __init__(self, lang_code: str = DEFAULT_LANGUAGE):
        super().__init__()
        self._lang_code = lang_code
        self._tr = load_language(lang_code)
        self.setMinimumSize(1300, 720)
        self.resize(1300, 750)
        self._fullscreen_mode = False
        self._edit_syncing = False
        self._cmp_dirty = {"left": False, "right": False}
        self._cmp_base_label = {"left": "", "right": ""}
        self._history = []
        self._hist_idx = -1
        self._restoring = False

        self._search_case_sensitive = False
        self._search_regex = False
        self._search_path = False
        self._validation_running = False

        self._build_ui()
        self._history_reset()
        self._setup_shortcuts()

        # Gespeicherte Fenstergröße laden
        s = QSettings("computer-experte", "BookmarkOrganisator")
        geometry = s.value("window/geometry")
        if geometry:
            self.restoreGeometry(geometry)

    # ── Übersetzungs-Helfer ───────────────────────────────────────────────────
    def _(self, key: str, **kwargs) -> str:
        text = self._tr.get(key, key)
        return text.format(**kwargs) if kwargs else text

    # ── Sprache wechseln ──────────────────────────────────────────────────────
    def _switch_language(self, code: str):
        if code == self._lang_code:
            return
        snap = self._snapshot()
        self._lang_code = code
        self._tr = load_language(code)
        s = QSettings("computer-experte", "BookmarkOrganisator")
        s.setValue("language", code)
        old_central = self.centralWidget()
        self._build_ui()
        if old_central:
            old_central.deleteLater()
        self._history_restore(snap)
        self._history_reset()

    # ── UI aufbauen ───────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setWindowTitle(f"{self._('window_title')}  v{VERSION}")
        central = QWidget()
        self.setCentralWidget(central)
        self.root_layout = QVBoxLayout(central)
        self.root_layout.setContentsMargins(20, 18, 20, 10)
        self.root_layout.setSpacing(14)

        self._build_menubar()

        self.header_widget = QWidget()
        hdr = QHBoxLayout(self.header_widget)
        hdr.setContentsMargins(0, 0, 0, 0)
        left = QVBoxLayout()
        left.setSpacing(2)
        title = QLabel(self._("app_title"))
        title.setObjectName("title")
        self.lbl_sub = QLabel(self._("app_subtitle"))
        self.lbl_sub.setObjectName("subtitle")
        left.addWidget(title)
        left.addWidget(self.lbl_sub)
        hdr.addLayout(left)
        hdr.addStretch()
        self.root_layout.addWidget(self.header_widget)

        self._build_vergleichen()
        self.setStatusBar(QStatusBar())

    def _build_menubar(self):
        mb = self.menuBar()
        mb.clear()

        # Sprachmenü
        lang_menu = mb.addMenu(self._("menu_language"))
        group = QActionGroup(self)
        group.setExclusive(True)
        for display_name, code in AVAILABLE_LANGUAGES.items():
            act = QAction(display_name, self, checkable=True)
            act.setChecked(code == self._lang_code)
            act.triggered.connect(lambda checked, c=code: self._switch_language(c))
            group.addAction(act)
            lang_menu.addAction(act)

        # ── NEU: Sitzungsmenü ────────────────────────────────────────────────
        session_menu = mb.addMenu(self._("menu_session"))

        save_session_act = QAction(self._("menu_session_save"), self)
        save_session_act.triggered.connect(self._save_session)
        session_menu.addAction(save_session_act)

        load_session_act = QAction(self._("menu_session_load"), self)
        load_session_act.triggered.connect(self._load_session)
        session_menu.addAction(load_session_act)

        # Ansichtsmenü
        view_menu = mb.addMenu(self._("menu_view"))
        save_geom_act = QAction(self._("menu_save_geometry"), self)
        save_geom_act.triggered.connect(self._save_geometry)
        view_menu.addAction(save_geom_act)
        reset_geom_act = QAction(self._("menu_reset_geometry"), self)
        reset_geom_act.triggered.connect(self._reset_geometry)
        view_menu.addAction(reset_geom_act)

        # Hilfe-Menü
        help_menu = mb.addMenu(self._("menu_help"))
        manual_act = QAction(self._("menu_help_manual"), self)
        manual_act.triggered.connect(self._show_manual)
        help_menu.addAction(manual_act)
        about_act = QAction(self._("menu_about"), self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _show_about(self):
        QMessageBox.about(
            self,
            self._("about_title"),
            self._("about_text", version=VERSION)
        )

    def _show_manual(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self._("manual_title"))
        dlg.resize(700, 550)
        layout = QVBoxLayout(dlg)
        browser = QTextBrowser()
        browser.setHtml(self._("manual_text"))
        browser.setOpenExternalLinks(False)
        layout.addWidget(browser)
        btn_close = QPushButton(self._("manual_close"))
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
        dlg.exec()

    # ── Tastenkürzel ──────────────────────────────────────────────────────────
    def _setup_shortcuts(self):
        # Bestehende Shortcuts
        QShortcut(QKeySequence("Ctrl+O"), self, activated=lambda: self._cmp_open_file("left"))
        QShortcut(QKeySequence("Ctrl+Shift+O"), self, activated=lambda: self._cmp_open_file("right"))
        QShortcut(QKeySequence("Ctrl+S"), self, activated=lambda: self._cmp_save("left"))
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, activated=lambda: self._cmp_save("right"))
        QShortcut(QKeySequence("Ctrl+N"), self, activated=lambda: self._cmp_new_empty("left"))
        QShortcut(QKeySequence("Ctrl+Shift+N"), self, activated=lambda: self._cmp_new_empty("right"))
        QShortcut(QKeySequence("Ctrl+B"), self, activated=lambda: self._cmp_browser_shortcut("left"))
        QShortcut(QKeySequence("Ctrl+Shift+B"), self, activated=lambda: self._cmp_browser_shortcut("right"))
        QShortcut(QKeySequence("Del"), self, activated=self._cmp_delete_both)
        QShortcut(QKeySequence("Delete"), self, activated=self._cmp_delete_both)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self._focus_search)
        QShortcut(QKeySequence("F11"), self, activated=self._toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Tab"), self, activated=self._switch_tree_focus)
        QShortcut(QKeySequence("Ctrl+C"), self, activated=self._copy_selected)
        QShortcut(QKeySequence("Ctrl+V"), self, activated=self._paste_from_clipboard)

    # ── Hilfsfunktionen für Kopieren/Einfügen ──────────────────────────────
    def _copy_selected(self):
        tree = self.focusWidget()
        if not isinstance(tree, CmpTree):
            return
        item = tree.currentItem()
        if item is None:
            return
        d = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if d.get("type") != "bookmark":
            return
        title = d.get("title", "")
        url = d.get("url", "")
        text = f"{title}\n{url}" if title else url
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.statusBar().showMessage(self._("status_copied"), 2000)

    def _paste_from_clipboard(self):
        tree = self.focusWidget()
        if not isinstance(tree, CmpTree):
            return
        side = self._cmp_side_of(tree)

        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if not text:
            self.statusBar().showMessage(self._("status_paste_empty"), 2000)
            return

        lines = text.splitlines()
        if len(lines) >= 2:
            title = lines[0].strip()
            url = lines[1].strip()
            if not url.startswith(('http://', 'https://')):
                if lines[0].startswith(('http://', 'https://')):
                    url = lines[0].strip()
                    title = lines[1].strip() if len(lines) > 1 else ""
                else:
                    for line in lines:
                        if line.strip().startswith(('http://', 'https://')):
                            url = line.strip()
                            break
        else:
            if text.startswith(('http://', 'https://')):
                url = text
                title = ""
            else:
                self.statusBar().showMessage(self._("status_paste_no_url"), 3000)
                return

        if not url.startswith(('http://', 'https://')):
            self.statusBar().showMessage(self._("status_paste_no_url"), 3000)
            return

        parent_item = tree.currentItem()
        if parent_item is not None:
            d = parent_item.data(0, Qt.ItemDataRole.UserRole) or {}
            if d.get("type") != "folder":
                parent_item = parent_item.parent() or tree.invisibleRootItem()
        else:
            parent_item = tree.invisibleRootItem()

        if not title:
            title = url
        bm = Bookmark(title=title, url=url, path="")
        leaf = QTreeWidgetItem(parent_item, [bm.title, bm.url, ""])
        leaf.setForeground(0, QColor(TEXT))
        leaf.setForeground(1, QColor(SUBTEXT))
        leaf.setData(0, Qt.ItemDataRole.UserRole,
                     {"type": "bookmark", "title": bm.title, "url": bm.url})
        leaf.setToolTip(1, bm.url)
        leaf.setFlags(leaf.flags() | Qt.ItemFlag.ItemIsEditable)

        parent_item.setExpanded(True)
        self._cmp_refresh(side)
        self._cmp_set_dirty(side)
        self._update_folder_counts(tree)
        self._history_push()
        self.statusBar().showMessage(self._("status_pasted"), 2000)

    # ── Sitzung speichern / laden ────────────────────────────────────────────
    def _save_session(self):
        """Speichert den aktuellen Zustand beider Seiten als .bmo-Datei."""
        left_items = self._cmp_tree_to_list(self._cmp_tree_left)
        right_items = self._cmp_tree_to_list(self._cmp_tree_right)

        path, _ = QFileDialog.getSaveFileName(
            self,
            self._("dlg_session_save_title"),
            str(Path.home() / "session.bmo"),
            self._("dlg_session_save_filter")
        )
        if not path:
            return
        p = Path(path)
        if p.suffix.lower() != ".bmo":
            p = p.with_suffix(".bmo")

        left_label = self._cmp_base_label.get("left", "")
        right_label = self._cmp_base_label.get("right", "")
        try:
            save_session_to_file(p, left_items, right_items, left_label, right_label)
            self.statusBar().showMessage(self._("status_session_saved", path=p), 4000)
        except Exception as e:
            QMessageBox.critical(self, self._("dlg_error_title"),
                                 self._("dlg_error_session_save", err=e))

    def _load_session(self):
        """Lädt eine .bmo-Sitzungsdatei und stellt beide Seiten wieder her."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._("dlg_session_load_title"),
            str(Path.home()),
            self._("dlg_session_load_filter")
        )
        if not path:
            return
        try:
            left_items, right_items, left_label, right_label = load_session_from_file(Path(path))
        except Exception as e:
            QMessageBox.critical(self, self._("dlg_error_title"),
                                 self._("dlg_error_session_load", err=e))
            return

        # Beide Seiten neu aufbauen
        self._cmp_load_into("left", [Bookmark.from_dict(item) for item in left_items], left_label)
        self._cmp_load_into("right", [Bookmark.from_dict(item) for item in right_items], right_label)
        self.statusBar().showMessage(self._("status_session_loaded", path=path), 4000)

    # ── Fenstergröße speichern / zurücksetzen ──────────────────────────────
    def _save_geometry(self):
        s = QSettings("computer-experte", "BookmarkOrganisator")
        s.setValue("window/geometry", self.saveGeometry())
        self.statusBar().showMessage(self._("status_geometry_saved"), 3000)

    def _reset_geometry(self):
        s = QSettings("computer-experte", "BookmarkOrganisator")
        s.remove("window/geometry")
        self.resize(1300, 750)
        self.move(100, 100)
        self.statusBar().showMessage(self._("status_geometry_reset"), 3000)

    # ── Tastenkürzel-Hilfsfunktionen ──────────────────────────────────────────
    def _cmp_browser_shortcut(self, side):
        browsers = detect_browsers()
        if browsers:
            label, kind, src = browsers[0]
            self._cmp_open_browser(side, label, kind, src)
        else:
            self.statusBar().showMessage(self._("browser_none"), 3000)

    def _focus_search(self):
        tree = self.focusWidget()
        if isinstance(tree, CmpTree):
            side = self._cmp_side_of(tree)
            _, _, _, search = self._cmp_widgets(side)
            search.setFocus()
            search.selectAll()
        else:
            self._cmp_search_left.setFocus()
            self._cmp_search_left.selectAll()

    def _switch_tree_focus(self):
        if self._cmp_tree_left.hasFocus():
            self._cmp_tree_right.setFocus()
        else:
            self._cmp_tree_left.setFocus()

    # ── Vergleichen (UI) ──────────────────────────────────────────────────────
    def _build_vergleichen(self):
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(12, 12, 12, 12)
        vl.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        self._cmp_lbl_left = QLabel("")
        self._cmp_lbl_right = QLabel("")
        for lbl in (self._cmp_lbl_left, self._cmp_lbl_right):
            lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:12px;")

        # Linke Buttons
        btn_ol = QPushButton(self._("btn_open_file"))
        btn_ol.setFixedHeight(34)
        btn_ol.setToolTip(self._("btn_open_file_tip"))
        btn_ol.clicked.connect(lambda: self._cmp_open_file("left"))

        btn_nl = QPushButton(self._("btn_new_empty"))
        btn_nl.setFixedHeight(34)
        btn_nl.setToolTip(self._("btn_new_empty_tip"))
        btn_nl.clicked.connect(lambda: self._cmp_new_empty("left"))

        btn_bl = QPushButton(self._("btn_from_browser"))
        btn_bl.setFixedHeight(34)
        btn_bl.setToolTip(self._("btn_from_browser_tip"))
        btn_bl.clicked.connect(lambda: self._cmp_browser_menu("left", btn_bl))

        # Rechte Buttons
        btn_or = QPushButton(self._("btn_open_file"))
        btn_or.setFixedHeight(34)
        btn_or.setToolTip(self._("btn_open_file_tip"))
        btn_or.clicked.connect(lambda: self._cmp_open_file("right"))

        btn_nr = QPushButton(self._("btn_new_empty"))
        btn_nr.setFixedHeight(34)
        btn_nr.setToolTip(self._("btn_new_empty_tip"))
        btn_nr.clicked.connect(lambda: self._cmp_new_empty("right"))

        btn_br = QPushButton(self._("btn_from_browser"))
        btn_br.setFixedHeight(34)
        btn_br.setToolTip(self._("btn_from_browser_tip"))
        btn_br.clicked.connect(lambda: self._cmp_browser_menu("right", btn_br))

        top_row.addWidget(btn_ol)
        top_row.addWidget(btn_nl)
        top_row.addWidget(btn_bl)
        top_row.addWidget(self._cmp_lbl_left, stretch=1)
        top_row.addSpacing(52)
        top_row.addWidget(btn_or)
        top_row.addWidget(btn_nr)
        top_row.addWidget(btn_br)
        top_row.addWidget(self._cmp_lbl_right, stretch=1)
        vl.addLayout(top_row)

        outer = QHBoxLayout()
        outer.setSpacing(0)

        self._cmp_panel_left = self._make_cmp_panel("left")
        self._cmp_panel_right = self._make_cmp_panel("right")

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

        ml.addWidget(mid_btn("🗑", self._("tip_delete_both"), self._cmp_delete_both))
        ml.addSpacing(10)
        self._btn_undo = mid_btn("↶", self._("tip_undo"), self._undo, "btnMid", 34)
        self._btn_undo.setEnabled(False)
        ml.addWidget(self._btn_undo)
        self._btn_redo = mid_btn("↷", self._("tip_redo"), self._redo, "btnMid", 34)
        self._btn_redo.setEnabled(False)
        ml.addWidget(self._btn_redo)
        ml.addStretch()

        outer.addWidget(self._cmp_panel_left, stretch=1)
        outer.addWidget(mid)
        outer.addWidget(self._cmp_panel_right, stretch=1)
        vl.addLayout(outer, stretch=1)

        bot = QHBoxLayout()
        bot.setSpacing(8)
        self._cmp_cnt_left = QLabel(self._("entries", n=0))
        self._cmp_cnt_right = QLabel(self._("entries", n=0))
        for lbl in (self._cmp_cnt_left, self._cmp_cnt_right):
            lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:12px;")

        def bot_btn(label, tip, slot, name="btnHtml"):
            b = QPushButton(label)
            b.setObjectName(name)
            b.setFixedHeight(34)
            b.setToolTip(tip)
            b.clicked.connect(slot)
            return b

        bot.addWidget(self._cmp_cnt_left)
        bot.addWidget(bot_btn(self._("btn_save_left"), self._("btn_save_left_tip"),
                              lambda: self._cmp_save("left")))
        bot.addStretch()
        self.btn_fullscreen = QPushButton(self._("btn_fullscreen"))
        self.btn_fullscreen.setFixedHeight(34)
        self.btn_fullscreen.setToolTip(self._("btn_fullscreen_tip"))
        self.btn_fullscreen.clicked.connect(self._toggle_fullscreen)
        bot.addWidget(self.btn_fullscreen)
        bot.addStretch()
        bot.addWidget(self._cmp_cnt_right)
        bot.addWidget(bot_btn(self._("btn_save_right"), self._("btn_save_right_tip"),
                              lambda: self._cmp_save("right")))
        vl.addLayout(bot)

        self.root_layout.addWidget(w, stretch=1)

    # ── Panel ──────────────────────────────────────────────────────────────────
    def _make_cmp_panel(self, side):
        panel = QWidget()
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(4)

        sw = QWidget()
        sw.setObjectName("searchBox")
        sw.setFixedHeight(30)
        sw.setStyleSheet(
            f"#searchBox {{ background:{SURFACE}; border:1px solid {BORDER}; "
            f"border-radius:8px; }}")
        swl = QHBoxLayout(sw)
        swl.setContentsMargins(8, 0, 6, 0)
        swl.setSpacing(4)

        lupe = QLabel("🔍")
        lupe.setStyleSheet(
            f"border:none; background:transparent; color:{SUBTEXT}; font-size:12px;")
        inp = QLineEdit()
        inp.setPlaceholderText(self._("search_placeholder"))
        inp.setStyleSheet(
            f"QLineEdit {{ border:none; background:transparent; color:{TEXT}; "
            f"font-size:12px; padding:0; }}"
            f"QLineEdit:focus {{ border:none; }}")
        swl.addWidget(lupe)
        swl.addWidget(inp)

        opt_btn = QToolButton()
        opt_btn.setText("⚙️")
        opt_btn.setToolTip(self._("search_options_tip"))
        opt_btn.setStyleSheet(f"border:none; background:transparent; color:{SUBTEXT}; font-size:14px;")
        opt_btn.clicked.connect(lambda: self._show_search_options(side))
        swl.addWidget(opt_btn)

        tree = CmpTree(self._cmp_handle_drop)
        tree.setHeaderLabels([self._("col_title"), self._("col_url"), self._("col_status")])
        tree.setColumnWidth(0, 220)
        tree.setColumnWidth(1, 450)
        tree.setColumnWidth(2, 100)
        tree.setAlternatingRowColors(True)
        tree.setAnimated(True)
        tree.setToolTip(self._("tree_tooltip"))
        tree.setStyleSheet(
            f"QTreeWidget {{ border-radius: 8px; font-size: 12px; }}"
            f"QTreeWidget::item {{ padding: 3px 6px; }}"
            f"QTreeWidget QLineEdit {{"
            f"  border: 1px solid {ACCENT}; border-radius: 0px;"
            f"  margin: 0px; padding: 0px 2px;"
            f"  font-weight: normal; font-size: 12px;"
            f"  min-height: 0px; background: {SURFACE}; color: {TEXT};"
            f"}}"
            f"QTreeWidget QLineEdit:focus {{"
            f"  border: 1px solid {ACCENT}; border-radius: 0px;"
            f"}}"
        )
        tree.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.SelectedClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed)
        tree.itemChanged.connect(self._edit_item_changed)

        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(lambda pos: self._show_context_menu(side, pos))

        pl.addWidget(sw)
        pl.addWidget(tree, stretch=1)

        if side == "left":
            self._cmp_tree_left = tree
            self._cmp_search_left = inp
            inp.textChanged.connect(lambda t: self._cmp_filter("left", t))
        else:
            self._cmp_tree_right = tree
            self._cmp_search_right = inp
            inp.textChanged.connect(lambda t: self._cmp_filter("right", t))

        return panel

    # ── Suchoptionen ──────────────────────────────────────────────────────────
    def _show_search_options(self, side):
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
        """)
        act_case = QAction(self._("search_case_sensitive"), self, checkable=True)
        act_case.setChecked(self._search_case_sensitive)
        act_case.triggered.connect(lambda: self._toggle_search_option("case", side))

        act_regex = QAction(self._("search_regex"), self, checkable=True)
        act_regex.setChecked(self._search_regex)
        act_regex.triggered.connect(lambda: self._toggle_search_option("regex", side))

        act_path = QAction(self._("search_path"), self, checkable=True)
        act_path.setChecked(self._search_path)
        act_path.triggered.connect(lambda: self._toggle_search_option("path", side))

        menu.addAction(act_case)
        menu.addAction(act_regex)
        menu.addAction(act_path)
        menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))

    def _toggle_search_option(self, option, side):
        if option == "case":
            self._search_case_sensitive = not self._search_case_sensitive
        elif option == "regex":
            self._search_regex = not self._search_regex
        elif option == "path":
            self._search_path = not self._search_path
        tree, _, _, search = self._cmp_widgets(side)
        self._cmp_filter(side, search.text())

    # ── Filter ──────────────────────────────────────────────────────────────────
    def _cmp_filter(self, side, text):
        tree, *_ = self._cmp_widgets(side)
        text = text.strip()
        if not text:
            self._show_all_items(tree)
            return

        case_sensitive = self._search_case_sensitive
        use_regex = self._search_regex
        search_path = self._search_path

        def matches(item_text: str) -> bool:
            if not case_sensitive:
                item_text = item_text.lower()
                search_text = text.lower()
            else:
                search_text = text
            if use_regex:
                try:
                    return bool(re.search(search_text, item_text))
                except re.error:
                    return search_text in item_text
            else:
                return search_text in item_text

        def visit(item):
            d = item.data(0, Qt.ItemDataRole.UserRole) or {}
            if d.get("type") == "bookmark":
                title = item.text(0)
                url = item.text(1)
                path = d.get("path", "") if search_path else ""
                vis = (matches(title) or matches(url) or (search_path and matches(path)))
                item.setHidden(not vis)
                return vis
            else:
                name = d.get("name", "")
                self_match = search_path and matches(name)
                if self_match:
                    self._show_all_items(item)
                    item.setExpanded(True)
                    return True
                any_vis = False
                for i in range(item.childCount()):
                    if visit(item.child(i)):
                        any_vis = True
                vis = any_vis
                item.setHidden(not vis)
                item.setExpanded(vis)
                return vis

        root = tree.invisibleRootItem()
        for i in range(root.childCount()):
            visit(root.child(i))

    def _show_all_items(self, item):
        item.setHidden(False)
        for i in range(item.childCount()):
            self._show_all_items(item.child(i))

    # ── Kontextmenü ────────────────────────────────────────────────────────────
    def _show_context_menu(self, side, pos):
        tree, *_ = self._cmp_widgets(side)
        item = tree.itemAt(pos)

        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())

        if item is None:
            new_folder_act = QAction(self._("ctx_new_folder"), self)
            new_folder_act.triggered.connect(lambda: self._create_folder(side, None))
            menu.addAction(new_folder_act)
            menu.addSeparator()
            validate_all_act = QAction(self._("ctx_validate_all"), self)
            validate_all_act.triggered.connect(lambda: self._validate_side(side))
            menu.addAction(validate_all_act)
            menu.addSeparator()
            dup_act = QAction(self._("ctx_find_duplicates"), self)
            dup_act.triggered.connect(lambda: self._find_duplicates(side))
            menu.addAction(dup_act)
            merge_act = QAction(self._("ctx_merge_duplicates"), self)
            merge_act.triggered.connect(lambda: self._merge_duplicates(side))
            menu.addAction(merge_act)
            menu.exec(tree.mapToGlobal(pos))
            return

        data = item.data(0, Qt.ItemDataRole.UserRole) or {}
        is_folder = data.get("type") == "folder"
        is_bookmark = data.get("type") == "bookmark"
        status = data.get("status", 0)

        # ── 1. Bearbeiten ────────────────────────────────────────────────────
        if is_bookmark:
            open_act = QAction(self._("ctx_open_in_browser"), self)
            open_act.triggered.connect(lambda: self._open_in_browser(item))
            menu.addAction(open_act)

            copy_act = QAction(self._("ctx_copy"), self)
            copy_act.triggered.connect(lambda: self._copy_to_clipboard(item))
            menu.addAction(copy_act)

        if is_folder:
            rename_act = QAction(self._("ctx_rename"), self)
            rename_act.triggered.connect(lambda: self._rename_item(item))
            menu.addAction(rename_act)

        new_folder_act = QAction(self._("ctx_new_folder"), self)
        new_folder_act.triggered.connect(lambda: self._create_folder(side, item if is_folder else None))
        menu.addAction(new_folder_act)

        menu.addSeparator()

        # ── 2. Sortieren ────────────────────────────────────────────────────
        sort_menu = menu.addMenu(self._("ctx_sort"))
        sort_title_asc = QAction(self._("ctx_sort_title_asc"), self)
        sort_title_asc.triggered.connect(lambda: self._sort_tree(side, "title", True))
        sort_menu.addAction(sort_title_asc)
        sort_title_desc = QAction(self._("ctx_sort_title_desc"), self)
        sort_title_desc.triggered.connect(lambda: self._sort_tree(side, "title", False))
        sort_menu.addAction(sort_title_desc)
        sort_url_asc = QAction(self._("ctx_sort_url_asc"), self)
        sort_url_asc.triggered.connect(lambda: self._sort_tree(side, "url", True))
        sort_menu.addAction(sort_url_asc)
        sort_url_desc = QAction(self._("ctx_sort_url_desc"), self)
        sort_url_desc.triggered.connect(lambda: self._sort_tree(side, "url", False))
        sort_menu.addAction(sort_url_desc)

        menu.addSeparator()

        # ── 3. Duplikate ────────────────────────────────────────────────────
        dup_act = QAction(self._("ctx_find_duplicates"), self)
        dup_act.triggered.connect(lambda: self._find_duplicates(side))
        menu.addAction(dup_act)
        merge_act = QAction(self._("ctx_merge_duplicates"), self)
        merge_act.triggered.connect(lambda: self._merge_duplicates(side))
        menu.addAction(merge_act)

        menu.addSeparator()

        # ── 4. Validierung ──────────────────────────────────────────────────
        selected = tree.selectedItems()
        bookmark_selected = [it for it in selected if (it.data(0, Qt.ItemDataRole.UserRole) or {}).get("type") == "bookmark"]

        if len(bookmark_selected) > 1:
            validate_multi_act = QAction(self._("ctx_validate_selected"), self)
            validate_multi_act.triggered.connect(lambda: self._validate_selected(side))
            menu.addAction(validate_multi_act)
        elif len(bookmark_selected) == 1:
            validate_act = QAction(self._("ctx_validate_item"), self)
            validate_act.triggered.connect(lambda: self._validate_item(side, bookmark_selected[0]))
            menu.addAction(validate_act)

            if status and (status >= 400 or status == 0):
                del_dead_act = QAction(self._("ctx_delete_dead"), self)
                del_dead_act.triggered.connect(lambda: self._delete_dead_item(bookmark_selected[0]))
                menu.addAction(del_dead_act)

                move_dead_act = QAction(self._("ctx_move_dead"), self)
                move_dead_act.triggered.connect(lambda: self._move_dead_item(side, bookmark_selected[0]))
                menu.addAction(move_dead_act)
        else:
            validate_all_act = QAction(self._("ctx_validate_all"), self)
            validate_all_act.triggered.connect(lambda: self._validate_side(side))
            menu.addAction(validate_all_act)

        menu.addSeparator()

        # ── 5. Löschen ─────────────────────────────────────────────────────
        del_act = QAction(self._("ctx_delete"), self)
        del_act.triggered.connect(lambda: self._delete_selected(side))
        menu.addAction(del_act)

        menu.exec(tree.mapToGlobal(pos))

    def _menu_style(self):
        return f"""
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
        """

    # ── Kontextmenü-Aktionen ───────────────────────────────────────────────────
    def _open_in_browser(self, item):
        d = item.data(0, Qt.ItemDataRole.UserRole) or {}
        url = d.get("url", "")
        if url:
            webbrowser.open(url)

    def _copy_to_clipboard(self, item):
        d = item.data(0, Qt.ItemDataRole.UserRole) or {}
        title = d.get("title", "")
        url = d.get("url", "")
        text = f"{title}\n{url}" if title else url
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.statusBar().showMessage(self._("status_copied"), 2000)

    def _create_folder(self, side, parent_item=None):
        tree, *_ = self._cmp_widgets(side)
        parent = parent_item or tree.invisibleRootItem()
        name, ok = QMessageBox.getText(self, self._("dlg_new_folder_title"), self._("dlg_new_folder_label"))
        if not ok or not name.strip():
            return
        folder = QTreeWidgetItem(parent, [f"📁  {name.strip()}", "", ""])
        folder.setForeground(0, QColor(FOLDER_C))
        fnt = folder.font(0); fnt.setBold(True); folder.setFont(0, fnt)
        folder.setData(0, Qt.ItemDataRole.UserRole, {"type": "folder", "name": name.strip()})
        parent.setExpanded(True)
        self._cmp_refresh(side)
        self._cmp_set_dirty(side)
        self._update_folder_counts(tree)
        self._history_push()

    def _rename_item(self, item):
        d = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if d.get("type") != "folder":
            return
        old_name = d.get("name", "")
        new_name, ok = QMessageBox.getText(self, self._("dlg_rename_title"), self._("dlg_rename_label"), text=old_name)
        if not ok or not new_name.strip() or new_name == old_name:
            return
        d["name"] = new_name.strip()
        item.setData(0, Qt.ItemDataRole.UserRole, d)
        # Update folder text (count will be recalculated)
        tree = item.treeWidget()
        if tree is not None:
            self._update_folder_counts(tree)
        self._cmp_set_dirty(self._cmp_side_of(item.treeWidget()))
        self._history_push()

    def _delete_selected(self, side):
        self._cmp_delete(side)

    # ── Duplikate ──────────────────────────────────────────────────────────────
    def _find_duplicates(self, side):
        tree, *_ = self._cmp_widgets(side)
        bookmarks = self._cmp_tree_to_list(tree)
        groups = find_duplicates(bookmarks)
        if not groups:
            QMessageBox.information(self, self._("dlg_no_duplicates_title"), self._("dlg_no_duplicates_text"))
            return
        msg = self._("dlg_duplicates_found", count=len(groups))
        QMessageBox.information(self, self._("dlg_duplicates_title"), msg)

    def _merge_duplicates(self, side):
        tree, *_ = self._cmp_widgets(side)
        bookmarks = self._cmp_tree_to_list(tree)
        merged = merge_duplicates(bookmarks)
        if len(merged) == len(bookmarks):
            QMessageBox.information(self, self._("dlg_no_duplicates_title"), self._("dlg_no_duplicates_text"))
            return
        self._cmp_build_combined_tree(tree, merged)
        self._cmp_refresh(side)
        self._cmp_set_dirty(side)
        self._update_folder_counts(tree)
        self._history_push()
        self.statusBar().showMessage(self._("status_merged", removed=len(bookmarks)-len(merged)), 4000)

    # ── Sortierung ─────────────────────────────────────────────────────────────
    def _sort_tree(self, side, key, ascending):
        tree, *_ = self._cmp_widgets(side)
        def sort_item(item):
            children = [item.child(i) for i in range(item.childCount())]
            if key == "title":
                children.sort(key=lambda it: it.text(0).lower(), reverse=not ascending)
            else:  # url
                children.sort(key=lambda it: it.text(1).lower(), reverse=not ascending)
            for i, child in enumerate(children):
                item.takeChild(0)
                item.insertChild(i, child)
                sort_item(child)

        root = tree.invisibleRootItem()
        sort_item(root)
        tree.collapseAll()
        self._cmp_set_dirty(side)
        self._update_folder_counts(tree)
        self._history_push()
        self.statusBar().showMessage(self._("status_sorted"), 2000)

    # ── Validierung ────────────────────────────────────────────────────────────
    def _validate_side(self, side):
        if self._validation_running:
            self.statusBar().showMessage(self._("status_validation_running"), 3000)
            return

        tree, *_ = self._cmp_widgets(side)
        bookmarks = self._cmp_tree_to_list(tree)
        if not bookmarks:
            self.statusBar().showMessage(self._("status_no_bookmarks_validate"), 3000)
            return

        items = self._collect_bookmark_items(tree.invisibleRootItem())
        if not items:
            return

        self._validation_running = True
        self.statusBar().showMessage(self._("status_validation_start"), 3000)

        progress = QProgressDialog(self._("validation_progress"), self._("validation_cancel"), 0, len(items), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        validator = BookmarkValidator(timeout=10, max_workers=10)

        def update_progress(done, total):
            progress.setValue(done)
            if done < total:
                progress.setLabelText(self._("validation_progress_text", done=done, total=total))

        def on_finished():
            self._validation_running = False
            progress.setValue(len(items))
            for item, bm in items:
                status = validator.get_status(bm.url)
                self._update_item_status(item, status)
            self._cmp_set_dirty(side)
            progress.close()
            self.statusBar().showMessage(self._("status_validation_done", checked=len(items)), 4000)

        def check():
            validator.check_bookmarks(bookmarks, progress_callback=update_progress)

        thread = threading.Thread(target=check)
        thread.finished.connect(on_finished)
        thread.start()

        progress.canceled.connect(lambda: setattr(self, '_validation_running', False))

    def _validate_item(self, side, item):
        d = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if d.get("type") != "bookmark":
            return
        url = d.get("url", "")
        if not url:
            return
        validator = BookmarkValidator()
        status = validator._check_url(url)
        self._update_item_status(item, status)
        self._cmp_set_dirty(side)
        self._history_push()
        self.statusBar().showMessage(self._("status_validation_done", checked=1), 4000)

    def _validate_selected(self, side):
        tree, *_ = self._cmp_widgets(side)
        selected_items = tree.selectedItems()
        bookmark_items = []
        for it in selected_items:
            d = it.data(0, Qt.ItemDataRole.UserRole) or {}
            if d.get("type") == "bookmark":
                bookmark_items.append(it)

        if not bookmark_items:
            self.statusBar().showMessage("Keine Lesezeichen ausgewählt.", 3000)
            return

        self.statusBar().showMessage(f"⏳ Prüfe {len(bookmark_items)} ausgewählte Links ...", 3000)
        QApplication.processEvents()

        validator = BookmarkValidator(timeout=10, max_workers=5)
        total = len(bookmark_items)
        for i, item in enumerate(bookmark_items):
            d = item.data(0, Qt.ItemDataRole.UserRole) or {}
            url = d.get("url", "")
            if url:
                status = validator._check_url(url)
                self._update_item_status(item, status)
            self.statusBar().showMessage(f"⏳ Prüfe {i+1}/{total} ...", 3000)
            QApplication.processEvents()

        self._cmp_set_dirty(side)
        self._history_push()
        self.statusBar().showMessage(f"✓ {total} Links geprüft", 4000)

    def _collect_bookmark_items(self, parent):
        result = []
        for i in range(parent.childCount()):
            child = parent.child(i)
            d = child.data(0, Qt.ItemDataRole.UserRole) or {}
            if d.get("type") == "bookmark":
                bm = Bookmark(title=d.get("title", ""), url=d.get("url", ""), path=d.get("path", ""))
                result.append((child, bm))
            else:
                result.extend(self._collect_bookmark_items(child))
        return result

    def _update_item_status(self, item, status_code):
        d = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if d.get("type") != "bookmark":
            return
        d["status"] = status_code
        item.setData(0, Qt.ItemDataRole.UserRole, d)

        if status_code == 0:
            display = "❌ Fehler"
            bg_color = QColor("#ffebee")
        elif 200 <= status_code < 400:
            display = f"✅ {status_code}"
            bg_color = QColor("#e8f5e9")
        else:
            display = f"❌ {status_code}"
            bg_color = QColor("#ffebee")

        item.setText(2, display)
        for col in range(3):
            item.setBackground(col, bg_color)
            item.setForeground(col, QColor(TEXT))

    def _delete_dead_item(self, item):
        d = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if d.get("type") != "bookmark":
            return
        status = d.get("status", 0)
        if status and (status >= 400 or status == 0):
            reply = QMessageBox.question(self, self._("dlg_delete_dead_title"),
                                         self._("dlg_delete_dead_text", title=d.get("title", "")),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                parent = item.parent() or item.treeWidget().invisibleRootItem()
                parent.takeChild(parent.indexOfChild(item))
                side = self._cmp_side_of(item.treeWidget())
                tree = item.treeWidget()
                self._cmp_refresh(side)
                self._cmp_set_dirty(side)
                if tree is not None:
                    self._update_folder_counts(tree)
                self._history_push()

    def _move_dead_item(self, side, item):
        d = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if d.get("type") != "bookmark":
            return
        status = d.get("status", 0)
        if status and (status >= 400 or status == 0):
            tree, *_ = self._cmp_widgets(side)
            root = tree.invisibleRootItem()
            invalid_folder = None
            for i in range(root.childCount()):
                child = root.child(i)
                dd = child.data(0, Qt.ItemDataRole.UserRole) or {}
                if dd.get("type") == "folder" and dd.get("name") == "Ungültig":
                    invalid_folder = child
                    break
            if invalid_folder is None:
                invalid_folder = QTreeWidgetItem(root, [f"📁  Ungültig", "", ""])
                invalid_folder.setForeground(0, QColor(FOLDER_C))
                fnt = invalid_folder.font(0); fnt.setBold(True); invalid_folder.setFont(0, fnt)
                invalid_folder.setData(0, Qt.ItemDataRole.UserRole, {"type": "folder", "name": "Ungültig"})
                root.setExpanded(True)

            clone = QTreeWidgetItem(invalid_folder, [item.text(0), item.text(1), item.text(2)])
            clone.setData(0, Qt.ItemDataRole.UserRole, dict(item.data(0, Qt.ItemDataRole.UserRole) or {}))
            for col in range(3):
                clone.setBackground(col, item.background(col))
                clone.setForeground(col, item.foreground(col))
            invalid_folder.setExpanded(True)

            parent = item.parent() or tree.invisibleRootItem()
            parent.takeChild(parent.indexOfChild(item))

            self._cmp_refresh(side)
            self._cmp_set_dirty(side)
            self._update_folder_counts(tree)
            self._history_push()
            self.statusBar().showMessage(self._("status_moved_dead"), 4000)

    # ── Ordner-Zählung aktualisieren (NEU) ────────────────────────────────────
    def _update_folder_counts(self, tree):
        """Aktualisiert die Anzeige der Anzahl der Lesezeichen pro Ordner (rekursiv)."""
        def count_bookmarks(item):
            """Zählt rekursiv die Anzahl der Lesezeichen unter diesem Item."""
            d = item.data(0, Qt.ItemDataRole.UserRole) or {}
            if d.get("type") == "bookmark":
                return 1
            if d.get("type") == "folder":
                total = 0
                for i in range(item.childCount()):
                    total += count_bookmarks(item.child(i))
                return total
            # Für andere Typen (z.B. Root) einfach Kinder zählen
            total = 0
            for i in range(item.childCount()):
                total += count_bookmarks(item.child(i))
            return total

        def update_item(item):
            d = item.data(0, Qt.ItemDataRole.UserRole) or {}
            if d.get("type") == "folder":
                name = d.get("name", "")
                count = count_bookmarks(item)
                # Text setzen: "📁  Name (count)" oder "📁  Name" wenn count=0
                if count > 0:
                    new_text = f"📁  {name} ({count})"
                else:
                    new_text = f"📁  {name}"
                if item.text(0) != new_text:
                    item.setText(0, new_text)
                # Kinder rekursiv aktualisieren (optional, da count_bookmarks schon alles zählt,
                # aber für die Anzeige der Unterordner brauchen wir es trotzdem)
                for i in range(item.childCount()):
                    update_item(item.child(i))
            elif d.get("type") == "bookmark":
                # Nichts zu tun
                pass

        root = tree.invisibleRootItem()
        for i in range(root.childCount()):
            update_item(root.child(i))

    # ── Grundlegende Baum-Operationen ──────────────────────────────────────
    def _cmp_widgets(self, side):
        if side == "left":
            return (self._cmp_tree_left, self._cmp_cnt_left,
                    self._cmp_lbl_left, self._cmp_search_left)
        return (self._cmp_tree_right, self._cmp_cnt_right,
                self._cmp_lbl_right, self._cmp_search_right)

    def _cmp_side_of(self, tree):
        return "left" if tree is self._cmp_tree_left else "right"

    @staticmethod
    def _cmp_parent_and_index(tree, item):
        parent = item.parent() or tree.invisibleRootItem()
        return parent, parent.indexOfChild(item)

    def _cmp_drop_position(self, target_tree, target_item, indicator):
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
        if indicator == Pos.OnItem:
            parent, idx = self._cmp_parent_and_index(target_tree, target_item)
            return parent, idx + 1
        return root_item, root_item.childCount()

    def _cmp_clone_item(self, item):
        d = dict(item.data(0, Qt.ItemDataRole.UserRole) or {})
        clone = QTreeWidgetItem([item.text(0), item.text(1), item.text(2)])
        clone.setData(0, Qt.ItemDataRole.UserRole, d)
        if d.get("type") == "folder":
            clone.setForeground(0, QColor(FOLDER_C))
            fnt = clone.font(0)
            fnt.setBold(True)
            clone.setFont(0, fnt)
        else:
            clone.setForeground(0, QColor(TEXT))
            clone.setForeground(1, QColor(SUBTEXT))
            clone.setToolTip(1, item.text(1))
            clone.setFlags(clone.flags() | Qt.ItemFlag.ItemIsEditable)
        for i in range(item.childCount()):
            clone.addChild(self._cmp_clone_item(item.child(i)))
        return clone

    def _cmp_top_level_roots(self, items):
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
        if not items:
            return False
        dragged_ids = set(id(it) for it in items)
        roots = self._cmp_top_level_roots(items)
        if not roots:
            return False
        anc = target_item
        while anc is not None:
            if id(anc) in dragged_ids:
                self.statusBar().showMessage(self._("status_self_drop"), 3000)
                return False
            anc = anc.parent()

        def detach(it):
            parent = it.parent()
            if parent is None:
                return source.takeTopLevelItem(source.indexOfTopLevelItem(it))
            return parent.takeChild(parent.indexOfChild(it))

        detached = [detach(it) for it in roots]
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
        if not items:
            return False
        roots = self._cmp_top_level_roots(items)
        if not roots:
            return False
        clones = [self._cmp_clone_item(it) for it in roots]
        root_item = target_tree.invisibleRootItem()
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
        self._update_folder_counts(target_tree)
        self._history_push()
        return True

    # ── Laden / Speichern ───────────────────────────────────────────────────
    def _cmp_load_into(self, side, bookmarks, label):
        tree, cnt, lbl, search = self._cmp_widgets(side)
        self._cmp_build_combined_tree(tree, bookmarks)
        self._cmp_base_label[side] = label
        lbl.setText(label)
        cnt.setText(self._("entries", n=len(bookmarks)))
        search.clear()
        self._cmp_set_dirty(side, False)
        self._history_reset()

    def _cmp_set_dirty(self, side, dirty=True):
        self._cmp_dirty[side] = dirty
        _, _, lbl, _ = self._cmp_widgets(side)
        base = self._cmp_base_label.get(side, "")
        lbl.setText(("●  " + base) if dirty else base)

    def _cmp_new_empty(self, side):
        tree, *_ = self._cmp_widgets(side)
        if self._cmp_tree_to_list(tree):
            if QMessageBox.question(
                    self, self._("dlg_new_empty_title"),
                    self._("dlg_new_empty_text")) != QMessageBox.StandardButton.Yes:
                return
        self._cmp_load_into(side, [], self._("new_file_label"))
        self.statusBar().showMessage(self._("status_empty_created"), 4000)

    def _cmp_open_file(self, side):
        path, _ = QFileDialog.getOpenFileName(
            self, self._("dlg_open_title"), str(Path.home()),
            self._("dlg_open_filter"))
        if not path:
            return
        try:
            bookmarks = load_bookmarks_from_file(Path(path))
        except Exception as e:
            QMessageBox.critical(self, self._("dlg_error_title"),
                                 self._("dlg_error_load", err=e))
            return
        short = Path(path).name
        self._cmp_load_into(side, bookmarks, short)
        self.statusBar().showMessage(
            self._("status_loaded", n=len(bookmarks), label=short), 4000)

    def _cmp_browser_menu(self, side, button):
        browsers = detect_browsers()
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
            a = menu.addAction(self._("browser_none"))
            a.setEnabled(False)
        else:
            for label, kind, src in browsers:
                a = menu.addAction(self._("browser_icon", label=label))
                acts[a] = (label, kind, src)
        pos = button.mapToGlobal(button.rect().bottomLeft())
        chosen = menu.exec(pos)
        if chosen in acts:
            label, kind, src = acts[chosen]
            self._cmp_open_browser(side, label, kind, src)

    def _cmp_open_browser(self, side, label, kind, src):
        try:
            bookmarks = load_browser_bookmarks(kind, src)
        except Exception as e:
            QMessageBox.critical(
                self, self._("dlg_error_title"),
                self._("dlg_error_browser", label=label, err=e))
            return
        if not bookmarks:
            self.statusBar().showMessage(
                self._("status_no_bookmarks", label=label), 4000)
            return
        self._cmp_load_into(side, bookmarks, self._("browser_icon", label=label))
        self.statusBar().showMessage(
            self._("status_loaded", n=len(bookmarks), label=label), 4000)

    def _cmp_build_combined_tree(self, tree, bookmarks, editable=True):
        tree.blockSignals(True)
        tree.clear()
        folder_items = {}

        def get_folder(path):
            parent = tree.invisibleRootItem()
            key = ""
            for part in [p.strip() for p in (path or "").split("/") if p.strip()]:
                key = (key + " / " + part) if key else part
                node = folder_items.get(key)
                if node is None:
                    node = QTreeWidgetItem(parent, [f"📁  {part}", "", ""])
                    node.setForeground(0, QColor(FOLDER_C))
                    fnt = node.font(0)
                    fnt.setBold(True)
                    node.setFont(0, fnt)
                    node.setData(0, Qt.ItemDataRole.UserRole,
                                 {"type": "folder", "name": part})
                    folder_items[key] = node
                parent = node
            return parent

        for bm in bookmarks:
            parent = get_folder(bm.path or "")
            leaf = QTreeWidgetItem(parent, [bm.title, bm.url, ""])
            leaf.setForeground(0, QColor(TEXT))
            leaf.setForeground(1, QColor(SUBTEXT))
            leaf.setData(0, Qt.ItemDataRole.UserRole,
                         {"type": "bookmark", "title": bm.title, "url": bm.url})
            leaf.setToolTip(1, bm.url)
            if editable:
                leaf.setFlags(leaf.flags() | Qt.ItemFlag.ItemIsEditable)

        tree.collapseAll()
        tree.blockSignals(False)

        # Nach dem Aufbau die Ordnerzählung aktualisieren
        self._update_folder_counts(tree)

    def _cmp_tree_to_list(self, tree):
        result = []

        def walk(item, parts):
            for i in range(item.childCount()):
                child = item.child(i)
                d = child.data(0, Qt.ItemDataRole.UserRole) or {}
                if d.get("type") == "bookmark":
                    result.append(Bookmark(
                        title=d.get("title", ""),
                        url=d.get("url", ""),
                        path=" / ".join(parts),
                    ))
                else:
                    walk(child, parts + [d.get("name", "")])

        walk(tree.invisibleRootItem(), [])
        return result

    def _cmp_refresh(self, side):
        tree, cnt, _, _ = self._cmp_widgets(side)
        cnt.setText(self._("entries", n=len(self._cmp_tree_to_list(tree))))

    def _cmp_delete_both(self):
        n = 0
        for side in ("left", "right"):
            n += self._cmp_delete(side)
        if not n:
            self.statusBar().showMessage(self._("status_no_selection"), 3000)
            return
        self._history_push()
        self.statusBar().showMessage(self._("status_deleted", n=n), 4000)

    def _cmp_delete(self, side):
        tree, *_ = self._cmp_widgets(side)
        roots = self._cmp_top_level_roots(tree.selectedItems())
        if not roots:
            return 0
        for it in roots:
            parent = it.parent() or tree.invisibleRootItem()
            parent.takeChild(parent.indexOfChild(it))
        self._cmp_refresh(side)
        self._cmp_set_dirty(side)
        self._update_folder_counts(tree)
        return len(roots)

    def _cmp_expanded_paths(self, tree):
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
        snap = {}
        for side in ("left", "right"):
            tree, *_ = self._cmp_widgets(side)
            snap[side] = {
                "items": self._cmp_tree_to_list(tree),
                "expanded": self._cmp_expanded_paths(tree),
                "dirty": self._cmp_dirty.get(side, False),
                "base": self._cmp_base_label.get(side, ""),
            }
        return snap

    def _history_reset(self):
        self._history = [self._snapshot()]
        self._hist_idx = 0
        self._update_history_buttons()

    def _history_push(self):
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
        self.statusBar().showMessage(self._("status_undo"), 2000)

    def _redo(self):
        if self._hist_idx >= len(self._history) - 1:
            return
        self._hist_idx += 1
        self._history_restore(self._history[self._hist_idx])
        self._update_history_buttons()
        self.statusBar().showMessage(self._("status_redo"), 2000)

    def _update_history_buttons(self):
        self._btn_undo.setEnabled(self._hist_idx > 0)
        self._btn_redo.setEnabled(self._hist_idx < len(self._history) - 1)

    def _cmp_save(self, side):
        tree, *_ = self._cmp_widgets(side)
        bookmarks = self._cmp_tree_to_list(tree)
        if not bookmarks:
            QMessageBox.warning(self,
                                self._("dlg_save_empty_title"),
                                self._("dlg_save_empty_text"))
            return False
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = self._("dlg_save_default", side=side, ts=ts)
        path, selected = QFileDialog.getSaveFileName(
            self, self._("dlg_save_title"),
            str(Path.home() / default_name),
            self._("dlg_save_filter"))
        if not path:
            return False
        p = Path(path)

        filter_ext = {
            "JSON (*.json)": ".json",
            "CSV (*.csv)": ".csv",
            "HTML (*.html)": ".html",
            "Opera ADR (*.adr)": ".adr",
            "IE URL (*.url)": ".url",
        }

        if p.suffix.lower() not in (".json", ".csv", ".html", ".adr", ".url"):
            p = p.with_suffix(filter_ext.get(selected, ".json"))

        save_bookmarks_to_file(bookmarks, p, selected)
        self._cmp_base_label[side] = p.name
        self._cmp_set_dirty(side, False)
        self.statusBar().showMessage(self._("status_saved", path=p), 4000)
        return True

    def _toggle_fullscreen(self):
        if not self._fullscreen_mode:
            self._prev_size = self.size()
            self._prev_pos = self.pos()
            self.header_widget.hide()
            self.showMaximized()
            self.btn_fullscreen.setText(self._("btn_fullscreen_exit"))
            self._fullscreen_mode = True
        else:
            self.header_widget.show()
            self.showNormal()
            self.resize(self._prev_size)
            self.move(self._prev_pos)
            self.btn_fullscreen.setText(self._("btn_fullscreen"))
            self._fullscreen_mode = False

    def _edit_item_changed(self, item, column):
        if self._edit_syncing:
            return
        d = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(d, dict) and d.get("type") == "bookmark":
            d["title"] = item.text(0)
            d["url"] = item.text(1)
            self._edit_syncing = True
            item.setData(0, Qt.ItemDataRole.UserRole, d)
            item.setToolTip(1, item.text(1))
            self._edit_syncing = False
            tree = item.treeWidget()
            if tree is not None:
                self._cmp_set_dirty(self._cmp_side_of(tree))
                self._update_folder_counts(tree)
            self._history_push()

    def closeEvent(self, event):
        # Fenstergröße automatisch speichern
        s = QSettings("computer-experte", "BookmarkOrganisator")
        s.setValue("window/geometry", self.saveGeometry())

        for side in ("left", "right"):
            if not self._cmp_dirty.get(side):
                continue
            if not self._cmp_tree_to_list(self._cmp_widgets(side)[0]):
                continue

            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Question)
            box.setWindowTitle(self._("dlg_close_title"))
            side_label = self._("side_label_left" if side == "left" else "side_label_right")
            box.setText(self._("dlg_close_text",
                               side_label=side_label,
                               base=self._cmp_base_label.get(side, "")))
            box.setStandardButtons(
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel)
            box.setDefaultButton(QMessageBox.StandardButton.Save)
            box.button(QMessageBox.StandardButton.Save).setText(self._("dlg_close_save"))
            box.button(QMessageBox.StandardButton.Discard).setText(self._("dlg_close_discard"))
            box.button(QMessageBox.StandardButton.Cancel).setText(self._("dlg_close_cancel"))
            choice = box.exec()

            if choice == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            if choice == QMessageBox.StandardButton.Discard:
                continue
            if not self._cmp_save(side):
                event.ignore()
                return
        event.accept()