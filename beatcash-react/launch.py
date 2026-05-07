#!/usr/bin/env python3
"""Beat Cash — wrapper PyWebView pour l'UI React + bridge Python."""
import json
import logging
import os
import sys
import threading
from pathlib import Path

import webview

# ─────────────────────────────────────────────────────────────────────
# PATHS & APPDIR
# ─────────────────────────────────────────────────────────────────────
def _appdir() -> Path:
    """Dossier de base : exe (PyInstaller) ou script."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.resolve().parent  # youtube-bot/

ROOT      = Path(__file__).parent.resolve()       # beatcash-react/
PROJECT   = _appdir()                              # youtube-bot/ ou exe dir
sys.path.insert(0, str(PROJECT))

# ─────────────────────────────────────────────────────────────────────
# LOGGING (beatcash.log à côté de l'exe)
# ─────────────────────────────────────────────────────────────────────
LOG_PATH = PROJECT / "beatcash.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("beatcash")

# ─────────────────────────────────────────────────────────────────────
# BETA MODE — force Pro + relax license check
# ─────────────────────────────────────────────────────────────────────
BETA = os.environ.get("BEATCASH_BETA", "") == "1" or (PROJECT / "BETA.flag").exists()

# ─────────────────────────────────────────────────────────────────────
# Lazy imports : on garde l'UI vivante même si une lib casse
# ─────────────────────────────────────────────────────────────────────
def _safe_import(name):
    try:
        mod = __import__(name)
        log.info("module %s chargé", name)
        return mod
    except Exception as e:
        log.warning("module %s indisponible : %s", name, e)
        return None

tiktok_mod    = _safe_import("tiktok")
license_mod   = _safe_import("license")
upload_mod    = _safe_import("upload")     # YouTube
instagram_mod = _safe_import("instagram")
seo_mod       = _safe_import("seo")


# ─────────────────────────────────────────────────────────────────────
# YT / IG state caches (en RAM tant que l'app tourne)
# ─────────────────────────────────────────────────────────────────────
_yt_service = None     # objet google api
_ig_client  = None     # instagrapi Client


# ─────────────────────────────────────────────────────────────────────
# BRIDGE JS ↔ PYTHON
# ─────────────────────────────────────────────────────────────────────
class Bridge:
    """Méthodes appelables depuis JS via `window.pywebview.api.<method>(...)`."""

    # ── Diagnostics ──────────────────────────────────────────────
    def ping(self) -> dict:
        return {"ok": True, "msg": "pong", "beta": BETA}

    def env(self) -> dict:
        return {
            "beta":         BETA,
            "log_path":     str(LOG_PATH),
            "modules": {
                "tiktok":    tiktok_mod is not None,
                "license":   license_mod is not None,
                "youtube":   upload_mod is not None,
                "instagram": instagram_mod is not None,
                "seo":       seo_mod is not None,
            },
        }

    # ── File picking ──────────────────────────────────────────────
    def select_file(self, kind: str = "video") -> str:
        from tkinter import Tk, filedialog
        root = Tk(); root.withdraw()
        types = {
            "video":  [("Vidéos", "*.mp4 *.mov *.avi *.mkv"), ("Tous", "*.*")],
            "audio":  [("Audio",  "*.mp3 *.wav *.aac *.flac"), ("Tous", "*.*")],
            "image":  [("Images", "*.jpg *.jpeg *.png *.webp"), ("Tous", "*.*")],
        }.get(kind, [("Tous", "*.*")])
        path = filedialog.askopenfilename(title="Choisir un fichier", filetypes=types)
        root.destroy()
        return path or ""

    # ── YOUTUBE ──────────────────────────────────────────────────
    def youtube_status(self) -> dict:
        global _yt_service
        if _yt_service:
            return {"connected": True}
        # Essaye de charger silencieusement le token existant
        if not upload_mod:
            return {"connected": False, "error": "module youtube indisponible"}
        try:
            token_file = PROJECT / "token.pickle"
            if token_file.exists():
                # On considère le token présent comme connecté (validation au moment du publish)
                return {"connected": True, "cached": True}
        except Exception as e:
            return {"connected": False, "error": str(e)}
        return {"connected": False}

    def connect_youtube(self) -> dict:
        global _yt_service
        if not upload_mod:
            return {"ok": False, "error": "module youtube indisponible"}
        try:
            log.info("YouTube : démarrage OAuth")
            _yt_service = upload_mod.get_authenticated_service()
            log.info("YouTube : connecté")
            return {"ok": True}
        except FileNotFoundError as e:
            return {"ok": False, "error": "client_secrets.json introuvable"}
        except Exception as e:
            log.exception("YouTube OAuth failed")
            return {"ok": False, "error": str(e)}

    def disconnect_youtube(self) -> dict:
        global _yt_service
        _yt_service = None
        token_file = PROJECT / "token.pickle"
        if token_file.exists():
            token_file.unlink()
        return {"ok": True}

    # ── INSTAGRAM ────────────────────────────────────────────────
    def instagram_status(self) -> dict:
        global _ig_client
        if _ig_client:
            return {"connected": True}
        sess = PROJECT / "instagram_session.json"
        return {"connected": sess.exists(), "cached": sess.exists()}

    def connect_instagram(self, login: str = "", password: str = "", code_2fa: str = "") -> dict:
        global _ig_client
        if not instagram_mod:
            return {"ok": False, "error": "module instagram indisponible"}
        if not login or not password:
            return {"ok": False, "error": "login/mot de passe requis"}
        try:
            log.info("Instagram : login %s", login)
            _ig_client = instagram_mod.login(login, password, code_2fa or None)
            log.info("Instagram : connecté")
            return {"ok": True}
        except Exception as e:
            log.exception("Instagram login failed")
            return {"ok": False, "error": str(e)}

    def disconnect_instagram(self) -> dict:
        global _ig_client
        if instagram_mod and _ig_client:
            try: instagram_mod.logout(_ig_client)
            except Exception: pass
        _ig_client = None
        sess = PROJECT / "instagram_session.json"
        if sess.exists(): sess.unlink()
        return {"ok": True}

    # ── TIKTOK ───────────────────────────────────────────────────
    def tiktok_status(self) -> dict:
        if not tiktok_mod:
            return {"connected": False, "error": "module tiktok indisponible"}
        sess = tiktok_mod.load_session(PROJECT)
        if not sess:
            return {"connected": False}
        return {
            "connected":  True,
            "expired":    tiktok_mod.is_token_expired(sess),
            "obtained":   sess.get("_obtained_at"),
            "expires_in": sess.get("expires_in"),
        }

    def connect_tiktok(self) -> dict:
        if not tiktok_mod:
            return {"ok": False, "error": "module tiktok indisponible"}
        ck = os.environ.get("TIKTOK_CLIENT_KEY", "")
        cs = os.environ.get("TIKTOK_CLIENT_SECRET", "")
        if not ck or not cs:
            return {
                "ok":    False,
                "error": "TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET manquants (.env)"
            }
        try:
            log.info("TikTok : démarrage OAuth")
            tok = tiktok_mod.oauth_login(ck, cs)
            tiktok_mod.save_session(tok, PROJECT)
            log.info("TikTok : connecté")
            return {"ok": True}
        except Exception as e:
            log.exception("TikTok OAuth failed")
            return {"ok": False, "error": str(e)}

    # alias pour compat avec la version précédente du bridge
    def tiktok_connect(self):    return self.connect_tiktok()
    def tiktok_disconnect(self): return self._tiktok_disconnect()
    def _tiktok_disconnect(self) -> dict:
        if tiktok_mod: tiktok_mod.disconnect(PROJECT)
        return {"ok": True}

    # ── PUBLISH (orchestré) ──────────────────────────────────────
    def publish(self, opts: dict) -> dict:
        """opts = {file, title, description, targets:[...], yt_privacy?, ...}

        Retourne {ok, results:{youtube?, instagram?, tiktok?}} où chaque
        sous-résultat est {ok, url?, id?, error?}.
        """
        global _yt_service, _ig_client
        opts = opts or {}
        file_path = opts.get("file") or ""
        title     = opts.get("title") or "Untitled beat"
        targets   = opts.get("targets") or []
        log.info("publish() target=%s file=%s", targets, file_path)

        if not file_path or not Path(file_path).exists():
            return {"ok": False, "error": f"fichier introuvable : {file_path}"}

        results = {}

        # ── YouTube ──
        if "youtube" in targets and upload_mod:
            try:
                if not _yt_service:
                    _yt_service = upload_mod.get_authenticated_service()
                vid = upload_mod.upload_video(
                    _yt_service,
                    Path(file_path),
                    title=title,
                    description=opts.get("description", ""),
                    privacy=opts.get("yt_privacy", "public"),
                )
                video_id = vid.get("id") if isinstance(vid, dict) else vid
                results["youtube"] = {
                    "ok": True, "id": video_id,
                    "url": f"https://youtube.com/watch?v={video_id}" if video_id else None,
                }
            except Exception as e:
                log.exception("YouTube publish failed")
                results["youtube"] = {"ok": False, "error": str(e)}

        # ── Instagram ──
        if "instagram" in targets and instagram_mod:
            try:
                if not _ig_client:
                    raise RuntimeError("Instagram non connecté — connecte-toi d'abord")
                media = instagram_mod.upload_reel(
                    _ig_client,
                    Path(file_path),
                    caption=opts.get("ig_caption", title),
                )
                results["instagram"] = {
                    "ok": True,
                    "id":  getattr(media, "pk", None) or getattr(media, "id", None),
                    "url": getattr(media, "code", None) and f"https://instagram.com/reel/{media.code}",
                }
            except Exception as e:
                log.exception("Instagram publish failed")
                results["instagram"] = {"ok": False, "error": str(e)}

        # ── TikTok ──
        if "tiktok" in targets and tiktok_mod:
            try:
                res = tiktok_mod.quick_publish(file_path, title, base=PROJECT,
                                               privacy=opts.get("tt_privacy", "PUBLIC_TO_EVERYONE"))
                results["tiktok"] = {"ok": True, **res}
            except Exception as e:
                log.exception("TikTok publish failed")
                results["tiktok"] = {"ok": False, "error": str(e)}

        return {"ok": True, "results": results}

    # ── License ──────────────────────────────────────────────────
    def license_status(self) -> dict:
        if BETA:
            return {"plan": "PRO", "key": "BETA-MODE", "valid_until": None,
                    "online": True, "needs_recheck": False, "beta": True}
        if not license_mod:
            return {"plan": "FREE", "error": "module license indisponible"}
        return license_mod.status(PROJECT)

    def license_activate(self, key: str) -> dict:
        if BETA:
            return {"ok": True, "plan": "PRO", "key": "BETA-MODE", "beta": True}
        if not license_mod:
            return {"ok": False, "error": "module license indisponible"}
        try:
            st = license_mod.activate(key.strip().upper(), PROJECT)
            return {"ok": True, **st}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def license_recheck(self) -> dict:
        if BETA: return self.license_status()
        if not license_mod: return {"plan": "FREE"}
        return license_mod.recheck(PROJECT)

    def license_deactivate(self) -> dict:
        if license_mod: license_mod.deactivate(PROJECT)
        return {"ok": True}

    def is_pro(self) -> bool:
        if BETA:
            return True
        return bool(license_mod and license_mod.is_pro(PROJECT))

    # ── Stub legacy ─────────────────────────────────────────────
    def tiktok_publish(self, file_path: str, title: str, **opts) -> dict:
        return self.publish({"file": file_path, "title": title, "targets": ["tiktok"], **opts})


# ─────────────────────────────────────────────────────────────────────
# .env loader (sans dotenv)
# ─────────────────────────────────────────────────────────────────────
def _load_env():
    for candidate in (PROJECT / ".env", ROOT / ".env"):
        if not candidate.exists():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)


def _resolve_dist_dir() -> Path:
    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS", ""))
        for c in (meipass / "dist", Path(sys.executable).parent / "dist"):
            if (c / "index.html").exists():
                return c
    return ROOT / "dist"


def main():
    _load_env()
    log.info("Beat Cash starting · BETA=%s · project=%s", BETA, PROJECT)
    dist = _resolve_dist_dir()
    index = dist / "index.html"
    if not index.exists():
        print(
            f"[ERROR] index.html introuvable dans {dist}. Build d'abord :\n  npm run build",
            file=sys.stderr,
        )
        sys.exit(1)
    title = "$ BEATCASH" + ("  ·  BETA" if BETA else "")
    webview.create_window(
        title=title,
        url=str(index),
        width=1280, height=860,
        min_size=(960, 680),
        background_color="#000000",
        js_api=Bridge(),
    )
    webview.start(debug=False, http_server=True)


if __name__ == "__main__":
    main()
