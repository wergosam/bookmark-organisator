# 🔖 Bookmark-Organisator

Ein leistungsstarker Desktop-Lesezeichen-Manager für Linux, gebaut mit Python und PyQt6. Er ermöglicht das Vergleichen, Zusammenführen, Validieren und Bearbeiten von Lesezeichen aus verschiedenen Browsern und Dateiformaten – alles in einer übersichtlichen Zwei-Panel-Ansicht.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green)
![Lizenz](https://img.shields.io/badge/Lizenz-GPL--3.0-blue)
![Plattform](https://img.shields.io/badge/Plattform-Linux-orange)

---

## ✨ Funktionen

### 📊 Zwei-Panel-Ansicht
- Zwei Lesezeichen-Sammlungen gleichzeitig anzeigen, vergleichen und bearbeiten
- **Drag & Drop** – Lesezeichen und Ordner per Maus verschieben – innerhalb einer Seite oder zwischen links und rechts (bei Seitenwechsel wird kopiert)
- **Inline-Bearbeitung** – Titel und URL direkt im Baum per Doppelklick bearbeiten
- **Ordnerzählung** – Neben jedem Ordner wird die Anzahl der enthaltenen Lesezeichen (rekursiv) angezeigt, z. B. `📁  Projekte (23)`

### 🌐 Browser-Import
- Direktes Laden aus **Firefox** (auch Flatpak/Snap), **Chromium**, **Google Chrome**, **Brave**, **Microsoft Edge**, **Vivaldi**, **Opera**, **Falkon** und weiteren
- Automatische Erkennung aller installierten Browser

### 📂 Datei-Import & Export
- **Import** – HTML (Netscape-Format), JSON, CSV, Opera ADR (`.adr`), Safari plist (`.plist`), Internet Explorer URL (`.url`)
- **Export** – HTML (Netscape-Format), JSON, CSV, Opera ADR (`.adr`), Internet Explorer URL (`.url`)
- **JSON-Format** – Enthält `path`, `title` und `url`

### 🔍 Lesezeichen validieren (tote Links)
- **Einzelnen Link prüfen** – Rechtsklick → „Link prüfen“
- **Mehrere Links gleichzeitig prüfen** – Mehrere Lesezeichen markieren → Rechtsklick → „Ausgewählte Links prüfen“
- **Gesamte Seite prüfen** – Rechtsklick auf leeren Bereich → „Tote Links prüfen (Seite)“
- **Status-Anzeige** – HTTP-Statuscodes in der „Status“-Spalte (z. B. `✅ 200`, `❌ 404`)
- **Tote Links behandeln** – Über Kontextmenü löschen oder in Ordner „Ungültig“ verschieben

### 🔄 Undo / Redo
- **Unbegrenzte Rückgängig-Funktion** (Strg+Z / Strg+Y)
- Alle Änderungen an Lesezeichen und Ordnern können rückgängig gemacht werden

### 🔎 Erweiterte Suche
- Echtzeitsuche in jeder Seite separat (Titel, URL, optional Pfad)
- **Erweiterte Optionen** (Zahnrad-Icon):
  - Groß-/Kleinschreibung beachten
  - Reguläre Ausdrücke (Regex)
  - Pfad durchsuchen

### 💾 Sitzungen speichern & laden
- Kompletten Zustand beider Seiten als `.bmo`-Datei speichern
- Sitzungen später wieder laden – inklusive aller Ordner, Lesezeichen und Historie
- Menü „Sitzung“ mit „Sitzung speichern…“ und „Sitzung laden…“

### 🪟 Fenstergröße speichern
- Automatisches Speichern der Fenstergröße beim Beenden
- Manuelles Speichern über Menü „Ansicht → Fenstergröße speichern“
- Zurücksetzen auf Standardgröße über „Ansicht → Fenstergröße zurücksetzen“

### ⛶ Vollbild-Modus
- Maximierte Ansicht für konzentriertes Arbeiten (F11 oder Button)

### 🎨 Benutzeroberfläche
- **Warmes Hell-Theme** – Angenehmes Cream-White/Orange-Design
- **Ausführliche Tooltips** – Alle Buttons haben hilfreiche Kurzinfos
- **Kontextmenü** – Schneller Zugriff auf alle Aktionen per Rechtsklick

### 💾 Speichern-Abfrage beim Beenden
- Verhindert ungewollten Datenverlust bei geänderten Seiten

---

## 📋 Voraussetzungen

- **Python** 3.10 oder neuer
- **PyQt6**

```bash
pip install PyQt6