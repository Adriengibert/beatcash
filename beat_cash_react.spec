# -*- mode: python ; coding: utf-8 -*-
"""Beat Cash React — PyInstaller spec
Entry : beatcash-react/launch.py (PyWebView + bridge Python)
Bundle : dist/ React build, tiktok.py, license.py, instagram.py, seo.py, upload.py, fonts/

Build : python -m PyInstaller beat_cash_react.spec --noconfirm
Sortie : dist/BeatCashReact/BeatCashReact.exe (mode --onedir)
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_all

ROOT      = Path(SPECPATH)
REACT_DIR = ROOT / "beatcash-react"
ENTRY     = REACT_DIR / "launch.py"

block_cipher = None

# ── Collecte paquets complexes ──────────────────────────────────────
datas, binaries, hiddenimports = [], [], []

for pkg in (
    "webview",          # PyWebView
    "clr_loader",       # pythonnet
    "imageio_ffmpeg",
    "tkinterdnd2",
    "instagrapi",
    "google",
    "googleapiclient",
    "google_auth_oauthlib",
    "google_auth_httplib2",
    "anthropic",
    "httpx", "httpcore",
    "PIL",
    "requests", "urllib3", "certifi", "charset_normalizer",
):
    try:
        d, b, h = collect_all(pkg)
        datas        += d
        binaries     += b
        hiddenimports += h
    except Exception as e:
        print(f"[WARN] collect_all({pkg}) : {e}")

# ── Modules Python du backend (à côté de launch.py) ─────────────────
for mod in ("tiktok.py", "license.py", "instagram.py", "seo.py", "upload.py"):
    src = ROOT / mod
    if src.exists():
        datas.append((str(src), "."))
    else:
        print(f"[WARN] backend module manquant : {mod}")

# ── React build (HTML/CSS/JS) ──────────────────────────────────────
dist_dir = REACT_DIR / "dist"
if dist_dir.exists():
    datas.append((str(dist_dir), "dist"))
else:
    raise SystemExit(
        "[ERROR] beatcash-react/dist/ introuvable. Build d'abord :\n"
        "    cd beatcash-react && npm run build"
    )

# ── Fonts custom ────────────────────────────────────────────────────
fonts_dir = ROOT / "fonts"
if fonts_dir.exists():
    datas.append((str(fonts_dir), "fonts"))

# ── Analyse ─────────────────────────────────────────────────────────
a = Analysis(
    [str(ENTRY)],
    pathex=[str(ROOT), str(REACT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + [
        "tiktok", "license", "instagram", "seo", "upload",
        "webview", "webview.platforms.winforms", "webview.platforms.edgechromium",
        "clr_loader",
        "tkinter", "tkinter.filedialog", "tkinter.messagebox",
        "json", "pathlib", "subprocess", "threading",
        "requests", "requests.adapters",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["matplotlib", "numpy", "pandas", "scipy", "PyQt5", "PyQt6", "wx"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BeatCashReact",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(ROOT / "beat_cash.ico") if (ROOT / "beat_cash.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="BeatCashReact",
)
