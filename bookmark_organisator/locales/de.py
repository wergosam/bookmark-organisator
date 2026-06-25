# locales/de.py – Deutsche Übersetzungen
LANG = {
    # Fenster & Header
    "window_title":     "Bookmark-Organisator",
    "app_title":        "🔖  Bookmark-Organisator",
    "app_subtitle":     "Lesezeichen aus Dateien oder Browsern vergleichen & zusammenführen",

    # Toolbar-Buttons
    "btn_open_file":    "Datei öffnen",
    "btn_new_empty":    "Neu/Leer",
    "btn_new_empty_tip":"Leere Datei anlegen – auf dieser Seite von Grund auf sammeln",
    "btn_from_browser": "Aus Browser  ▾",

    # Mitte-Buttons (Tooltips)
    "tip_delete_both":  "Ausgewählte Einträge/Ordner auf beiden Seiten löschen",
    "tip_undo":         "Rückgängig (Strg+Z)",
    "tip_redo":         "Wiederherstellen (Strg+Y)",

    # Unterleiste
    "btn_save_left":    "💾  Links speichern",
    "btn_save_right":   "💾  Rechts speichern",
    "btn_fullscreen":   "⛶  Vollbild",
    "btn_fullscreen_exit": "✕  Vollbild beenden",
    "entries":          "{n} Einträge",

    # Baum
    "col_title":        "Titel",
    "col_url":          "URL",
    "col_status":       "Status",
    "search_placeholder": "Suchen …",
    "tree_tooltip":     ("Tipp: Titel/URL per Doppelklick bearbeiten · Lesezeichen "
                         "oder Ordner mit der Maus ziehen – zwischen den Seiten oder "
                         "zum Umsortieren innerhalb einer Seite."),

    # Statusleiste
    "status_loaded":    "✓  {n} Lesezeichen aus «{label}» geladen",
    "status_saved":     "✓  Gespeichert: {path}",
    "status_empty_created": "✓  Leere Datei angelegt – Lesezeichen hierher ziehen oder kopieren",
    "status_undo":      "↶  Rückgängig",
    "status_redo":      "↷  Wiederhergestellt",
    "status_deleted":   "🗑  {n} Element(e) gelöscht  ·  «↶» macht es rückgängig",
    "status_no_selection": "Bitte zuerst Einträge oder Ordner auswählen.",
    "status_no_bookmarks": "Keine Lesezeichen in {label} gefunden.",
    "status_self_drop": "Ein Ordner kann nicht in sich selbst verschoben werden.",
    "status_copied":    "✓  In Zwischenablage kopiert",
    "status_sorted":    "✓  Sortiert",
    "status_merged":    "✓  {removed} Duplikate entfernt",
    "status_validation_start": "⏳  Prüfe Lesezeichen …",
    "status_validation_done":  "✓  {checked} Links geprüft",
    "status_validation_running": "Prüfung läuft bereits …",
    "status_no_bookmarks_validate": "Keine Lesezeichen zum Prüfen.",
    "status_moved_dead":      "✓  Toter Link verschoben",
    "status_geometry_saved":  "✓  Fenstergröße gespeichert",
    "status_geometry_reset":  "✓  Fenstergröße zurückgesetzt",
    "status_paste_empty":     "Zwischenablage ist leer.",
    "status_paste_no_url":    "Keine gültige URL in der Zwischenablage gefunden.",
    "status_pasted":          "✓  Lesezeichen eingefügt",

    # ── NEU: Sitzungsstatus ──────────────────────────────────────────────────
    "status_session_saved":   "✓  Sitzung gespeichert: {path}",
    "status_session_loaded":  "✓  Sitzung geladen: {path}",

    # Dialoge
    "dlg_open_title":   "Lesezeichen-Datei öffnen",
    "dlg_open_filter":  "Lesezeichen (*.html *.json *.csv *.adr *.plist *.url);;Alle Dateien (*)",
    "dlg_save_title":   "Speichern als",
    "dlg_save_default": "lesezeichen_{side}_{ts}.json",
    "dlg_save_filter":  "JSON (*.json);;CSV (*.csv);;HTML (*.html);;Opera ADR (*.adr);;IE URL (*.url)",

    "dlg_new_empty_title": "Neue leere Datei",
    "dlg_new_empty_text":  ("Die aktuelle Seite enthält Einträge. Wirklich leeren und "
                            "eine neue, leere Datei anlegen?"),
    "new_file_label":   "📄  (neue Datei)",

    "dlg_save_empty_title": "Leer",
    "dlg_save_empty_text":  "Keine Einträge zum Speichern.",

    "dlg_close_title":  "Vor dem Beenden speichern?",
    "dlg_close_text":   ("Die {side_label} Seite «{base}» wurde geändert.\n"
                         "Änderungen speichern?"),
    "dlg_close_save":   "Speichern …",
    "dlg_close_discard":"Verwerfen",
    "dlg_close_cancel": "Abbrechen",
    "side_label_left":  "linke",
    "side_label_right": "rechte",

    "dlg_error_load":   "Datei konnte nicht geladen werden:\n{err}",
    "dlg_error_browser":"Lesezeichen aus {label} konnten nicht geladen werden:\n{err}",
    "dlg_error_title":  "Fehler",

    "dlg_new_folder_title": "Neuen Ordner anlegen",
    "dlg_new_folder_label": "Ordnername:",
    "dlg_rename_title":     "Ordner umbenennen",
    "dlg_rename_label":     "Neuer Name:",

    "dlg_duplicates_title":   "Duplikate gefunden",
    "dlg_duplicates_found":   "Es wurden {count} Gruppen von Duplikaten gefunden.",
    "dlg_no_duplicates_title":"Keine Duplikate",
    "dlg_no_duplicates_text": "Es wurden keine doppelten Lesezeichen gefunden.",

    "dlg_delete_dead_title":  "Toten Link löschen?",
    "dlg_delete_dead_text":   "Soll der tote Link «{title}» wirklich gelöscht werden?",

    # ── NEU: Sitzungsdialoge ─────────────────────────────────────────────────
    "dlg_session_save_title": "Sitzung speichern",
    "dlg_session_save_filter":"Bookmark-Sitzung (*.bmo)",
    "dlg_session_load_title": "Sitzung laden",
    "dlg_session_load_filter":"Bookmark-Sitzung (*.bmo)",
    "dlg_error_session_save": "Sitzung konnte nicht gespeichert werden:\n{err}",
    "dlg_error_session_load": "Sitzung konnte nicht geladen werden:\n{err}",

    # Browser-Menü
    "browser_none":     "Kein Browser mit Lesezeichen gefunden",
    "browser_icon":     "🌐  {label}",

    # Firefox-Ordnernamen
    "ff_menu":          "Lesezeichen-Menü",
    "ff_toolbar":       "Lesezeichen-Symbolleiste",
    "ff_unsorted":      "Nicht abgelegt",
    "ff_mobile":        "Mobil",
    "ff_no_name":       "(kein Name)",

    # Chromium-Ordnernamen
    "cr_toolbar":       "Lesezeichen-Symbolleiste",
    "cr_menu":          "Lesezeichen-Menü",
    "cr_other":         "Weitere Lesezeichen",
    "cr_mobile":        "Mobil",

    # HTML-Export
    "html_title":       "Bookmarks",
    "html_h1":          "Lesezeichen-Menü",

    # JSON-Fehler
    "err_json":         ("JSON muss eine Liste von Lesezeichen-Objekten "
                         "oder ein Browser-Export sein."),
    "err_format":       "Nicht unterstütztes Format.",

    # Menüs
    "menu_language":    "Sprache / Language",
    "menu_view":        "Ansicht",
    "menu_save_geometry": "Fenstergröße speichern",
    "menu_reset_geometry": "Fenstergröße zurücksetzen",
    "menu_help":        "Hilfe",
    "menu_help_manual": "Bedienungsanleitung",
    "menu_about":       "Über",

    # ── NEU: Sitzungsmenü ────────────────────────────────────────────────────
    "menu_session":           "Sitzung",
    "menu_session_save":      "Sitzung speichern…",
    "menu_session_load":      "Sitzung laden…",

    # Hilfe / Über
    "manual_title":     "Bedienungsanleitung – Bookmark-Organisator",
    "manual_close":     "Schließen",
    "manual_text": """
<h2>Bookmark-Organisator – Bedienungsanleitung</h2>

<p>Dieses Programm ermöglicht Ihnen, Lesezeichen aus verschiedenen Quellen zu laden, zu vergleichen, zu organisieren und in vielen Formaten zu exportieren. Die Oberfläche ist in zwei unabhängige Bereiche (links / rechts) aufgeteilt – jede Seite kann separat gefüllt und bearbeitet werden.</p>

<h3>📂  Lesezeichen laden</h3>
<ul>
  <li><b>Datei öffnen</b> – Unterstützte Formate: <code>.json</code> (Chromium, Firefox neu, eigene Liste), <code>.csv</code>, <code>.html</code> (Netscape‑Format), <code>.adr</code> (Opera alt), <code>.plist</code> (Safari) und <code>.url</code> (Internet Explorer).</li>
  <li><b>Neu / Leer</b> – legt eine leere Liste auf der aktuellen Seite an.</li>
  <li><b>Aus Browser ▾</b> – erkennt automatisch installierte Browser (Firefox, Chrome, Brave, Edge, Vivaldi, Opera, Falkon u. a.) und lädt deren Lesezeichen.</li>
</ul>

<h3>✏️  Bearbeiten & Organisieren</h3>
<ul>
  <li><b>Drag & Drop</b> – Ziehen Sie Lesezeichen oder ganze Ordner mit der Maus. Sie können innerhalb einer Seite umsortieren oder Elemente von links nach rechts (und umgekehrt) <i>kopieren</i> (bei Seitenwechsel) oder <i>verschieben</i> (innerhalb einer Seite).</li>
  <li><b>Doppelklick</b> – auf einen Titel oder eine URL ändert den Wert direkt in der Liste.</li>
  <li><b>Löschen</b> – markieren Sie Elemente und klicken Sie auf den <b>🗑</b>-Button in der Mitte. Sie werden auf beiden Seiten gleichzeitig gelöscht.</li>
  <li><b>Suchen</b> – oberhalb jeder Liste können Sie nach Titel, URL oder (optional) Pfad filtern. Das Zahnrad‑Icon bietet erweiterte Optionen wie Groß-/Kleinschreibung und reguläre Ausdrücke.</li>
  <li><b>Kontextmenü (rechte Maustaste)</b> – bietet schnellen Zugriff auf: Im Browser öffnen, Kopieren, Ordner anlegen/umbenennen, Sortieren (nach Titel/URL), Duplikate finden/zusammenführen, Lesezeichen validieren (Link prüfen) und Löschen.</li>
</ul>

<h3>🔍  Lesezeichen validieren (tote Links)</h3>
<ul>
  <li><b>Einzelnen Link prüfen</b> – Rechtsklick auf ein Lesezeichen → „Link prüfen“. Der HTTP‑Statuscode wird in der Spalte „Status“ angezeigt.</li>
  <li><b>Mehrere Links gleichzeitig prüfen</b> – Markieren Sie mehrere Lesezeichen (mit <b>Strg</b> oder <b>Umschalt</b>), dann Rechtsklick → „Ausgewählte Links prüfen“.</li>
  <li><b>Gesamte Seite prüfen</b> – Rechtsklick auf leeren Bereich oder Ordner → „Tote Links prüfen (Seite)“. Ein Fortschrittsdialog zeigt den Fortschritt.</li>
  <li><b>Tote Links behandeln</b> – Nach der Prüfung können Sie einzelne tote Links über das Kontextmenü löschen oder in den Ordner „Ungültig“ verschieben.</li>
  <li>Die Status‑Spalte zeigt <b>✅ 200</b> für gültige, <b>❌ 404</b> für fehlerhafte und <b>❌ Fehler</b> für nicht erreichbare Links. Die Zeilen werden farblich hinterlegt.</li>
</ul>

<h3>↶  Rückgängig / Wiederherstellen</h3>
<ul>
  <li>Die Buttons <b>↶</b> (Rückgängig) und <b>↷</b> (Wiederherstellen) in der Mitte erlauben Ihnen, Änderungen schrittweise rückgängig zu machen oder erneut anzuwenden.</li>
  <li>Tastenkürzel: <b>Strg+Z</b> (Undo) und <b>Strg+Y</b> (Redo).</li>
</ul>

<h3>💾  Speichern & Exportieren</h3>
<ul>
  <li>Unter jeder Seite befindet sich ein <b>„Speichern“</b>-Button. Sie können die aktuelle Seite als <b>JSON</b>, <b>CSV</b>, <b>HTML</b> (Netscape‑Format), <b>Opera ADR</b> oder <b>IE URL</b> exportieren.</li>
  <li>Geänderte Seiten werden durch einen <b>●</b> vor dem Dateinamen gekennzeichnet.</li>
</ul>

<h3>⛶  Vollbild</h3>
<ul>
  <li>Der Button <b>⛶ Vollbild</b> unten blendet den Titel‑Bereich aus und maximiert das Fenster – ideal für große Listen. Drücken Sie <b>F11</b> als Tastenkürzel.</li>
</ul>

<h3>🌐  Sprache wechseln</h3>
<ul>
  <li>Über das Menü <b>Sprache / Language</b> können Sie zwischen Deutsch und Englisch umschalten. Die Einstellung wird gespeichert.</li>
</ul>

<h3>🪟  Fenstergröße speichern</h3>
<ul>
  <li>Das Menü <b>Ansicht</b> bietet zwei Aktionen: <b>Fenstergröße speichern</b> (speichert die aktuelle Position und Größe) und <b>Fenstergröße zurücksetzen</b> (setzt auf Standard 1300×750 zurück). Die Größe wird automatisch beim Beenden gespeichert.</li>
</ul>

<h3>💾  Sitzungen speichern & laden</h3>
<ul>
  <li>Im Menü <b>Sitzung</b> können Sie den kompletten Zustand beider Seiten als <b>.bmo</b>-Datei speichern und später wieder laden – inklusive aller Ordner, Lesezeichen und der aktuellen Bearbeitungshistorie.</li>
</ul>

<h3>📊  Ordnerzählung</h3>
<ul>
  <li>Neben jedem Ordner wird in Klammern die Anzahl der enthaltenen Lesezeichen (rekursiv, d.h. inklusive aller Unterordner) angezeigt, z. B. <b>📁  Projekte (23)</b>. Die Zählung wird bei jeder Änderung automatisch aktualisiert.</li>
</ul>

<h3>⌨️  Alle Tastenkürzel im Überblick</h3>
<table style="border-collapse:collapse; width:100%;">
  <tr><th style="text-align:left; padding:4px 8px;">Kürzel</th><th style="text-align:left; padding:4px 8px;">Funktion</th></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+O</b></td><td style="padding:4px 8px;">Datei öffnen (links)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+Shift+O</b></td><td style="padding:4px 8px;">Datei öffnen (rechts)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+S</b></td><td style="padding:4px 8px;">Speichern (links)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+Shift+S</b></td><td style="padding:4px 8px;">Speichern (rechts)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+N</b></td><td style="padding:4px 8px;">Neu/Leer (links)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+Shift+N</b></td><td style="padding:4px 8px;">Neu/Leer (rechts)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+B</b></td><td style="padding:4px 8px;">Browser laden (links)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+Shift+B</b></td><td style="padding:4px 8px;">Browser laden (rechts)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Entf</b> / <b>Del</b></td><td style="padding:4px 8px;">Auswahl löschen (beide Seiten)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+F</b></td><td style="padding:4px 8px;">Suchfeld fokussieren (aktive Seite)</td></tr>
  <tr><td style="padding:4px 8px;"><b>F11</b></td><td style="padding:4px 8px;">Vollbild umschalten</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+Tab</b></td><td style="padding:4px 8px;">Fokus zwischen linkem und rechtem Baum wechseln</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+Z</b></td><td style="padding:4px 8px;">Rückgängig</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+Y</b></td><td style="padding:4px 8px;">Wiederherstellen</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+C</b></td><td style="padding:4px 8px;">Ausgewähltes Lesezeichen kopieren (Titel+URL in Zwischenablage)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Strg+V</b></td><td style="padding:4px 8px;">Lesezeichen aus Zwischenablage einfügen (erwartet eine URL, optional mit Titel)</td></tr>
</table>

<p>Bei Fragen oder Anregungen nutzen Sie bitte die „Über“-Funktion für Kontaktmöglichkeiten (sofern hinterlegt).</p>
""",
    "about_title":      "Über Bookmark-Organisator",
    "about_text":       "<b>Bookmark-Organisator</b><br>Version {version}<br><br>Ein Werkzeug zum Vergleichen und Zusammenführen von Lesezeichen.<br>© 2026 · Open Source",

    # Kontextmenü
    "ctx_open_in_browser": "Im Browser öffnen",
    "ctx_copy":            "Kopieren (Titel+URL)",
    "ctx_new_folder":      "Neuen Ordner anlegen",
    "ctx_rename":          "Umbenennen",
    "ctx_sort":            "Sortieren",
    "ctx_sort_title_asc":  "Nach Titel (A→Z)",
    "ctx_sort_title_desc": "Nach Titel (Z→A)",
    "ctx_sort_url_asc":    "Nach URL (A→Z)",
    "ctx_sort_url_desc":   "Nach URL (Z→A)",
    "ctx_find_duplicates": "Duplikate finden",
    "ctx_merge_duplicates":"Duplikate zusammenführen",
    "ctx_validate_item":   "Link prüfen",
    "ctx_validate_all":    "Tote Links prüfen (Seite)",
    "ctx_validate_selected": "Ausgewählte Links prüfen",
    "ctx_delete_dead":     "Toten Link löschen",
    "ctx_move_dead":       "Toten Link verschieben (Ungültig)",
    "ctx_delete":          "Löschen",

    # Suchoptionen
    "search_options_tip":  "Erweiterte Suchoptionen",
    "search_case_sensitive": "Groß-/Kleinschreibung beachten",
    "search_regex":        "Reguläre Ausdrücke verwenden",
    "search_path":         "Pfad durchsuchen",

    # Validierung
    "validation_progress":    "Lesezeichen werden geprüft …",
    "validation_cancel":      "Abbrechen",
    "validation_progress_text": "{done} von {total} geprüft",

    # ── NEU: Ausführliche Tooltips für Buttons ──────────────────────────────
    "btn_open_file_tip":      "Öffnet eine Lesezeichen-Datei (HTML, JSON, CSV, ADR, PLIST, URL) auf der linken Seite.",
    "btn_from_browser_tip":   "Erkennt installierte Browser und lädt deren Lesezeichen auf die aktuelle Seite.",
    "btn_save_left_tip":      "Speichert die linke Seite als Lesezeichen-Datei (JSON, CSV, HTML, ADR, URL).",
    "btn_save_right_tip":     "Speichert die rechte Seite als Lesezeichen-Datei (JSON, CSV, HTML, ADR, URL).",
    "btn_fullscreen_tip":     "Schaltet den Vollbildmodus um (blendet den Titel-Bereich aus).",
}