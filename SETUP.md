# Guide de configuration — YouTube Upload Bot

## Étape 1 — Installer Python

Télécharge Python depuis https://python.org (version 3.8+)  
⚠️ Coche "Add Python to PATH" pendant l'installation.

---

## Étape 2 — Installer les dépendances

Double-clique sur `installer.bat`  
(ou lance `pip install google-auth google-auth-oauthlib google-api-python-client` dans un terminal)

---

## Étape 3 — Créer les credentials Google (1 seule fois)

1. Va sur https://console.cloud.google.com
2. Crée un **nouveau projet** (ex: "YouTube Bot")
3. Dans le menu gauche → **APIs & Services** → **Enable APIs**
   - Cherche "YouTube Data API v3" → Activer
4. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**
   - Type d'application : **Desktop app**
   - Nom : "YouTube Bot" (peu importe)
   - Clique **Create**
5. Clique **Download JSON** → renomme le fichier en `client_secrets.json`
6. Dépose `client_secrets.json` dans ce dossier (à côté de `upload.py`)

> Si tu vois "This app isn't verified", clique "Advanced" → "Go to YouTube Bot (unsafe)" — c'est normal pour les apps perso.

---

## Étape 4 — Utilisation

### Upload d'un fichier
```
python upload.py mavideo.mp4
```

### Upload de plusieurs fichiers
```
python upload.py video1.mp4 video2.mp4 video3.mp4
```

### Avec un titre personnalisé
```
python upload.py mavideo.mp4 --titre "Mon titre super cool"
```

### Upload en privé
```
python upload.py mavideo.mp4 --prive
```

### Upload en non-répertorié
```
python upload.py mavideo.mp4 --non-liste
```

### Mode surveillance (dossier automatique)
Dépose tes MP4 dans un dossier, le bot les upload automatiquement :
```
python upload.py --watch C:\Users\moi\Videos\a_uploader
```
Les vidéos uploadées sont déplacées dans le sous-dossier `_uploaded/`.

### Mode surveillance avec vérification toutes les 30 secondes
```
python upload.py --watch ./videos --interval 30
```

---

## Astuce — Raccourci Windows

1. Crée un fichier `uploader.bat` dans ce dossier :
```bat
@echo off
python "%~dp0upload.py" %*
pause
```
2. Glisse tes MP4 sur ce fichier .bat pour les uploader directement !

---

## Catégories YouTube (si tu veux changer)

Dans `upload.py`, ligne `"categoryId": "22"`, tu peux mettre :
- `10` = Music
- `20` = Gaming  
- `22` = People & Blogs (défaut)
- `23` = Comedy
- `24` = Entertainment
- `25` = News & Politics
- `28` = Science & Technology
