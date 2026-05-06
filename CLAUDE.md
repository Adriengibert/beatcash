# BeatCash — Instructions Claude

## Mémoire rapide — chargée automatiquement

@C:\Users\giber\Documents\BEATCASH\🎯 État Actuel.md
@C:\Users\giber\Documents\BEATCASH\🏗️ Architecture.md
@C:\Users\giber\Documents\BEATCASH\🔧 Commandes.md
@C:\Users\giber\Documents\BEATCASH\📝 Historique.md

---

## Projet

**BeatCash** — outil desktop Python pour les producteurs de beats.
Publie simultanément sur YouTube et Instagram en un clic.
Formats adaptés automatiquement selon la plateforme.

**Fichier principal** : `app.py` (~2400 lignes)
**Framework UI** : CustomTkinter 5.2.2 (dark mode Apple)
**Python** : 3.10

---

## Stack technique

| Composant | Tech |
|-----------|------|
| UI | CustomTkinter 5.2.2 + tkinter (Canvas pour animations) |
| YouTube | google-api-python-client + OAuth2 |
| Instagram | instagrapi |
| SEO | module seo.py (OpenAI) |
| Build | PyInstaller (beat_cash.spec → dist\BeatCash\BeatCash.exe) |
| Installeur | Inno Setup 6 (setup.iss) |

---

## Architecture UI

### 3 onglets
| Clé | Label | Méthode |
|-----|-------|---------|
| `publier` | Publier | `_build_publier` |
| `connexions` | Connexions | `_build_connexions` |
| `seo` | SEO & Profils | `_build_seo` |

### Palette Apple Dark
```python
_DK = "#0d0d0e"   # bg principal
_DN = "#111113"   # nav
_DS = "#2c2c2e"   # bordures
_DC = "#161618"   # cards niveau 1
_DE = "#1c1c1e"   # cards niveau 2 / inputs
_DF = "#f2f2f7"   # texte primaire
_DU = "#98989f"   # texte secondaire
BLUE   = "#ff3a30" # accent rouge BeatCash
BLUE_H = "#ff5a52"
BLUE_D = "#d42a22"
GREEN  = "#30d158"
RED    = "#ff453a"
ORANGE = "#ff9f0a"
W_RED  = "#cc1100" # logo seulement
```

### Widgets custom
- `AppleBtn(ctk.CTkButton)` : styles primary / secondary / ghost / danger
- `SmoothBar(ctk.CTkProgressBar)` : interpolation animée
- `AnimatedDot(tk.Canvas)` : pulse orange (connecting) / glow vert (on) / rouge (error)
- `Spinner(tk.Canvas)` : arc tournant
- `card(parent)` : ctk.CTkFrame corner_radius=12
- `entry(parent, var)` : ctk.CTkEntry dark-native
- `label(parent, text, size, bold)` : ctk.CTkLabel

### Variables clés publication (_ev_*)
```python
self._ev_yt_dot, self._ev_ig_dot   # AnimatedDot statuts
self._ev_src_mode                   # "video" | "mp3+img"
self._ev_vid_path, self._ev_img_path, self._ev_mp3_path
self._ev_yt_on, self._ev_ig_on     # BooleanVar plateformes
self._ev_title, self._ev_priv, self._ev_cat
self._ev_btn                        # AppleBtn publier
self._ev_bar                        # SmoothBar progression
self._ev_status                     # StringVar statut texte
```

---

## Commandes essentielles

```bash
# Lancer en dev
cd "C:\Users\giber\Documents\youtube-bot"
python app.py

# Build exe
python -m PyInstaller beat_cash.spec --noconfirm

# Exe produit : dist\BeatCash\BeatCash.exe

# Installeur
"C:/Program Files (x86)/Inno Setup 6/ISCC.exe" setup.iss

# Syntax check
python -c "import py_compile; py_compile.compile('app.py', doraise=True)"

# Tuer le process avant rebuild (PowerShell)
Stop-Process -Name "BeatCash" -Force -ErrorAction SilentlyContinue
```

---

## Regles importantes

- NE JAMAIS committer : client_secrets.json, token.pickle, instagram_session.json
- Toujours tuer BeatCash.exe avant de rebuild (sinon PermissionError)
- Dark mode CTk toujours actif, pas de toggle
- Pages utilisent ctk.CTkScrollableFrame (plus de hack canvas)
- Switch de pages instantane (slide supprime car trop lent avec CTkScrollableFrame)

---

## Historique sessions

| Session | Ce qui a ete fait |
|---------|-------------------|
| Session 1 (avr 30) | Bugfixes grids, scrollbars |
| Session 2 (avr 30) | Refonte 4 sections, suppression doublons |
| Session 3 (avr 30) | 4 onglets -> 3 onglets, fusion logique |
| Session 4 (avr 30) | Palette Apple dark, animations, AnimatedDot |
| Session 5 (mai 02) | Migration CustomTkinter complete, logo CTk, fix hero |
