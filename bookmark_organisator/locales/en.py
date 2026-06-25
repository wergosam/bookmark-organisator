# locales/en.py – English translations
LANG = {
    # Window & Header
    "window_title":     "Bookmark Organiser",
    "app_title":        "🔖  Bookmark Organiser",
    "app_subtitle":     "Compare & merge bookmarks from files or browsers",

    # Toolbar buttons
    "btn_open_file":    "Open file",
    "btn_new_empty":    "New/Empty",
    "btn_new_empty_tip":"Create an empty list – start collecting bookmarks from scratch",
    "btn_from_browser": "From browser  ▾",

    # Centre buttons (tooltips)
    "tip_delete_both":  "Delete selected items/folders on both sides",
    "tip_undo":         "Undo (Ctrl+Z)",
    "tip_redo":         "Redo (Ctrl+Y)",

    # Bottom bar
    "btn_save_left":    "💾  Save left",
    "btn_save_right":   "💾  Save right",
    "btn_fullscreen":   "⛶  Fullscreen",
    "btn_fullscreen_exit": "✕  Exit fullscreen",
    "entries":          "{n} entries",

    # Tree
    "col_title":        "Title",
    "col_url":          "URL",
    "col_status":       "Status",
    "search_placeholder": "Search …",
    "tree_tooltip":     ("Tip: double-click to edit title/URL · drag bookmarks "
                         "or folders between sides or to reorder within a side."),

    # Status bar
    "status_loaded":    "✓  {n} bookmarks loaded from «{label}»",
    "status_saved":     "✓  Saved: {path}",
    "status_empty_created": "✓  Empty list created – drag or copy bookmarks here",
    "status_undo":      "↶  Undone",
    "status_redo":      "↷  Redone",
    "status_deleted":   "🗑  {n} item(s) deleted  ·  «↶» to undo",
    "status_no_selection": "Please select items or folders first.",
    "status_no_bookmarks": "No bookmarks found in {label}.",
    "status_self_drop": "A folder cannot be moved into itself.",
    "status_copied":    "✓  Copied to clipboard",
    "status_sorted":    "✓  Sorted",
    "status_merged":    "✓  {removed} duplicates removed",
    "status_validation_start": "⏳  Checking bookmarks …",
    "status_validation_done":  "✓  {checked} links checked",
    "status_validation_running": "Validation already running …",
    "status_no_bookmarks_validate": "No bookmarks to check.",
    "status_moved_dead":      "✓  Dead link moved",
    "status_geometry_saved":  "✓  Window size saved",
    "status_geometry_reset":  "✓  Window size reset",
    "status_paste_empty":     "Clipboard is empty.",
    "status_paste_no_url":    "No valid URL found in clipboard.",
    "status_pasted":          "✓  Bookmark pasted",

    # ── NEW: Session status ──────────────────────────────────────────────────
    "status_session_saved":   "✓  Session saved: {path}",
    "status_session_loaded":  "✓  Session loaded: {path}",

    # Dialogs
    "dlg_open_title":   "Open bookmark file",
    "dlg_open_filter":  "Bookmarks (*.html *.json *.csv *.adr *.plist *.url);;All files (*)",
    "dlg_save_title":   "Save as",
    "dlg_save_default": "bookmarks_{side}_{ts}.json",
    "dlg_save_filter":  "JSON (*.json);;CSV (*.csv);;HTML (*.html);;Opera ADR (*.adr);;IE URL (*.url)",

    "dlg_new_empty_title": "New empty list",
    "dlg_new_empty_text":  ("The current side contains entries. Really clear it and "
                            "start a new, empty list?"),
    "new_file_label":   "📄  (new file)",

    "dlg_save_empty_title": "Empty",
    "dlg_save_empty_text":  "No entries to save.",

    "dlg_close_title":  "Save before quitting?",
    "dlg_close_text":   ("The {side_label} side «{base}» has unsaved changes.\n"
                         "Save changes?"),
    "dlg_close_save":   "Save …",
    "dlg_close_discard":"Discard",
    "dlg_close_cancel": "Cancel",
    "side_label_left":  "left",
    "side_label_right": "right",

    "dlg_error_load":   "Could not load file:\n{err}",
    "dlg_error_browser":"Could not load bookmarks from {label}:\n{err}",
    "dlg_error_title":  "Error",

    "dlg_new_folder_title": "Create new folder",
    "dlg_new_folder_label": "Folder name:",
    "dlg_rename_title":     "Rename folder",
    "dlg_rename_label":     "New name:",

    "dlg_duplicates_title":   "Duplicates found",
    "dlg_duplicates_found":   "Found {count} groups of duplicates.",
    "dlg_no_duplicates_title":"No duplicates",
    "dlg_no_duplicates_text": "No duplicate bookmarks found.",

    "dlg_delete_dead_title":  "Delete dead link?",
    "dlg_delete_dead_text":   "Really delete dead link «{title}»?",

    # ── NEW: Session dialogs ─────────────────────────────────────────────────
    "dlg_session_save_title": "Save session",
    "dlg_session_save_filter":"Bookmark session (*.bmo)",
    "dlg_session_load_title": "Load session",
    "dlg_session_load_filter":"Bookmark session (*.bmo)",
    "dlg_error_session_save": "Could not save session:\n{err}",
    "dlg_error_session_load": "Could not load session:\n{err}",

    # Browser menu
    "browser_none":     "No browser with bookmarks found",
    "browser_icon":     "🌐  {label}",

    # Firefox folder names
    "ff_menu":          "Bookmarks Menu",
    "ff_toolbar":       "Bookmarks Toolbar",
    "ff_unsorted":      "Unsorted Bookmarks",
    "ff_mobile":        "Mobile Bookmarks",
    "ff_no_name":       "(no name)",

    # Chromium folder names
    "cr_toolbar":       "Bookmarks Bar",
    "cr_menu":          "Bookmarks Menu",
    "cr_other":         "Other Bookmarks",
    "cr_mobile":        "Mobile Bookmarks",

    # HTML export
    "html_title":       "Bookmarks",
    "html_h1":          "Bookmarks Menu",

    # JSON errors
    "err_json":         ("JSON must be a list of bookmark objects "
                         "or a browser export file."),
    "err_format":       "Unsupported file format.",

    # Menus
    "menu_language":    "Sprache / Language",
    "menu_view":        "View",
    "menu_save_geometry": "Save window size",
    "menu_reset_geometry": "Reset window size",
    "menu_help":        "Help",
    "menu_help_manual": "User Manual",
    "menu_about":       "About",

    # ── NEW: Session menu ────────────────────────────────────────────────────
    "menu_session":           "Session",
    "menu_session_save":      "Save session…",
    "menu_session_load":      "Load session…",

    # Help / About
    "manual_title":     "User Manual – Bookmark Organiser",
    "manual_close":     "Close",
    "manual_text": """
<h2>Bookmark Organiser – User Manual</h2>

<p>This tool allows you to load bookmarks from various sources, compare, organise and export them in many formats. The interface is split into two independent panels (left / right) – each side can be filled and edited separately.</p>

<h3>📂  Loading bookmarks</h3>
<ul>
  <li><b>Open file</b> – Supported formats: <code>.json</code> (Chromium, Firefox new, own list), <code>.csv</code>, <code>.html</code> (Netscape format), <code>.adr</code> (Opera old), <code>.plist</code> (Safari) and <code>.url</code> (Internet Explorer).</li>
  <li><b>New / Empty</b> – creates an empty list on the current side.</li>
  <li><b>From browser ▾</b> – automatically detects installed browsers (Firefox, Chrome, Brave, Edge, Vivaldi, Opera, Falkon etc.) and loads their bookmarks.</li>
</ul>

<h3>✏️  Editing & Organising</h3>
<ul>
  <li><b>Drag & Drop</b> – drag bookmarks or entire folders with your mouse. You can reorder items within a side or <i>copy</i> them between sides (or <i>move</i> within the same side).</li>
  <li><b>Double‑click</b> – on a title or URL to edit it directly in the list.</li>
  <li><b>Delete</b> – select items and click the <b>🗑</b> button in the centre. They are removed from both sides simultaneously.</li>
  <li><b>Search</b> – above each list you can filter by title, URL or (optionally) path. The gear icon provides advanced options like case sensitivity and regular expressions.</li>
  <li><b>Context menu (right‑click)</b> – provides quick access to: Open in browser, Copy, Create/rename folder, Sort (by title/URL), Find/merge duplicates, Validate bookmarks (check link) and Delete.</li>
</ul>

<h3>🔍  Validating bookmarks (dead links)</h3>
<ul>
  <li><b>Check a single link</b> – right‑click on a bookmark → „Check link“. The HTTP status code appears in the „Status“ column.</li>
  <li><b>Check multiple links at once</b> – select several bookmarks (with <b>Ctrl</b> or <b>Shift</b>), then right‑click → „Check selected links“.</li>
  <li><b>Check entire side</b> – right‑click on empty space or a folder → „Check for dead links (page)“. A progress dialog shows the status.</li>
  <li><b>Handle dead links</b> – after validation, you can delete individual dead links or move them to the „Invalid“ folder via the context menu.</li>
  <li>The Status column displays <b>✅ 200</b> for valid, <b>❌ 404</b> for erroneous, and <b>❌ Error</b> for unreachable links. Rows are colour‑coded.</li>
</ul>

<h3>↶  Undo / Redo</h3>
<ul>
  <li>The <b>↶</b> (Undo) and <b>↷</b> (Redo) buttons in the centre let you step back or forward through your changes.</li>
  <li>Keyboard shortcuts: <b>Ctrl+Z</b> (Undo) and <b>Ctrl+Y</b> (Redo).</li>
</ul>

<h3>💾  Saving & Exporting</h3>
<ul>
  <li>Below each side there is a <b>„Save“</b> button. You can export the current side as <b>JSON</b>, <b>CSV</b>, <b>HTML</b> (Netscape format), <b>Opera ADR</b> or <b>IE URL</b>.</li>
  <li>Modified sides are marked with a <b>●</b> before the file name.</li>
</ul>

<h3>⛶  Fullscreen</h3>
<ul>
  <li>The <b>⛶ Fullscreen</b> button at the bottom hides the header area and maximises the window – ideal for large lists. Use <b>F11</b> as shortcut.</li>
</ul>

<h3>🌐  Changing language</h3>
<ul>
  <li>Use the <b>Sprache / Language</b> menu to switch between German and English. The setting is saved.</li>
</ul>

<h3>🪟  Save window size</h3>
<ul>
  <li>The <b>View</b> menu offers two actions: <b>Save window size</b> (stores current position and size) and <b>Reset window size</b> (restores default 1300×750). The size is automatically saved when you close the application.</li>
</ul>

<h3>💾  Saving & loading sessions</h3>
<ul>
  <li>In the <b>Session</b> menu you can save the complete state of both sides as a <b>.bmo</b> file and reload it later – including all folders, bookmarks and the current edit history.</li>
</ul>

<h3>📊  Folder counts</h3>
<ul>
  <li>Next to each folder, the number of contained bookmarks (recursively, i.e. including all subfolders) is shown in parentheses, e.g. <b>📁  Projects (23)</b>. The count is automatically updated on every change.</li>
</ul>

<h3>⌨️  All keyboard shortcuts</h3>
<table style="border-collapse:collapse; width:100%;">
  <tr><th style="text-align:left; padding:4px 8px;">Shortcut</th><th style="text-align:left; padding:4px 8px;">Function</th></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+O</b></td><td style="padding:4px 8px;">Open file (left)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+Shift+O</b></td><td style="padding:4px 8px;">Open file (right)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+S</b></td><td style="padding:4px 8px;">Save (left)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+Shift+S</b></td><td style="padding:4px 8px;">Save (right)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+N</b></td><td style="padding:4px 8px;">New/Empty (left)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+Shift+N</b></td><td style="padding:4px 8px;">New/Empty (right)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+B</b></td><td style="padding:4px 8px;">Load browser (left)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+Shift+B</b></td><td style="padding:4px 8px;">Load browser (right)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Del</b></td><td style="padding:4px 8px;">Delete selection (both sides)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+F</b></td><td style="padding:4px 8px;">Focus search field (active side)</td></tr>
  <tr><td style="padding:4px 8px;"><b>F11</b></td><td style="padding:4px 8px;">Toggle fullscreen</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+Tab</b></td><td style="padding:4px 8px;">Switch focus between left and right tree</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+Z</b></td><td style="padding:4px 8px;">Undo</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+Y</b></td><td style="padding:4px 8px;">Redo</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+C</b></td><td style="padding:4px 8px;">Copy selected bookmark (Title+URL to clipboard)</td></tr>
  <tr><td style="padding:4px 8px;"><b>Ctrl+V</b></td><td style="padding:4px 8px;">Paste bookmark from clipboard (expects a URL, optional with title)</td></tr>
</table>

<p>For questions or suggestions, please use the „About“ function for contact details (if provided).</p>
""",
    "about_title":      "About Bookmark Organiser",
    "about_text":       "<b>Bookmark Organiser</b><br>Version {version}<br><br>A tool to compare and merge bookmarks.<br>© 2026 · Open Source",

    # Context menu
    "ctx_open_in_browser": "Open in browser",
    "ctx_copy":            "Copy (Title+URL)",
    "ctx_new_folder":      "Create new folder",
    "ctx_rename":          "Rename",
    "ctx_sort":            "Sort",
    "ctx_sort_title_asc":  "By title (A→Z)",
    "ctx_sort_title_desc": "By title (Z→A)",
    "ctx_sort_url_asc":    "By URL (A→Z)",
    "ctx_sort_url_desc":   "By URL (Z→A)",
    "ctx_find_duplicates": "Find duplicates",
    "ctx_merge_duplicates":"Merge duplicates",
    "ctx_validate_item":   "Check link",
    "ctx_validate_all":    "Check for dead links (page)",
    "ctx_validate_selected": "Check selected links",
    "ctx_delete_dead":     "Delete dead link",
    "ctx_move_dead":       "Move dead link (to Invalid)",
    "ctx_delete":          "Delete",

    # Search options
    "search_options_tip":  "Advanced search options",
    "search_case_sensitive": "Case sensitive",
    "search_regex":        "Use regular expressions",
    "search_path":         "Search path",

    # Validation
    "validation_progress":    "Checking bookmarks …",
    "validation_cancel":      "Cancel",
    "validation_progress_text": "{done} of {total} checked",

    # ── NEW: Extended tooltips ──────────────────────────────────────────────
    "btn_open_file_tip":      "Opens a bookmark file (HTML, JSON, CSV, ADR, PLIST, URL) on the left side.",
    "btn_from_browser_tip":   "Detects installed browsers and loads their bookmarks to the current side.",
    "btn_save_left_tip":      "Saves the left side as a bookmark file (JSON, CSV, HTML, ADR, URL).",
    "btn_save_right_tip":     "Saves the right side as a bookmark file (JSON, CSV, HTML, ADR, URL).",
    "btn_fullscreen_tip":     "Toggles fullscreen mode (hides the title area).",
}