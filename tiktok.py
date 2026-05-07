"""TikTok Content Posting API — module Beat Cash.

Doc API : https://developers.tiktok.com/doc/content-posting-api-get-started

Flow :
    1. OAuth 2.0 (scopes: user.info.basic, video.publish)
    2. Upload init (FILE_UPLOAD) → renvoie publish_id + upload_url
    3. PUT chunks vidéo sur upload_url
    4. Poll status jusqu'à PUBLISH_COMPLETE / FAILED

Stockage du token : tiktok_session.json (à côté de l'exe / app.py).
"""
from __future__ import annotations

import json
import os
import secrets
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from typing import Callable, Optional

import requests

# ── Constants ─────────────────────────────────────────────────────────
AUTH_URL          = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL         = "https://open.tiktokapis.com/v2/oauth/token/"
INIT_URL          = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_URL        = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
USERINFO_URL      = "https://open.tiktokapis.com/v2/user/info/"
SCOPES            = "user.info.basic,video.publish,video.upload"
LOCAL_PORT        = 4123
REDIRECT_URI      = f"http://localhost:{LOCAL_PORT}/callback"
CHUNK_MIN         = 5 * 1024 * 1024     # 5 Mo par chunk (min imposé)
CHUNK_MAX         = 64 * 1024 * 1024    # 64 Mo
SESSION_FILE_NAME = "tiktok_session.json"


def _session_path(base: Optional[Path] = None) -> Path:
    return (base or Path.cwd()) / SESSION_FILE_NAME


# ─────────────────────────────────────────────────────────────────────
# OAUTH
# ─────────────────────────────────────────────────────────────────────
class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Capture le `code=` retourné par TikTok après authorize."""
    captured: dict = {}

    def do_GET(self):                                # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404); self.end_headers(); return
        params = urllib.parse.parse_qs(parsed.query)
        _OAuthCallbackHandler.captured = {k: v[0] for k, v in params.items()}
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"<!doctype html><html><body style='font-family:system-ui;"
            b"background:#000;color:#fff;display:grid;place-items:center;height:100vh;'>"
            b"<div><h2>OK \xe2\x9c\x93</h2><p>Tu peux fermer cet onglet.</p></div>"
            b"</body></html>"
        )

    def log_message(self, *_): pass  # silence


def oauth_login(
    client_key: str,
    client_secret: str,
    on_progress: Optional[Callable[[str], None]] = None,
) -> dict:
    """Lance le flow OAuth dans le navigateur, attend le code, échange contre access_token.

    Retourne : {access_token, refresh_token, expires_in, open_id, scope, token_type}
    """
    if not client_key or not client_secret:
        raise RuntimeError("TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET manquants dans .env")

    state = secrets.token_urlsafe(16)
    auth_qs = urllib.parse.urlencode({
        "client_key":    client_key,
        "scope":         SCOPES,
        "response_type": "code",
        "redirect_uri":  REDIRECT_URI,
        "state":         state,
    })
    on_progress and on_progress("Ouverture du navigateur…")

    server = HTTPServer(("127.0.0.1", LOCAL_PORT), _OAuthCallbackHandler)
    Thread(target=server.handle_request, daemon=True).start()
    webbrowser.open(f"{AUTH_URL}?{auth_qs}")

    # Attend ~120s max
    deadline = time.time() + 120
    while time.time() < deadline and not _OAuthCallbackHandler.captured:
        time.sleep(0.3)
    captured = _OAuthCallbackHandler.captured
    _OAuthCallbackHandler.captured = {}

    if "error" in captured:
        raise RuntimeError(f"OAuth refusé : {captured.get('error_description', captured['error'])}")
    if captured.get("state") != state:
        raise RuntimeError("OAuth : state mismatch (session compromise possible)")
    code = captured.get("code")
    if not code:
        raise RuntimeError("OAuth : pas de code reçu (timeout ou refus)")

    on_progress and on_progress("Échange du code contre un token…")
    r = requests.post(TOKEN_URL, data={
        "client_key":    client_key,
        "client_secret": client_secret,
        "code":          code,
        "grant_type":    "authorization_code",
        "redirect_uri":  REDIRECT_URI,
    }, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=20)

    if r.status_code != 200:
        raise RuntimeError(f"Token exchange échoué [{r.status_code}] : {r.text[:300]}")
    tok = r.json()
    if "access_token" not in tok:
        raise RuntimeError(f"Token invalide : {tok}")
    tok["_obtained_at"] = int(time.time())
    return tok


def refresh_token(client_key: str, client_secret: str, refresh_tok: str) -> dict:
    r = requests.post(TOKEN_URL, data={
        "client_key":    client_key,
        "client_secret": client_secret,
        "grant_type":    "refresh_token",
        "refresh_token": refresh_tok,
    }, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"Refresh échoué : {r.text[:300]}")
    tok = r.json()
    tok["_obtained_at"] = int(time.time())
    return tok


# ─────────────────────────────────────────────────────────────────────
# SESSION
# ─────────────────────────────────────────────────────────────────────
def save_session(tok: dict, base: Optional[Path] = None) -> Path:
    p = _session_path(base)
    p.write_text(json.dumps(tok, indent=2), encoding="utf-8")
    return p


def load_session(base: Optional[Path] = None) -> Optional[dict]:
    p = _session_path(base)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def is_token_expired(tok: dict, margin: int = 300) -> bool:
    obtained = tok.get("_obtained_at", 0)
    expires  = tok.get("expires_in", 0)
    return (obtained + expires - margin) < int(time.time())


def get_valid_token(client_key: str, client_secret: str, base: Optional[Path] = None) -> str:
    """Retourne un access_token valide (refresh si nécessaire). Lève si pas de session."""
    tok = load_session(base)
    if not tok:
        raise RuntimeError("Pas de session TikTok. Lance la connexion d'abord.")
    if is_token_expired(tok):
        refreshed = refresh_token(client_key, client_secret, tok["refresh_token"])
        # Préserve refresh_token si TikTok n'en renvoie pas un nouveau
        refreshed.setdefault("refresh_token", tok["refresh_token"])
        save_session(refreshed, base)
        return refreshed["access_token"]
    return tok["access_token"]


def get_user_info(access_token: str) -> dict:
    r = requests.get(USERINFO_URL,
                     params={"fields": "open_id,union_id,avatar_url,display_name"},
                     headers={"Authorization": f"Bearer {access_token}"},
                     timeout=15)
    return r.json()


# ─────────────────────────────────────────────────────────────────────
# UPLOAD VIDEO (FILE_UPLOAD)
# ─────────────────────────────────────────────────────────────────────
def _pick_chunk_size(file_size: int) -> tuple[int, int]:
    """Retourne (chunk_size, total_chunk_count) selon les contraintes TikTok."""
    if file_size <= CHUNK_MIN:
        return file_size, 1
    chunk = min(max(CHUNK_MIN, file_size // 10), CHUNK_MAX)
    total = (file_size + chunk - 1) // chunk
    if total > 1000:                # limite TikTok
        chunk = (file_size + 999) // 1000
        total = (file_size + chunk - 1) // chunk
    return chunk, total


def upload_video(
    access_token: str,
    file_path: str | Path,
    title: str,
    *,
    privacy: str = "PUBLIC_TO_EVERYONE",   # MUTUAL_FOLLOW_FRIENDS | SELF_ONLY
    disable_duet: bool = False,
    disable_comment: bool = False,
    disable_stitch: bool = False,
    on_progress: Optional[Callable[[float], None]] = None,
) -> dict:
    """Upload une vidéo locale sur TikTok et attend le statut final.

    Retourne : {"publish_id": str, "status": str, "share_url": str|None}
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    file_size = file_path.stat().st_size
    chunk_size, total_chunks = _pick_chunk_size(file_size)

    init_body = {
        "post_info": {
            "title":            title[:2200],   # max 2200 char
            "privacy_level":    privacy,
            "disable_duet":     disable_duet,
            "disable_comment":  disable_comment,
            "disable_stitch":   disable_stitch,
        },
        "source_info": {
            "source":             "FILE_UPLOAD",
            "video_size":         file_size,
            "chunk_size":         chunk_size,
            "total_chunk_count":  total_chunks,
        },
    }

    r = requests.post(
        INIT_URL,
        json=init_body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json; charset=UTF-8",
        },
        timeout=20,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Init échoué [{r.status_code}] : {r.text[:300]}")
    init = r.json()
    data = init.get("data") or {}
    publish_id = data.get("publish_id")
    upload_url = data.get("upload_url")
    if not publish_id or not upload_url:
        raise RuntimeError(f"Init renvoie incomplet : {init}")

    # ── Upload chunks ─────────────────────────────────────────────
    with open(file_path, "rb") as f:
        for idx in range(total_chunks):
            start = idx * chunk_size
            end = min(start + chunk_size, file_size) - 1
            f.seek(start)
            buf = f.read(end - start + 1)
            up = requests.put(
                upload_url,
                data=buf,
                headers={
                    "Content-Type":   "video/mp4",
                    "Content-Length": str(len(buf)),
                    "Content-Range":  f"bytes {start}-{end}/{file_size}",
                },
                timeout=300,
            )
            if up.status_code not in (200, 201, 206):
                raise RuntimeError(
                    f"Chunk {idx + 1}/{total_chunks} échoué [{up.status_code}] : {up.text[:200]}"
                )
            on_progress and on_progress((idx + 1) / total_chunks * 0.85)

    # ── Poll status ───────────────────────────────────────────────
    final = _poll_status(access_token, publish_id, on_progress=on_progress)
    return {"publish_id": publish_id, **final}


def _poll_status(
    access_token: str,
    publish_id: str,
    *,
    timeout_s: int = 240,
    on_progress: Optional[Callable[[float], None]] = None,
) -> dict:
    deadline = time.time() + timeout_s
    last_pct = 0.85
    while time.time() < deadline:
        r = requests.post(
            STATUS_URL,
            json={"publish_id": publish_id},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type":  "application/json; charset=UTF-8",
            },
            timeout=15,
        )
        data = r.json().get("data") or {}
        status = data.get("status", "UNKNOWN")
        if status == "PUBLISH_COMPLETE":
            on_progress and on_progress(1.0)
            return {
                "status":    "PUBLISH_COMPLETE",
                "share_url": (data.get("publicaly_available_post_id") or [None])[0]
                              if isinstance(data.get("publicaly_available_post_id"), list) else None,
            }
        if status in ("FAILED", "EXPIRED"):
            return {"status": status, "fail_reason": data.get("fail_reason"), "share_url": None}
        last_pct = min(0.99, last_pct + 0.01)
        on_progress and on_progress(last_pct)
        time.sleep(3)
    return {"status": "TIMEOUT", "share_url": None}


# ─────────────────────────────────────────────────────────────────────
# Helpers haut niveau pour l'app desktop
# ─────────────────────────────────────────────────────────────────────
def quick_publish(
    file_path: str | Path,
    title: str,
    *,
    base: Optional[Path] = None,
    on_progress: Optional[Callable[[float], None]] = None,
    **post_opts,
) -> dict:
    """Upload + publish en un seul appel. Lit les credentials depuis env."""
    client_key    = os.environ.get("TIKTOK_CLIENT_KEY", "")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET", "")
    if not client_key or not client_secret:
        raise RuntimeError("TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET non définis (.env)")

    token = get_valid_token(client_key, client_secret, base)
    return upload_video(token, file_path, title, on_progress=on_progress, **post_opts)


def is_connected(base: Optional[Path] = None) -> bool:
    return load_session(base) is not None


def disconnect(base: Optional[Path] = None) -> None:
    p = _session_path(base)
    if p.exists():
        p.unlink()
