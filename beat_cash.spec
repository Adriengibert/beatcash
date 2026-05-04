# -*- mode: python ; coding: utf-8 -*-
"""
Beat Cash — PyInstaller spec
Génère : dist/BeatCash/BeatCash.exe  (mode --onedir, plus stable)
"""

from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# ── Collecte des paquets complexes ──────────────────────────────────────
datas      = []
binaries   = []
hiddenimports = []

for pkg in (
    "imageio_ffmpeg",   # inclut le binaire ffmpeg
    "tkinterdnd2",      # inclut les DLL TkDnD
    "instagrapi",       # très modulaire, tout collecter
    "google",           # google-auth
    "googleapiclient",  # google-api-python-client
    "google_auth_oauthlib",
    "google_auth_httplib2",
    "anthropic",        # IA SEO (optionnel mais inclus)
    "httpx",            # dépendance anthropic
    "httpcore",
    "PIL",              # Pillow
):
    try:
        d, b, h = collect_all(pkg)
        datas        += d
        binaries     += b
        hiddenimports += h
    except Exception as e:
        print(f"[WARN] collect_all({pkg}) : {e}")

# ── Analyse ─────────────────────────────────────────────────────────────
a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + [
        "pickle", "threading", "subprocess", "tempfile",
        "tkinter", "tkinter.ttk", "tkinter.filedialog",
        "tkinter.messagebox", "pathlib", "json", "re",
        "email", "email.mime", "email.mime.text",
        "certifi", "charset_normalizer", "urllib3",
        "cryptography", "cryptography.hazmat",
        "requests", "requests.adapters",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["matplotlib", "numpy", "pandas", "scipy",
              "PyQt5", "PyQt6", "wx"],   # exclure l'inutile
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BeatCash",
    debug=False,
    strip=False,
    upx=False,          # upx=False évite les faux positifs antivirus
    console=False,      # pas de fenêtre console
    icon="beat_cash.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="BeatCash",
)
