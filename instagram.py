"""
Module Instagram — upload de Reels via instagrapi
"""

import sys, json, time
from pathlib import Path

def _appdir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

SESSION_FILE = _appdir() / "instagram_session.json"

try:
    from instagrapi import Client
    from instagrapi.exceptions import (
        LoginRequired, TwoFactorRequired, ChallengeRequired,
        BadPassword, InvalidMediaId
    )
    INSTA_OK = True
except ImportError:
    INSTA_OK = False


def get_client():
    return Client() if INSTA_OK else None


def login(username: str, password: str, verification_code: str = None):
    """
    Connexion Instagram. Retourne le client connecté.
    Lève TwoFactorRequired si la 2FA est nécessaire et non fournie.
    """
    if not INSTA_OK:
        raise RuntimeError("instagrapi n'est pas installé.\nLance installer.bat.")

    cl = Client()
    cl.delay_range = [1, 3]  # délai humain entre les requêtes

    # charger session existante
    if SESSION_FILE.exists():
        try:
            cl.load_settings(str(SESSION_FILE))
            cl.login(username, password)
            cl.dump_settings(str(SESSION_FILE))
            return cl
        except Exception:
            pass  # session expirée → reconnexion normale

    try:
        if verification_code:
            cl.login(username, password, verification_code=verification_code)
        else:
            cl.login(username, password)
    except TwoFactorRequired:
        raise  # l'UI va demander le code
    except ChallengeRequired:
        raise RuntimeError(
            "Instagram demande une vérification de sécurité.\n"
            "Connecte-toi manuellement sur l'app Instagram une fois, puis réessaie."
        )
    except BadPassword:
        raise RuntimeError("Mot de passe incorrect.")

    cl.dump_settings(str(SESSION_FILE))
    return cl


def upload_reel(cl, video_path: Path, caption: str = "", cover_path: Path = None,
                progress_cb=None):
    """
    Upload un Reel Instagram.
    Retourne l'URL du post.
    """
    if not INSTA_OK:
        raise RuntimeError("instagrapi n'est pas installé.\nLance installer.bat.")

    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {video_path}")

    if progress_cb:
        progress_cb(10, "Préparation du Reel...")

    kwargs = {
        "path": video_path,
        "caption": caption,
    }
    if cover_path and Path(cover_path).exists():
        kwargs["thumbnail"] = Path(cover_path)

    if progress_cb:
        progress_cb(30, "Upload en cours (peut prendre quelques minutes)...")

    media = cl.clip_upload(**kwargs)

    if progress_cb:
        progress_cb(100, "Reel publié !")

    code = media.code if hasattr(media, "code") else media.pk
    return f"https://www.instagram.com/reel/{code}/"


def logout(cl):
    """Déconnexion et suppression de la session locale."""
    try:
        cl.logout()
    except Exception:
        pass
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
