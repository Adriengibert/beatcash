#!/usr/bin/env python3
"""POC BeatCash — UI web wrappée dans PyWebView."""
import sys
from pathlib import Path
import webview


class Bridge:
    """Pont JS ↔ Python — ici stub, à remplir au moment de la migration réelle."""

    def select_file(self):
        from tkinter import Tk, filedialog
        root = Tk(); root.withdraw()
        path = filedialog.askopenfilename(
            title="Choisir un fichier",
            filetypes=[("Vidéos", "*.mp4 *.mov *.avi *.mkv"),
                       ("Audio", "*.mp3 *.wav *.aac *.flac"),
                       ("Tous", "*.*")])
        root.destroy()
        return path or ""

    def ping(self):
        return {"ok": True, "msg": "pong from python"}


def main():
    here = Path(__file__).parent.resolve()
    html = here / "index.html"
    if not html.exists():
        print(f"[ERROR] {html} introuvable", file=sys.stderr)
        sys.exit(1)

    window = webview.create_window(
        title="$ BEATCASH",
        url=str(html),
        width=1200, height=820,
        min_size=(900, 640),
        background_color="#0F172A",
        js_api=Bridge(),
        frameless=False,
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
