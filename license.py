"""Beat Cash — License client (desktop).

Stocke la license key + son token signé en local. Vérifie hebdomadairement
auprès du backend cloud. En cas d'offline, garde le plan jusqu'à expiration
du token (typiquement 7 jours).

Layout des fichiers :
    license.json   : { "key": "BC-...", "device_id": "...", "cache": {...} }
"""
from __future__ import annotations

import json
import os
import platform
import time
import uuid
from pathlib import Path
from typing import Optional

import requests

# ── Config ────────────────────────────────────────────────────────────
DEFAULT_API = os.environ.get("BEATCASH_API", "https://app.beatcash.app")
LICENSE_FILE = "license.json"
RECHECK_DAYS = 7        # vérification cloud toutes les 7 jours
GRACE_DAYS   = 14       # offline grace si le check échoue


def _path(base: Optional[Path] = None) -> Path:
    return (base or Path.cwd()) / LICENSE_FILE


def _device_id() -> str:
    """ID stable par machine (UUID basé sur node/MAC)."""
    return f"{platform.node()}-{uuid.getnode():012x}"


# ── Storage ──────────────────────────────────────────────────────────
def _load(base: Optional[Path] = None) -> dict:
    p = _path(base)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict, base: Optional[Path] = None) -> None:
    _path(base).write_text(json.dumps(data, indent=2), encoding="utf-8")


# ── Public API ───────────────────────────────────────────────────────
def status(base: Optional[Path] = None) -> dict:
    """Retourne l'état actuel sans contacter le serveur.

    {
      "plan": "FREE" | "PRO",
      "key":  str | None,
      "valid_until": int | None  (unix ms),
      "needs_recheck": bool,
      "online": bool,                 # cache encore valide ?
    }
    """
    d = _load(base)
    cache = d.get("cache") or {}
    expires_at = cache.get("expires_at")
    now = int(time.time() * 1000)

    plan = "FREE"
    if expires_at and expires_at > now:
        plan = cache.get("plan", "FREE")

    last_check = d.get("last_check_at", 0)
    needs_recheck = (now - last_check) > RECHECK_DAYS * 24 * 3600 * 1000

    return {
        "plan":          plan,
        "key":           d.get("key"),
        "valid_until":   expires_at,
        "needs_recheck": needs_recheck,
        "online":        bool(expires_at and expires_at > now),
        "device_id":     d.get("device_id") or _device_id(),
    }


def is_pro(base: Optional[Path] = None) -> bool:
    return status(base)["plan"] == "PRO"


def activate(key: str, base: Optional[Path] = None, api: Optional[str] = None) -> dict:
    """Active une license en contactant le serveur. Lève en cas d'échec.

    Retourne le status() actualisé.
    """
    api = api or DEFAULT_API
    device_id = _device_id()

    r = requests.post(
        f"{api}/api/license/verify",
        json={"key": key, "device_id": device_id},
        timeout=15,
    )
    if r.status_code == 404:
        raise RuntimeError("License inconnue. Vérifie la clé.")
    if r.status_code == 409:
        raise RuntimeError("License déjà liée à un autre appareil.")
    if not r.ok:
        try: msg = r.json().get("error", r.text[:200])
        except Exception: msg = r.text[:200]
        raise RuntimeError(f"Échec activation [{r.status_code}] : {msg}")

    data = r.json()
    if not data.get("valid"):
        raise RuntimeError(data.get("error", "License invalide"))

    plan       = data.get("plan", "FREE")
    cached_for = data.get("cached_for_seconds", 7 * 24 * 3600)
    now_ms     = int(time.time() * 1000)
    cache = {
        "plan":         plan,
        "token":        data.get("token"),
        "issued_at":    now_ms,
        "expires_at":   now_ms + cached_for * 1000,
    }
    _save({
        "key":           key,
        "device_id":     device_id,
        "cache":         cache,
        "last_check_at": now_ms,
    }, base)
    return status(base)


def recheck(base: Optional[Path] = None, api: Optional[str] = None) -> dict:
    """Re-vérifie le plan auprès du serveur. Si offline, garde l'état actuel."""
    d = _load(base)
    if not d.get("key"):
        return status(base)
    try:
        return activate(d["key"], base, api)
    except Exception as e:
        # Garde le cache existant. Si trop vieux (> GRACE_DAYS post-expiration), bascule FREE.
        cache = d.get("cache") or {}
        expires_at = cache.get("expires_at", 0)
        grace_until = expires_at + GRACE_DAYS * 24 * 3600 * 1000
        if int(time.time() * 1000) > grace_until:
            cache["plan"] = "FREE"
            d["cache"] = cache
            _save(d, base)
        return {**status(base), "recheck_error": str(e)}


def deactivate(base: Optional[Path] = None) -> None:
    p = _path(base)
    if p.exists():
        p.unlink()
