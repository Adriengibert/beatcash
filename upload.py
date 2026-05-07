#!/usr/bin/env python3
"""
YouTube Auto-Upload Bot
Usage:
  python upload.py video.mp4
  python upload.py video1.mp4 video2.mp4 video3.mp4
  python upload.py --watch ./videos_folder
"""

import os
import sys
import time
import argparse
import pickle
from pathlib import Path

# pip install google-auth google-auth-oauthlib google-api-python-client
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = "client_secrets.json"
TOKEN_FILE = "token.pickle"

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"}


def get_authenticated_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("\n❌ Fichier 'client_secrets.json' introuvable!")
                print("📖 Suis le guide SETUP.md pour créer tes credentials Google.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print("✅ Authentification réussie et sauvegardée.")

    return build("youtube", "v3", credentials=creds)


def upload_video(youtube, file_path: Path, title=None, description="", privacy="public"):
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ Fichier introuvable: {file_path}")
        return False

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f"⚠️  Format non supporté: {file_path.suffix} — ignoré.")
        return False

    video_title = title or file_path.stem.replace("_", " ").replace("-", " ").title()
    size_mb = file_path.stat().st_size / (1024 * 1024)

    print(f"\n📤 Upload: {file_path.name} ({size_mb:.1f} MB)")
    print(f"   Titre  : {video_title}")
    print(f"   Statut : {privacy}")

    body = {
        "snippet": {
            "title": video_title,
            "description": description,
            "categoryId": "22",  # People & Blogs (change si besoin)
        },
        "status": {
            "privacyStatus": privacy,
        },
    }

    media = MediaFileUpload(
        str(file_path),
        mimetype="video/*",
        resumable=True,
        chunksize=5 * 1024 * 1024,  # 5 MB par chunk
    )

    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    last_progress = -1
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            if progress != last_progress:
                bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
                print(f"\r   [{bar}] {progress}%", end="", flush=True)
                last_progress = progress

    print(f"\n✅ Uploadé! → https://youtu.be/{response['id']}")
    return True


def watch_folder(youtube, folder: Path, privacy: str, description: str, interval: int):
    folder = Path(folder)
    uploaded = set()
    done_folder = folder / "_uploaded"
    done_folder.mkdir(exist_ok=True)

    print(f"\n👀 Surveillance du dossier: {folder.resolve()}")
    print(f"   Vérifie toutes les {interval}s — Ctrl+C pour arrêter\n")

    while True:
        videos = [
            f for f in folder.iterdir()
            if f.suffix.lower() in SUPPORTED_EXTENSIONS and f not in uploaded
        ]

        if videos:
            for video in sorted(videos):
                success = upload_video(youtube, video, privacy=privacy, description=description)
                if success:
                    uploaded.add(video)
                    dest = done_folder / video.name
                    video.rename(dest)
                    print(f"   📁 Déplacé vers _uploaded/")
        else:
            print(f"⏳ Aucune vidéo... prochain check dans {interval}s", end="\r")

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(
        description="Upload automatique de vidéos sur YouTube",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python upload.py video.mp4
  python upload.py clip1.mp4 clip2.mp4
  python upload.py video.mp4 --titre "Mon super titre" --prive
  python upload.py --watch ./dossier_videos
  python upload.py --watch ./dossier --interval 30
        """
    )

    parser.add_argument("fichiers", nargs="*", help="Fichier(s) vidéo à uploader")
    parser.add_argument("--watch", "-w", metavar="DOSSIER",
                        help="Mode surveillance: surveille un dossier en continu")
    parser.add_argument("--interval", "-i", type=int, default=60,
                        help="Intervalle de vérification en secondes (défaut: 60)")
    parser.add_argument("--titre", "-t", help="Titre de la vidéo (1 seul fichier)")
    parser.add_argument("--description", "-d", default="",
                        help="Description de la vidéo")
    parser.add_argument("--prive", action="store_true",
                        help="Mettre la vidéo en privé")
    parser.add_argument("--non-liste", action="store_true",
                        help="Mettre la vidéo en non-répertorié")

    args = parser.parse_args()

    if args.prive:
        privacy = "private"
    elif args.non_liste:
        privacy = "unlisted"
    else:
        privacy = "public"

    if not args.fichiers and not args.watch:
        parser.print_help()
        sys.exit(0)

    print("🔐 Connexion à YouTube...")
    youtube = get_authenticated_service()

    if args.watch:
        watch_folder(youtube, Path(args.watch), privacy, args.description, args.interval)
    else:
        if args.titre and len(args.fichiers) > 1:
            print("⚠️  --titre ignoré avec plusieurs fichiers (titre auto depuis nom de fichier)")
            args.titre = None

        success_count = 0
        for fichier in args.fichiers:
            ok = upload_video(
                youtube,
                Path(fichier),
                title=args.titre,
                description=args.description,
                privacy=privacy,
            )
            if ok:
                success_count += 1

        print(f"\n🎉 {success_count}/{len(args.fichiers)} vidéo(s) uploadée(s) avec succès!")


if __name__ == "__main__":
    main()
