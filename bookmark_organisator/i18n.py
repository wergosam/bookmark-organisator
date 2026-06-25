# bookmark_organisator/i18n.py
"""Internationalisierung – Laden von Sprachmodulen."""

from pathlib import Path

AVAILABLE_LANGUAGES = {
    "Deutsch": "de",
    "English": "en",
    # Weitere Sprachen hier eintragen, z. B.:
    # "Français": "fr",
    # "Español":  "es",
}
DEFAULT_LANGUAGE = "de"


def load_language(code: str) -> dict:
    """Lädt das Sprachmodul aus locales/<code>.py und gibt das LANG-Dict zurück.
    Fällt bei Fehler auf Deutsch zurück."""
    try:
        base = Path(__file__).parent / "locales" / f"{code}.py"
        ns = {}
        exec(compile(base.read_text(encoding="utf-8"), str(base), "exec"), ns)
        return ns["LANG"]
    except Exception:
        if code != DEFAULT_LANGUAGE:
            return load_language(DEFAULT_LANGUAGE)
        raise