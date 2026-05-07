#!/usr/bin/env python3
"""Beat Cash — Upload Bot"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys, math, pickle, threading, subprocess, tempfile, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import seo as seo_module
import customtkinter as ctk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def _appdir() -> Path:
    """Dossier de base : exe (packagé PyInstaller) ou script (dev)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

# ── Chargement fonts custom (Windows) ──────────────────────────────────
def _load_bundled_fonts():
    """Enregistre Syncopate + Space Mono pour la session courante."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        FR_PRIVATE = 0x10
        fonts_dir = _appdir() / "fonts"
        if not fonts_dir.exists():
            return
        for ttf in fonts_dir.glob("*.ttf"):
            ctypes.windll.gdi32.AddFontResourceExW(str(ttf), FR_PRIVATE, 0)
    except Exception:
        pass

_load_bundled_fonts()

try:
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_OK = True
except ImportError:
    GOOGLE_OK = False

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_OK = True
except ImportError:
    DND_OK = False

import instagram as ig_module

# ══════════════════════════════════════════════════════════════════════
# PALETTE
# ══════════════════════════════════════════════════════════════════════
# Base light (logo hover Warhol uniquement)
BG      = "#f7f2f2"
CARD    = "#ffffff"
CARD2   = "#fdf8f8"
BORDER  = "#e0cccc"
TEXT    = "#0f0f0f"
SUB     = "#6b3838"
MUTED   = "#9e7070"
SHADOW  = "#ecdcdc"
W_RED   = "#cc1100"   # rouge Warhol — logo seulement
W_BLACK = "#0f0f0f"

# Accent (dark + light)
BLUE    = "#ff3a30"   # rouge BeatCash vif
BLUE_H  = "#ff5a52"   # hover
BLUE_D  = "#d42a22"   # pressed
GREEN   = "#30d158"   # vert Apple
RED     = "#ff453a"   # rouge erreur
ORANGE  = "#ff9f0a"   # orange Apple

# ── Font resolution (Segoe UI Variable si Win11, sinon fallback) ────────
def _resolve_font():
    try:
        import tkinter.font as _tf
        import tkinter as _tk2
        # Needs a root window to query families — use existing if available
        root = _tk2._default_root
        if root is None:
            return "Segoe UI"
        avail = set(_tf.families())
        for f in ("Segoe UI Variable", "Inter", "Aptos", "Segoe UI"):
            if f in avail:
                return f
    except Exception:
        pass
    return "Segoe UI"

_FONT = "Segoe UI"          # body / UI — resolved in _init_fonts()
_FONT_DISPLAY = "Segoe UI"  # logo, gros titres (Syncopate si dispo)
_FONT_MONO = "Consolas"     # mono (Space Mono si dispo)

# ── Typographic scale (ratio 1.4) ────────────────────────────────────────
T_DISPLAY = (_FONT, 28, "bold")
T_HEADING  = (_FONT, 14, "bold")
T_SUBHEAD  = (_FONT, 10, "bold")
T_BODY     = (_FONT, 10)
T_SMALL    = (_FONT, 9)
T_MICRO    = (_FONT, 8)

# ── Spacing scale ──────────────────────────────────────────────────────
SP = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "xxl": 32}

def _lerp_color(c1, c2, t):
    """Interpole entre deux couleurs hex. t=0→c1, t=1→c2."""
    def h(c):
        c = c.lstrip("#")
        return (int(c[0:2],16), int(c[2:4],16), int(c[4:6],16))
    r1,g1,b1 = h(c1); r2,g2,b2 = h(c2)
    t = max(0.0, min(1.0, t))
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

# ── Dark Mode OLED — recommandé par ui-ux-pro-max pour BeatCash ────────
# "Studio purple + waveform green on dark", deep midnight blue-black
_DK = "#0F172A"   # bg principal — deep midnight blue-black (OLED)
_DN = "#0a1020"   # nav — un cran plus sombre
_DS = "#1f2942"   # bordures / séparateurs
_DC = "#171939"   # cards niveau 1 — muted blue-purple
_DE = "#1d2240"   # cards niveau 2 / inputs
_DF = "#FFFFFF"   # fg primaire — full white (OLED contrast)
_DU = "#9aa0b4"   # fg secondaire — gris bleuté neutre
_DZ = "#5a6080"   # fg tertiaire — très estompé
_DH = "#2a3050"   # highlight border (cards)
GLOW_HOT = "#ff5a52"   # halo accent (hover rouge brand)
PURPLE = "#7C3AED"     # accent secondaire — studio purple (skill)
PURPLE_H = "#9d6df0"   # purple hover
WAVE = "#22C55E"       # waveform green (skill — connect OK)
DESTRUCT = "#DC2626"   # erreur (skill)

SCOPES           = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = _appdir() / "client_secrets.json"
TOKEN_FILE       = _appdir() / "token.pickle"
SUPPORTED_EXT    = {".mp4",".mov",".avi",".mkv",".wmv",".flv",".webm"}
IMAGE_EXT        = {".jpg",".jpeg",".png",".bmp",".webp"}
AUDIO_EXT        = {".mp3",".wav",".aac",".ogg",".flac",".m4a"}
CATEGORIES       = {
    "People & Blogs":"22","Music":"10","Gaming":"20",
    "Comedy":"23","Entertainment":"24","News":"25",
    "Science & Tech":"28","Sports":"17","Education":"27",
}

# ══════════════════════════════════════════════════════════════════════
# WIDGETS CUSTOM
# ══════════════════════════════════════════════════════════════════════

class AppleBtn(ctk.CTkButton):
    """Bouton moderne CustomTkinter."""
    def __init__(self, parent, text, command=None, style="primary",
                 font=None, padx=20, pady=8, **kw):
        style_map = {
            "primary":   {"fg_color": BLUE,    "hover_color": GLOW_HOT, "text_color": "#ffffff",
                          "border_width": 1, "border_color": GLOW_HOT},
            "secondary": {"fg_color": _DE,     "hover_color": _DS,     "text_color": _DF,
                          "border_width": 1, "border_color": _DH},
            "ghost":     {"fg_color": "transparent", "hover_color": _DE, "text_color": _DU,
                          "border_width": 1, "border_color": _DH},
            "danger":    {"fg_color": RED,     "hover_color": "#ff6b63","text_color": "#ffffff",
                          "border_width": 1, "border_color": "#ff6b63"},
        }
        s = dict(style_map.get(style, style_map["primary"]))
        f = font if isinstance(font, ctk.CTkFont) else ctk.CTkFont(
            family=_FONT,
            size=font[1] if isinstance(font, tuple) and len(font) >= 2 else 11,
            weight="bold" if isinstance(font, tuple) and len(font) >= 3 and font[2] == "bold" else "normal"
        )
        bw = s.pop("border_width", 0)
        bc = s.pop("border_color", _DS)
        super().__init__(parent, text=text, command=command,
                         font=f, corner_radius=10,
                         border_width=bw, border_color=bc,
                         **s, **kw)
        self._enabled = True

    def disable(self):
        self._enabled = False
        self.configure(state="disabled")

    def enable(self):
        self._enabled = True
        self.configure(state="normal")

    def flash(self, color=None, steps=4):
        c = color or BLUE_H
        if steps <= 0:
            self.configure(fg_color=BLUE)
            return
        self.configure(fg_color=c if steps % 2 == 0 else BLUE)
        self.after(120, lambda: self.flash(color, steps - 1))


class SmoothBar(ctk.CTkProgressBar):
    """Barre de progression CTk animée."""
    def __init__(self, parent, height=6, color=BLUE, **kw):
        kw.pop("bg", None)
        kw.pop("color", None)
        super().__init__(parent, height=height,
                         progress_color=BLUE,
                         fg_color=_DS,
                         corner_radius=3,
                         **kw)
        self._tgt = 0
        super().set(0)

    def set(self, pct):
        self._tgt = float(pct)
        self._step()

    def _step(self):
        cur = self.get() * 100
        diff = self._tgt - cur
        if abs(diff) > 0.5:
            cur += diff * 0.3
            super().set(cur / 100)
            self.after(16, self._step)
        else:
            super().set(self._tgt / 100)



class AnimatedDot(tk.Canvas):
    """Indicateur de statut animé — remplace les ⬤ tk.Label."""
    def __init__(self, parent, bg=BG, size=10, **kw):
        pad = 7
        s = size + pad * 2
        super().__init__(parent, width=s, height=s, bg=bg,
                         highlightthickness=0, **kw)
        self._dot_size  = size
        self._bg_color  = bg
        self._state     = "off"
        self._tick      = 0
        self._animating = False
        self.bind("<Configure>", lambda e: self._draw())
        self._draw()

    # ── Compatibilité avec l'API tk.Label.config(fg=...) ─────────────────
    def config(self, **kw):
        fg = kw.pop("fg", None)
        if fg is not None:
            self._set_by_color(fg)
        if kw:
            super().config(**kw)
    configure = config

    def _set_by_color(self, fg):
        if   fg == GREEN:   self._change("on")
        elif fg == RED:     self._change("error")
        elif fg == ORANGE:  self._change("connecting")
        else:               self._change("off")

    def _change(self, state):
        self._state = state
        self._tick  = 0
        if state == "connecting" and not self._animating:
            self._animating = True
            self._anim_loop()
        elif state != "connecting":
            self._animating = False
            self._draw()

    def _anim_loop(self):
        if not self._animating:
            return
        self._tick += 1
        self._draw()
        self.after(50, self._anim_loop)

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()  or (self._dot_size + 14)
        h = self.winfo_height() or (self._dot_size + 14)
        cx, cy = w // 2, h // 2
        r  = self._dot_size // 2
        bg = self._bg_color

        cols = {"on": GREEN, "error": RED, "off": "#c0a8a8", "connecting": ORANGE}
        c = cols.get(self._state, "#c0a8a8")

        if self._state == "connecting":
            pulse = (math.sin(self._tick * 0.22) + 1) / 2
            rr = int(r + 2 + pulse * 4)
            glow = _lerp_color(c, bg, 0.42 + pulse * 0.35)
            self.create_oval(cx-rr, cy-rr, cx+rr, cy+rr, fill=glow, outline="")
        elif self._state == "on":
            rr = r + 3
            glow = _lerp_color(c, bg, 0.72)
            self.create_oval(cx-rr, cy-rr, cx+rr, cy+rr, fill=glow, outline="")

        self.create_oval(cx-r, cy-r, cx+r, cy+r, fill=c, outline="")


class Spinner(tk.Canvas):
    """Arc tournant pour les états de chargement."""
    def __init__(self, parent, size=18, color=None, bg=BG, **kw):
        super().__init__(parent, width=size, height=size, bg=bg,
                         highlightthickness=0, **kw)
        self._size    = size
        self._color   = color   # resolved after globals available
        self._angle   = 0
        self._active  = False

    def start(self):
        if self._color is None:
            self._color = BLUE
        self._active = True
        self._spin()

    def stop(self):
        self._active = False
        self.delete("all")

    def _spin(self):
        if not self._active:
            return
        self.delete("all")
        s, p = self._size, 2
        # track arc
        self.create_arc(p, p, s-p, s-p,
                        start=0, extent=359,
                        outline=SHADOW, width=2, style="arc")
        # spinning arc
        self.create_arc(p, p, s-p, s-p,
                        start=self._angle, extent=260,
                        outline=self._color, width=2, style="arc")
        self._angle = (self._angle + 14) % 360
        self.after(33, self._spin)



# ══════════════════════════════════════════════════════════════════════
# WIDGETS CUSTOM — Apple-style controls
# ══════════════════════════════════════════════════════════════════════

class ToggleSwitch(tk.Canvas):
    """Interrupteur iOS animé — remplace tk.Checkbutton."""
    TW, TH = 46, 26   # track width / height

    def __init__(self, parent, variable, bg=CARD, command=None, **kw):
        super().__init__(parent, width=self.TW, height=self.TH,
                         bg=bg, highlightthickness=0, cursor="hand2", **kw)
        self._var     = variable
        self._cmd     = command
        self._bg_col  = bg
        self._knob_x  = float(self.TH // 2)
        variable.trace_add("write", lambda *_: self._sync())
        self.bind("<ButtonRelease-1>", self._click)
        self.bind("<Configure>", lambda e: self._draw())
        self._sync(animate=False)

    def _click(self, _):
        self._var.set(not self._var.get())
        if self._cmd: self._cmd()

    def _sync(self, animate=True):
        on = bool(self._var.get())
        target = float(self.TW - self.TH // 2 - 1) if on else float(self.TH // 2)
        if animate:
            self._animate_to(target, steps=7)
        else:
            self._knob_x = target
            self._draw()

    def _animate_to(self, target, steps):
        diff = target - self._knob_x
        self._knob_x += diff / steps
        self._draw()
        if steps > 1:
            self.after(14, lambda: self._animate_to(target, steps - 1))
        else:
            self._knob_x = target
            self._draw()

    def _draw(self):
        self.delete("all")
        W, H = self.TW, self.TH
        R    = H // 2
        on   = bool(self._var.get())
        col  = BLUE if on else "#555566"
        # Track
        self.create_arc(0, 0, H, H, start=90, extent=180, fill=col, outline="")
        self.create_arc(W-H, 0, W, H, start=270, extent=180, fill=col, outline="")
        self.create_rectangle(R, 0, W-R, H, fill=col, outline="")
        # Knob shadow
        kx, ky, kr = int(self._knob_x), R, R - 3
        self.create_oval(kx-kr, ky-kr, kx+kr, ky+kr,
                         fill="#00000033" if False else "#c8c8c8", outline="")
        # Knob white
        self.create_oval(kx-kr+1, ky-kr+1, kx+kr-1, ky+kr-1,
                         fill="#ffffff", outline="")


class SegmentedPill(tk.Frame):
    """Sélecteur segmenté style iOS — remplace tk.Radiobutton."""

    def __init__(self, parent, variable, options, bg=CARD, command=None, **kw):
        super().__init__(parent, bg=bg, **kw)
        self._var  = variable
        self._bg   = bg
        self._cmd  = command
        self._btns = {}
        # Container avec bordure arrondie simulée
        self.config(highlightthickness=1, highlightbackground=BORDER)
        for val, lbl in options:
            btn = tk.Label(self, text=lbl,
                           font=(_FONT, 10, "bold"),
                           bg=bg, fg=MUTED,
                           padx=18, pady=7,
                           cursor="hand2")
            btn.pack(side="left")
            btn.bind("<ButtonRelease-1>", lambda e, v=val: self._select(v))
            self._btns[val] = btn
        variable.trace_add("write", lambda *_: self._update())
        self._update()

    def _select(self, val):
        self._var.set(val)
        if self._cmd: self._cmd()

    def _update(self):
        val = self._var.get()
        for v, btn in self._btns.items():
            if v == val:
                btn.config(bg=BLUE, fg="#ffffff")
            else:
                btn.config(bg=self._bg, fg=MUTED)


class PillDropdown(tk.Frame):
    """Dropdown minimaliste — remplace ttk.Combobox."""

    def __init__(self, parent, variable, options, width=14, bg=CARD, **kw):
        super().__init__(parent, bg=bg, cursor="hand2",
                         highlightthickness=1, highlightbackground=BORDER, **kw)
        self._var  = variable
        self._opts = options
        self._bg   = bg

        self._lbl = tk.Label(self, font=(_FONT, 10), bg=bg, fg=TEXT,
                             padx=12, pady=5, width=width, anchor="w",
                             cursor="hand2")
        self._lbl.pack(side="left")
        tk.Label(self, text="▾", font=(_FONT, 10), bg=bg, fg=MUTED,
                 padx=6, pady=5, cursor="hand2").pack(side="left")

        self._lbl.bind("<ButtonRelease-1>", self._open)
        self.bind("<ButtonRelease-1>", self._open)
        for child in self.winfo_children():
            child.bind("<Enter>", lambda e: self.config(
                highlightbackground=BLUE))
            child.bind("<Leave>", lambda e: self.config(
                highlightbackground=BORDER))
        self.bind("<Enter>", lambda e: self.config(highlightbackground=BLUE))
        self.bind("<Leave>", lambda e: self.config(highlightbackground=BORDER))

        variable.trace_add("write", lambda *_: self._update())
        self._update()

    def _update(self):
        self._lbl.config(text=self._var.get())

    def _open(self, _=None):
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        bg = _DK
        fg_t = _DF
        popup.configure(bg=bg, highlightthickness=1,
                        highlightbackground=BORDER)
        self.update_idletasks()
        px = self.winfo_rootx()
        py = self.winfo_rooty() + self.winfo_height() + 2
        popup.geometry(f"+{px}+{py}")

        for opt in self._opts:
            row = tk.Label(popup, text=opt, font=(_FONT, 10),
                           bg=bg, fg=fg_t, padx=14, pady=7,
                           anchor="w", cursor="hand2")
            row.pack(fill="x")
            row.bind("<Enter>", lambda e, r=row: r.config(bg=BLUE, fg="#ffffff"))
            row.bind("<Leave>", lambda e, r=row: r.config(bg=bg, fg=fg_t))
            row.bind("<ButtonRelease-1>",
                     lambda e, o=opt: (self._var.set(o), popup.destroy()))

        popup.bind("<FocusOut>", lambda e: popup.destroy())
        popup.focus_set()


def card(parent, pady=(0, SP["md"]), padx=0, **kw):
    """Carte futuriste : bordure subtile, corner radius prononcé."""
    f = ctk.CTkFrame(parent, fg_color=_DC, corner_radius=14,
                     border_width=1, border_color=_DH, **kw)
    f.pack(fill="x", pady=pady, padx=padx)
    return f


def pulse_dot(dot, colors=None, interval=380, _idx=0):
    """Anime un label dot ⬤ en cyclant sur colors tant que dot._pulse est True."""
    if not getattr(dot, '_pulse', False):
        return
    c = colors or [ORANGE, "#c05500", "#e09000", "#c05500"]
    try:
        dot.config(fg=c[_idx % len(c)])
        dot.after(interval, lambda: pulse_dot(dot, colors, interval, _idx + 1))
    except tk.TclError:
        pass  # widget détruit


def label(parent, text, size=13, bold=False, color=None, **kw):
    kw.pop("bg", None)
    c = color or _DF
    font = ctk.CTkFont(family=_FONT, size=size, weight="bold" if bold else "normal")
    lbl = ctk.CTkLabel(parent, text=text, font=font, text_color=c,
                       fg_color="transparent", **kw)
    return lbl


def sublabel(parent, text, size=10, **kw):
    return label(parent, text, size=size, color=_DU, **kw)


def sep(parent):
    f = ctk.CTkFrame(parent, fg_color=_DS, height=1, corner_radius=0)
    f.pack(fill="x", pady=10)
    f.pack_propagate(False)


def entry(parent, var, width=200, show="", **kw):
    """Entry CTk avec border ring."""
    kw.pop("bg", None)
    kw.pop("fg", None)
    kw.pop("relief", None)
    kw.pop("highlightthickness", None)
    kw.pop("highlightbackground", None)
    kw.pop("insertbackground", None)
    e = ctk.CTkEntry(parent, textvariable=var, show=show,
                     font=ctk.CTkFont(family=_FONT, size=11),
                     fg_color=_DE, border_color=_DS, border_width=1,
                     text_color=_DF, placeholder_text_color=_DU,
                     width=width, corner_radius=8, **kw)
    return e


# ══════════════════════════════════════════════════════════════════════
# AUTH YOUTUBE
# ══════════════════════════════════════════════════════════════════════
_yt = None

def get_youtube():
    global _yt
    if _yt: return _yt
    creds = None
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE,"rb") as f: creds = pickle.load(f)
        except Exception:
            TOKEN_FILE.unlink(missing_ok=True)
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # Token révoqué ou expiré — on repart de zéro
                TOKEN_FILE.unlink(missing_ok=True)
                creds = None
        if not creds:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError("client_secrets.json introuvable")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE,"wb") as f: pickle.dump(creds, f)
    _yt = build("youtube","v3",credentials=creds)
    return _yt


# ══════════════════════════════════════════════════════════════════════
# FFMPEG
# ══════════════════════════════════════════════════════════════════════
def find_ffmpeg():
    try:
        subprocess.run(["ffmpeg","-version"],capture_output=True,check=True)
        return "ffmpeg"
    except: pass
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except: pass
    return None

def make_mp4(img, audio, out, cb=None):
    ff = find_ffmpeg()
    if not ff: raise RuntimeError("ffmpeg introuvable. Lance installer.bat.")
    cmd = [ff,"-y","-loop","1","-i",str(img),"-i",str(audio),
           "-c:v","libx264","-tune","stillimage","-c:a","aac","-b:a","192k",
           "-pix_fmt","yuv420p","-vf","scale=trunc(iw/2)*2:trunc(ih/2)*2",
           "-shortest",str(out)]
    proc = subprocess.Popen(cmd,stderr=subprocess.PIPE,stdout=subprocess.PIPE,
                            universal_newlines=True)
    lines, dur = [], None
    for line in proc.stderr:
        lines.append(line)
        if "Duration:" in line and not dur:
            try:
                t=line.split("Duration:")[1].split(",")[0].strip()
                h,m,s=t.split(":"); dur=int(h)*3600+int(m)*60+float(s)
            except: pass
        if "time=" in line and dur and cb:
            try:
                t=line.split("time=")[1].split(" ")[0].strip()
                h,m,s=t.split(":"); cb(min(int((int(h)*3600+int(m)*60+float(s))/dur*100),99))
            except: pass
    proc.wait()
    if proc.returncode!=0:
        raise RuntimeError("ffmpeg a échoué:\n"+"".join(lines[-15:]))


# ══════════════════════════════════════════════════════════════════════
# APPLICATION
# ══════════════════════════════════════════════════════════════════════
class App(TkinterDnD.Tk if DND_OK else ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("$ BEAT CASH")
        self.geometry("960x720")
        self.minsize(820, 600)
        try:
            self.configure(fg_color=_DK)
        except tk.TclError:
            self.configure(bg=_DK)

        self.queue        = []
        self.uploading    = False
        self.stop_flag    = False
        self.youtube      = None
        self._img_path    = None
        self._mp3_path    = None
        self._ig_client   = None
        self._ig_vid_path = None
        self._ig_cov_path = None
        self._rows        = []
        self._dark_mode   = True
        self._current_key = "publier"

        self._init_fonts()
        self._build()

    # ──────────────────────────────────────────────────────────────────
    # ANIMATION DE DÉMARRAGE
    # ──────────────────────────────────────────────────────────────────
    def _run_splash(self):
        """
        Splash Warhol : grand $ centré sur fond noir
        → rétrécit et vole vers le logo en haut à gauche.
        Utilise un Toplevel pour être visible par-dessus tout.
        """
        self.update()                       # forcer le rendu complet
        self.update_idletasks()

        W  = self.winfo_width()
        H  = self.winfo_height()
        RX = self.winfo_rootx()
        RY = self.winfo_rooty()

        if W < 50:                          # pas encore rendu
            self.after(80, self._run_splash)
            return

        # ── Fenêtre splash (sans chrome, par-dessus tout) ─────────────
        sp = tk.Toplevel(self)
        sp.overrideredirect(True)
        sp.geometry(f"{W}x{H}+{RX}+{RY}")
        sp.attributes("-topmost", True)
        sp.lift()

        cv = tk.Canvas(sp, bg=W_BLACK, highlightthickness=0,
                       width=W, height=H)
        cv.pack(fill="both", expand=True)

        # ── Coordonnées ───────────────────────────────────────────────
        sx, sy     = W // 2, H // 2
        fx, fy     = RX + 34, RY + 34      # position du $ dans le logo
        # (coordonnées écran → on travaille en coordonnées canvas = fenêtre splash)
        fx_cv      = 34                    # en coords canvas
        fy_cv      = 34

        SIZE_BIG   = min(W, H) // 3
        SIZE_SMALL = 38

        # ── Phases ────────────────────────────────────────────────────
        # 0..20  : apparition
        # 20..35 : maintien + légère respiration
        # 35..90 : vol vers le logo
        # 90..100: disparition
        TOTAL = 100
        DELAY = 16
        frame = [0]

        def eio(t):          # ease-in-out
            return t * t * (3 - 2 * t)
        def eoc(t):          # ease-out cubic
            return 1 - (1 - t) ** 3
        def lerp(a, b, t):
            return a + (b - a) * t
        def lerpRGB(c1, c2, t):
            return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
        def hex3(c):
            return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"

        C_BLACK = (12,  12,  12)
        C_APP   = (247, 242, 242)

        def step():
            f = frame[0]
            if f > TOTAL:
                sp.destroy()
                return

            # valeurs par défaut
            bg   = C_BLACK
            show = True

            if f <= 20:                     # ── Apparition
                t   = eio(f / 20)
                sz  = SIZE_BIG
                x, y = sx, sy
                off  = max(4, sz // 16)

            elif f <= 35:                   # ── Maintien / respiration
                t   = (f - 20) / 15
                pulse = math.sin(t * math.pi * 2) * 0.02
                sz  = int(SIZE_BIG * (1 + pulse))
                x, y = sx, sy
                off  = max(4, sz // 16)

            elif f <= 90:                   # ── Vol vers le logo
                t   = eoc((f - 35) / 55)
                sz  = int(lerp(SIZE_BIG, SIZE_SMALL, t))
                x   = lerp(sx, fx_cv, t)
                y   = lerp(sy, fy_cv, t)
                off = max(1, sz // 16)
                # fond s'efface à partir de t=0.5
                t_bg = max(0, (t - 0.5) / 0.5)
                bg   = lerpRGB(C_BLACK, C_APP, eio(t_bg))

            else:                           # ── Disparition
                t   = (f - 90) / 10
                sz  = SIZE_SMALL
                x, y = fx_cv, fy_cv
                off  = 1
                bg   = C_APP
                show = (t < 0.95)

            # ── Rendu du frame ────────────────────────────────────────
            cv.configure(bg=hex3(bg))
            cv.delete("all")

            if show:
                # Ombre rouge (décalée +off)
                cv.create_text(x + off, y + off, text="$",
                               font=("Impact", sz),
                               fill=W_RED, anchor="center")
                # $ blanc/clair (décalé -off)
                cv.create_text(x - off, y - off, text="$",
                               font=("Impact", sz),
                               fill=_DF, anchor="center")

            frame[0] += 1
            self.after(DELAY, step)

        step()

    def _init_fonts(self):
        """Détecte les fonts custom (Syncopate display + Space Mono) avec fallback."""
        global _FONT, _FONT_DISPLAY, _FONT_MONO
        global T_DISPLAY, T_HEADING, T_SUBHEAD, T_BODY, T_SMALL, T_MICRO
        global CTK_DISPLAY, CTK_HEADING, CTK_BODY, CTK_SMALL
        import tkinter.font as tkf
        try:
            avail = set(tkf.families())
            # Body / UI : Segoe UI Variable > Inter > Segoe UI
            for f in ("Segoe UI Variable", "Inter", "Aptos", "Segoe UI"):
                if f in avail:
                    _FONT = f
                    break
            # Display (logo, gros titres) : Syncopate (skill) > Bahnschrift > _FONT
            _FONT_DISPLAY = _FONT
            for f in ("Syncopate", "Bahnschrift Condensed", "Bahnschrift", _FONT):
                if f in avail:
                    _FONT_DISPLAY = f
                    break
            # Mono (numéros, statuts techniques) : Space Mono (skill) > Cascadia > Consolas
            _FONT_MONO = _FONT
            for f in ("Space Mono", "Cascadia Mono", "Cascadia Code", "Consolas", _FONT):
                if f in avail:
                    _FONT_MONO = f
                    break
        except Exception:
            _FONT = "Segoe UI"
            _FONT_DISPLAY = _FONT
            _FONT_MONO = _FONT
        T_DISPLAY = (_FONT_DISPLAY, 24, "bold")
        T_HEADING  = (_FONT, 13, "bold")
        T_SUBHEAD  = (_FONT, 11, "bold")
        T_BODY     = (_FONT, 11)
        T_SMALL    = (_FONT, 10)
        T_MICRO    = (_FONT, 9)
        CTK_DISPLAY = ctk.CTkFont(family=_FONT_DISPLAY, size=24, weight="bold")
        CTK_HEADING = ctk.CTkFont(family=_FONT, size=13, weight="bold")
        CTK_BODY    = ctk.CTkFont(family=_FONT, size=11)
        CTK_SMALL   = ctk.CTkFont(family=_FONT, size=10)

    # ──────────────────────────────────────────────────────────────────
    # NAVIGATION
    # ──────────────────────────────────────────────────────────────────
    def _build(self):
        # ── Barre de navigation ──
        nav = ctk.CTkFrame(self, fg_color=_DN, corner_radius=0, height=64)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        self._nav = nav

        left = ctk.CTkFrame(nav, fg_color=_DN, corner_radius=0)
        left.pack(side="left", padx=28, pady=8)
        self._draw_logo(left)

        # Tabs
        tabs_frame = ctk.CTkFrame(nav, fg_color=_DN, corner_radius=0)
        tabs_frame.pack(side="left", padx=20)

        # Pill animée (derrière les labels — créée EN PREMIER)
        self._pill = tk.Frame(tabs_frame, bg=_DS, height=34)
        self._pill.place(x=0, y=4, width=4, height=34)
        self._pill.lower()

        self._tab_btns = {}
        for key, lbl in [("publier","🚀  Publier"),
                          ("connexions","🔑  Connexions"),
                          ("seo","✨  SEO & Profils")]:
            b = tk.Label(tabs_frame, text=lbl,
                         font=(_FONT, 10, "bold"),
                         bg=_DN, fg=_DU, cursor="hand2",
                         padx=16, pady=10)
            b.pack(side="left", padx=1)
            b.bind("<Button-1>", lambda e, k=key: self._switch(k))
            b.bind("<Enter>", lambda e, btn=b, k=key: self._tab_hover(btn, k, True))
            b.bind("<Leave>", lambda e, btn=b, k=key: self._tab_hover(btn, k, False))
            self._tab_btns[key] = b

        # Underline invisible (compatibilité)
        self._uline = tk.Frame(self, bg=_DN, height=1)
        self._uline.place(x=0, y=0, width=0, height=1)

        # ── Pages ──
        self._pages = {}
        container = ctk.CTkFrame(self, fg_color=_DK, corner_radius=0)
        container.pack(fill="both", expand=True)
        self._container = container

        for key in ("publier","connexions","seo"):
            f = ctk.CTkFrame(container, fg_color=_DK, corner_radius=0)
            self._pages[key] = f

        self._build_publier(self._pages["publier"])
        self._build_connexions(self._pages["connexions"])
        self._build_seo(self._pages["seo"])

        self._switch("publier")

    def _switch_tab(self, key):
        self._switch(key)

    def _switch(self, key):
        prev_key = getattr(self, '_current_key', None)
        self._current_key = key

        # Couleurs onglets
        for k, b in self._tab_btns.items():
            active = (k == key)
            b.config(fg=_DF if active else _DU, bg=_DN)

        # Pill animée
        self.update_idletasks()
        b = self._tab_btns[key]
        tx = b.winfo_x()
        tw = b.winfo_width()
        self._animate_pill(tx, 4, tw, 34)

        # Switch instantané — la pill anime, pas le contenu
        for k, f in self._pages.items():
            f.pack_forget()
        self._pages[key].pack(fill="both", expand=True)

    def _slide_pages(self, old_key, new_key, direction, step=0, steps=7):
        """Glisse old_page vers la gauche/droite et new_page depuis l'opposé."""
        w = self._container.winfo_width() or 900

        if step == 0:
            for k, f in self._pages.items():
                f.pack_forget()
            self._pages[old_key].place(x=0, y=0, relwidth=1, relheight=1)
            self._pages[new_key].place(x=w * direction, y=0,
                                       relwidth=1, relheight=1)
            self.after(16, lambda: self._slide_pages(
                old_key, new_key, direction, 1, steps))
            return

        def ease_out(t): return 1 - (1 - t) ** 3

        t     = ease_out(step / steps)
        old_x = int(-w * t * direction)
        new_x = int(w * direction * (1 - t))

        self._pages[old_key].place(x=old_x, y=0, relwidth=1, relheight=1)
        self._pages[new_key].place(x=new_x, y=0, relwidth=1, relheight=1)

        if step < steps:
            self.after(16, lambda: self._slide_pages(
                old_key, new_key, direction, step + 1, steps))
        else:
            self._pages[old_key].place_forget()
            self._pages[new_key].place_forget()
            self._pages[new_key].pack(fill="both", expand=True)

    def _animate_pill(self, tx, ty, tw, th, steps=7):
        """Glisse la pill sous l'onglet actif (ease-out quart)."""
        try:
            cx = self._pill.winfo_x()
            cw = self._pill.winfo_width() or tw
        except Exception:
            cx, cw = tx, tw
        def ease(t): return 1 - (1 - t) ** 4
        progress = ease(1 / max(steps, 1))
        nx = cx + (tx - cx) * progress
        nw = max(4, cw + (tw - cw) * progress)
        self._pill.place(x=int(nx), y=ty, width=int(nw), height=th)
        if steps > 1:
            self.after(16, lambda: self._animate_pill(tx, ty, tw, th, steps - 1))

    def _tab_hover(self, btn, key, entering):
        """Hover discret sur onglets inactifs."""
        if key == self._current_key:
            return
        btn.config(bg=_DS if entering else _DN)

    # ──────────────────────────────────────────────────────────────────
    # LOGO  — Style Warhol $ sign  +  déclencheur de thème
    # ──────────────────────────────────────────────────────────────────
    def _draw_logo(self, parent):
        """Logo BeatCash — wordmark Syncopate ($) + double trait glow."""
        container = ctk.CTkFrame(parent, fg_color=_DN, corner_radius=0)
        container.pack(side="left")

        row = ctk.CTkFrame(container, fg_color=_DN, corner_radius=0)
        row.pack(side="top", anchor="w")

        # $ — accent rouge brand (Warhol heritage)
        ctk.CTkLabel(row, text="$",
                     font=ctk.CTkFont(family=_FONT_DISPLAY, size=30, weight="bold"),
                     text_color=BLUE,
                     fg_color=_DN).pack(side="left", padx=(0, 6), pady=(0, 0))

        # BEATCASH — wordmark Syncopate, full white pour OLED contrast
        ctk.CTkLabel(row, text="BEATCASH",
                     font=ctk.CTkFont(family=_FONT_DISPLAY, size=15, weight="bold"),
                     text_color=_DF,
                     fg_color=_DN).pack(side="left", pady=(6, 0))

        # Glow underline rouge fin (intense)
        underline = ctk.CTkFrame(container, fg_color=BLUE,
                                 height=2, width=160, corner_radius=1)
        underline.pack(side="top", anchor="w", padx=(2, 0), pady=(2, 0))
        underline.pack_propagate(False)

        # Sous-glow purple plus diffus (skill secondary accent)
        underline2 = ctk.CTkFrame(container, fg_color=PURPLE,
                                  height=1, width=130, corner_radius=1)
        underline2.pack(side="top", anchor="w", padx=(2, 0), pady=(0, 0))
        underline2.pack_propagate(False)

        self._logo_draw = lambda dark=True: None  # compat

    # ──────────────────────────────────────────────────────────────────
    # THÈME DYNAMIQUE  — CTk gère le dark mode nativement
    # ──────────────────────────────────────────────────────────────────
    def _set_theme(self, dark):
        """Conservé pour compatibilité — CTk gère le thème nativement."""
        self._dark_mode = dark
        if hasattr(self, '_logo_draw'):
            self._logo_draw(dark)
        if hasattr(self, '_pill'):
            self._pill.configure(bg=_DS)
        if hasattr(self, '_tab_btns'):
            cur = self._current_key
            for k, b in self._tab_btns.items():
                active = (k == cur)
                b.configure(fg=_DF if active else _DU, bg=_DN)

    # ══════════════════════════════════════════════════════════════════
    # PAGE 1 — PUBLIER (unifié YouTube + Instagram)
    # ══════════════════════════════════════════════════════════════════
    def _build_publier(self, p):
        wrap = ctk.CTkScrollableFrame(p, fg_color=_DK, scrollbar_button_color=_DS,
                                      scrollbar_button_hover_color=_DE)
        wrap.pack(fill="both", expand=True, padx=0, pady=0)
        inner_wrap = ctk.CTkFrame(wrap, fg_color=_DK, corner_radius=0)
        inner_wrap.pack(fill="both", expand=True, padx=40, pady=30)
        wrap = inner_wrap  # alias pour le reste de la méthode

        hero = ctk.CTkFrame(wrap, fg_color=_DK, corner_radius=0)
        hero.pack(fill="x", pady=(0,20))
        acc = ctk.CTkFrame(hero, fg_color=BLUE, width=4, height=52, corner_radius=2)
        acc.pack(side="left", padx=(0,14))
        acc.pack_propagate(False)
        htxt = ctk.CTkFrame(hero, fg_color=_DK, corner_radius=0)
        htxt.pack(side="left")
        label(htxt,"Publier",24,True).pack(anchor="w")
        sublabel(htxt,
            "Publie en une fois sur YouTube et Instagram — formats adaptés automatiquement.",
            10).pack(anchor="w",pady=(3,0))

        # ── Statut connexions ─────────────────────────────────────────
        conn_card = card(wrap)
        conn_in   = ctk.CTkFrame(conn_card, fg_color=_DC, corner_radius=0)
        conn_in.pack(fill="x", padx=20, pady=14)
        label(conn_in,"Connexions",14,True).pack(anchor="w",pady=(0,10))

        conn_row = ctk.CTkFrame(conn_in, fg_color=_DC, corner_radius=0)
        conn_row.pack(fill="x")

        yt_box = ctk.CTkFrame(conn_row, fg_color=_DC, corner_radius=8,
                              border_width=1, border_color=_DS)
        yt_box.pack(side="left", padx=(0,12), ipadx=16, ipady=10)
        yt_top = ctk.CTkFrame(yt_box, fg_color=_DC, corner_radius=0)
        yt_top.pack(anchor="w")
        self._ev_yt_dot = AnimatedDot(yt_top, bg=_DC)
        self._ev_yt_dot.pack(side="left", padx=(0,4))
        self._ev_yt_lbl = ctk.CTkLabel(yt_top, text="YouTube — non connecté",
                                       font=ctk.CTkFont(family=_FONT,size=10,weight="bold"),
                                       text_color=_DF, fg_color="transparent")
        self._ev_yt_lbl.pack(side="left")
        AppleBtn(yt_box,"→ Connexions",
                 command=lambda: self._switch("connexions"),
                 style="secondary",font=(_FONT,9,"bold"),
                 padx=12,pady=5).pack(anchor="w",pady=(8,0))

        ig_box = ctk.CTkFrame(conn_row, fg_color=_DC, corner_radius=8,
                              border_width=1, border_color=_DS)
        ig_box.pack(side="left", ipadx=16, ipady=10)
        ig_top = ctk.CTkFrame(ig_box, fg_color=_DC, corner_radius=0)
        ig_top.pack(anchor="w")
        self._ev_ig_dot = AnimatedDot(ig_top, bg=_DC)
        self._ev_ig_dot.pack(side="left", padx=(0,4))
        self._ev_ig_lbl = ctk.CTkLabel(ig_top, text="Instagram — non connecté",
                                       font=ctk.CTkFont(family=_FONT,size=10,weight="bold"),
                                       text_color=_DF, fg_color="transparent")
        self._ev_ig_lbl.pack(side="left")
        AppleBtn(ig_box,"→ Connexions",
                 command=lambda: self._switch("connexions"),
                 style="secondary",font=(_FONT,9,"bold"),
                 padx=12,pady=5).pack(anchor="w",pady=(8,0))

        self.after(200, self._ev_sync_status)

        # ── Source & Plateformes ──────────────────────────────────────
        pub_card = card(wrap)
        pub_in = ctk.CTkFrame(pub_card, fg_color=_DC, corner_radius=0)
        pub_in.pack(fill="x", padx=20, pady=16)
        label(pub_in,"Source & Publication",14,True).pack(anchor="w",pady=(0,12))

        sublabel(pub_in,"Fichier à publier",10).pack(anchor="w",pady=(0,6))
        self._ev_mode = tk.StringVar(value="video")
        SegmentedPill(pub_in, self._ev_mode,
                      [("video","  Vidéo MP4  "), ("mp3img","  MP3 + Image  ")],
                      bg=_DC, command=self._ev_toggle_source
                      ).pack(anchor="w", pady=(0,12))

        self._ev_vid_frame = ctk.CTkFrame(pub_in, fg_color=_DC, corner_radius=0)
        self._ev_vid_frame.pack(fill="x")
        self._ev_vid_lbl = ctk.CTkLabel(self._ev_vid_frame,
                                        text="Aucune vidéo sélectionnée",
                                        font=ctk.CTkFont(family=_FONT,size=10),
                                        text_color=_DU, fg_color="transparent")
        self._ev_vid_lbl.pack(anchor="w",pady=(0,6))
        AppleBtn(self._ev_vid_frame,"Choisir une vidéo",
                 command=self._ev_pick_vid, style="secondary",
                 font=(_FONT,10,"bold"),padx=14,pady=7).pack(anchor="w")
        self._ev_vid_path = None

        self._ev_mp3img_frame = ctk.CTkFrame(pub_in, fg_color=_DC, corner_radius=0)
        self._ev_img_lbl = ctk.CTkLabel(self._ev_mp3img_frame,
                                        text="Image : aucune",
                                        font=ctk.CTkFont(family=_FONT,size=10),
                                        text_color=_DU, fg_color="transparent")
        self._ev_img_lbl.pack(anchor="w",pady=(0,4))
        self._ev_mp3_lbl = ctk.CTkLabel(self._ev_mp3img_frame,
                                        text="Audio : aucun",
                                        font=ctk.CTkFont(family=_FONT,size=10),
                                        text_color=_DU, fg_color="transparent")
        self._ev_mp3_lbl.pack(anchor="w",pady=(0,6))
        brow = ctk.CTkFrame(self._ev_mp3img_frame, fg_color=_DC, corner_radius=0)
        brow.pack(anchor="w")
        AppleBtn(brow,"Image",command=self._ev_pick_img,
                 style="secondary",font=(_FONT,9,"bold"),
                 padx=12,pady=7).pack(side="left",padx=(0,8))
        AppleBtn(brow,"Audio",command=self._ev_pick_mp3,
                 style="secondary",font=(_FONT,9,"bold"),
                 padx=12,pady=7).pack(side="left")
        self._ev_img_path = None
        self._ev_mp3_path = None
        self._ev_mp3img_frame.pack_forget()

        sep(pub_in)

        sublabel(pub_in,"Où publier",10).pack(anchor="w",pady=(0,6))
        self._ev_yt  = tk.BooleanVar(value=True)
        self._ev_ig  = tk.BooleanVar(value=True)
        self._ev_priv = tk.StringVar(value="Public")
        self._ev_cat  = tk.StringVar(value="Music")

        plat_row = ctk.CTkFrame(pub_in, fg_color=_DC, corner_radius=0)
        plat_row.pack(anchor="w", pady=(0,12))
        for bvar, icon, txt in [
                (self._ev_yt,  "▶", "YouTube"),
                (self._ev_ig, "📱", "Instagram")]:
            pf = ctk.CTkFrame(plat_row, fg_color=_DE, corner_radius=8,
                              border_width=1, border_color=_DS)
            pf.pack(side="left", padx=(0,10), ipadx=14, ipady=10)
            top = ctk.CTkFrame(pf, fg_color=_DE, corner_radius=0)
            top.pack(anchor="w")
            ctk.CTkLabel(top, text=f"{icon}  {txt}",
                         font=ctk.CTkFont(family=_FONT,size=10,weight="bold"),
                         text_color=_DF, fg_color="transparent").pack(side="left", padx=(0,10))
            ToggleSwitch(top, bvar, bg=_DE).pack(side="left")

        opts_row = ctk.CTkFrame(pub_in, fg_color=_DC, corner_radius=0)
        opts_row.pack(anchor="w")
        fo1 = ctk.CTkFrame(opts_row, fg_color=_DC, corner_radius=0)
        fo1.pack(side="left", padx=(0,20))
        sublabel(fo1, "Statut YouTube", 9).pack(anchor="w", pady=(0,4))
        PillDropdown(fo1, self._ev_priv,
                     ["Public", "Non répertorié", "Privé"],
                     bg=_DC, width=14).pack(anchor="w")
        fo2 = ctk.CTkFrame(opts_row, fg_color=_DC, corner_radius=0)
        fo2.pack(side="left")
        sublabel(fo2, "Catégorie YouTube", 9).pack(anchor="w", pady=(0,4))
        PillDropdown(fo2, self._ev_cat,
                     list(CATEGORIES.keys()),
                     bg=_DC, width=18).pack(anchor="w")

        # ── SEO & Contenu ─────────────────────────────────────────────
        seo_card = card(wrap)
        seo_in   = ctk.CTkFrame(seo_card, fg_color=_DC, corner_radius=0)
        seo_in.pack(fill="x", padx=20, pady=16)
        label(seo_in,"Titre & SEO",14,True).pack(anchor="w",pady=(0,10))

        self._ev_title = tk.StringVar()
        self._ev_tags  = tk.StringVar()

        gen_panel = ctk.CTkFrame(seo_in, fg_color=_DE, corner_radius=8,
                                 border_width=1, border_color=_DS)
        gen_panel.pack(fill="x", pady=(0,12))
        gp_in = ctk.CTkFrame(gen_panel, fg_color=_DE, corner_radius=0)
        gp_in.pack(fill="x", padx=14, pady=10)

        label(gp_in,"Générer le contenu",11,True).pack(anchor="w",pady=(0,6))

        self._ev_gen_mode = tk.StringVar(value="auto")
        SegmentedPill(gp_in, self._ev_gen_mode,
                      [("auto", "  🤖 IA Auto  "), ("profile", "  📁 Profil  ")],
                      bg=_DE, command=self._ev_toggle_gen_mode
                      ).pack(anchor="w", pady=(0,8))

        self._ev_gen_auto_frame = ctk.CTkFrame(gp_in, fg_color=_DE, corner_radius=0)
        self._ev_gen_auto_frame.pack(fill="x", pady=(0,4))
        af_row = ctk.CTkFrame(self._ev_gen_auto_frame, fg_color=_DE, corner_radius=0)
        af_row.pack(fill="x")
        fa_genre = ctk.CTkFrame(af_row, fg_color=_DE, corner_radius=0)
        fa_genre.pack(side="left",padx=(0,16))
        ctk.CTkLabel(fa_genre, text="Genre (optionnel)",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        self._ev_auto_genre = tk.StringVar(value="Aléatoire")
        PillDropdown(fa_genre, self._ev_auto_genre,
                     ["Aléatoire"]+list(seo_module.ARTIST_TAGS.keys()),
                     bg=_DE, width=16).pack(anchor="w")
        fa_art = ctk.CTkFrame(af_row, fg_color=_DE, corner_radius=0)
        fa_art.pack(side="left")
        ctk.CTkLabel(fa_art, text="Artiste (optionnel)",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        self._ev_auto_artist = tk.StringVar()
        entry(fa_art, self._ev_auto_artist, width=160).pack(ipady=2)

        self._ev_gen_profile_frame = ctk.CTkFrame(gp_in, fg_color=_DE, corner_radius=0)
        ev_pb, _, _ = self._make_profile_banner(
            self._ev_gen_profile_frame,
            lambda name: self._ev_load_profile(name))
        ev_pb.pack(anchor="w", pady=(0,4))
        self._ev_gen_profile_frame.pack_forget()

        AppleBtn(gp_in,"🤖  Générer le contenu automatiquement",
                 command=self._ev_gen_content,
                 style="primary", font=(_FONT,10,"bold"),
                 padx=18, pady=9).pack(anchor="w", pady=(6,0))
        self._ev_ai_status = ctk.CTkLabel(gp_in, text="",
                                          font=ctk.CTkFont(family=_FONT,size=9),
                                          text_color=_DU, fg_color="transparent")
        self._ev_ai_status.pack(anchor="w", pady=(4,0))

        row1 = ctk.CTkFrame(seo_in, fg_color=_DC, corner_radius=0)
        row1.pack(fill="x",pady=(0,8))
        ctk.CTkLabel(row1, text="Titre",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        entry(row1, self._ev_title, width=500).pack(fill="x")

        ctk.CTkLabel(seo_in, text="Description YouTube",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent"
                     ).pack(anchor="w", pady=(8,4))
        self._ev_desc = ctk.CTkTextbox(seo_in,
                                       fg_color=_DE, border_color=_DS,
                                       text_color=_DF, corner_radius=8,
                                       border_width=1, height=100,
                                       font=ctk.CTkFont(family=_FONT,size=9))
        self._ev_desc.pack(fill="x")

        ctk.CTkLabel(seo_in, text="Légende Instagram",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent"
                     ).pack(anchor="w", pady=(8,4))
        self._ev_ig_cap = ctk.CTkTextbox(seo_in,
                                         fg_color=_DE, border_color=_DS,
                                         text_color=_DF, corner_radius=8,
                                         border_width=1, height=70,
                                         font=ctk.CTkFont(family=_FONT,size=9))
        self._ev_ig_cap.pack(fill="x")

        # ── Progression & bouton ──────────────────────────────────────
        prog_card = card(wrap)
        prog_in = ctk.CTkFrame(prog_card, fg_color=_DC, corner_radius=0)
        prog_in.pack(fill="x",padx=20,pady=14)
        self._ev_bar = SmoothBar(prog_in, height=6)
        self._ev_bar.pack(fill="x",pady=(0,6))
        self._ev_status = tk.StringVar(value="")
        ctk.CTkLabel(prog_in, textvariable=self._ev_status,
                     font=ctk.CTkFont(family=_FONT,size=10),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")

        foot = ctk.CTkFrame(wrap, fg_color=_DK, corner_radius=0)
        foot.pack(fill="x",pady=(10,0))
        self._ev_btn = AppleBtn(foot,"🚀  Publier sur toutes les plateformes",
                                command=self._ev_publish,
                                style="primary",
                                font=(_FONT,11,"bold"),padx=24,pady=11)
        self._ev_btn.pack(side="right")

    # ══════════════════════════════════════════════════════════════════
    # PAGE 2 — CONNEXIONS
    # ══════════════════════════════════════════════════════════════════
    def _build_connexions(self, p):
        wrap = ctk.CTkScrollableFrame(p, fg_color=_DK, scrollbar_button_color=_DS,
                                      scrollbar_button_hover_color=_DE)
        wrap.pack(fill="both", expand=True, padx=0, pady=0)
        inner_wrap = ctk.CTkFrame(wrap, fg_color=_DK, corner_radius=0)
        inner_wrap.pack(fill="both", expand=True, padx=40, pady=30)
        wrap = inner_wrap  # alias pour le reste de la méthode

        hero = ctk.CTkFrame(wrap, fg_color=_DK, corner_radius=0)
        hero.pack(fill="x", pady=(0,20))
        acc = ctk.CTkFrame(hero, fg_color=BLUE, width=4, height=52, corner_radius=2)
        acc.pack(side="left", padx=(0,14))
        acc.pack_propagate(False)
        htxt = ctk.CTkFrame(hero, fg_color=_DK, corner_radius=0)
        htxt.pack(side="left")
        label(htxt,"Connexions",24,True).pack(anchor="w")
        sublabel(htxt,"Configure tes comptes YouTube et Instagram.",10
                 ).pack(anchor="w",pady=(3,0))

        # ── YouTube ───────────────────────────────────────────────────
        yt_card = card(wrap)
        yt_in = ctk.CTkFrame(yt_card, fg_color=_DC, corner_radius=0)
        yt_in.pack(fill="x", padx=20, pady=16)

        yt_hdr = ctk.CTkFrame(yt_in, fg_color=_DC, corner_radius=0)
        yt_hdr.pack(fill="x", pady=(0,10))
        label(yt_hdr,"▶  YouTube",14,True).pack(side="left")
        self._yt_dot = AnimatedDot(yt_hdr, bg=_DC)
        self._yt_dot.pack(side="right", padx=(0,2))

        sublabel(yt_in,
            "Clique sur Connecter, une fenêtre Google s'ouvrira pour autoriser l'accès.",10
            ).pack(anchor="w", pady=(0,10))

        self._yt_btn = AppleBtn(yt_in,"Connecter YouTube",
                                command=self._connect_yt,
                                style="primary",
                                font=(_FONT,10,"bold"),padx=18,pady=9)
        self._yt_btn.pack(anchor="w")

        sep(wrap)

        # ── Instagram ─────────────────────────────────────────────────
        ig_card = card(wrap)
        ig_in = ctk.CTkFrame(ig_card, fg_color=_DC, corner_radius=0)
        ig_in.pack(fill="x", padx=20, pady=16)

        label(ig_in,"📱  Instagram",14,True).pack(anchor="w",pady=(0,10))

        self._ig_method = tk.StringVar(value="session")
        mrow = ctk.CTkFrame(ig_in, fg_color=_DC, corner_radius=0)
        mrow.pack(anchor="w", pady=(0,12))

        def toggle():
            if self._ig_method.get()=="session":
                self._pw_frame.pack_forget()
                self._sid_frame.pack(anchor="w",fill="x")
            else:
                self._sid_frame.pack_forget()
                self._pw_frame.pack(anchor="w",fill="x")

        SegmentedPill(mrow, self._ig_method,
                      [("session", "  Cookie sessionid  "), ("password", "  ID + mot de passe  ")],
                      bg=_DC, command=toggle).pack(anchor="w")

        self._sid_frame = ctk.CTkFrame(ig_in, fg_color=_DC, corner_radius=0)
        self._sid_frame.pack(anchor="w", fill="x")

        # ── Guide pas-à-pas ──────────────────────────────────────────
        guide = ctk.CTkFrame(self._sid_frame, fg_color=_DE, corner_radius=8)
        guide.pack(fill="x", pady=(0, 10))

        # Header guide
        g_head = ctk.CTkFrame(guide, fg_color=_DE, corner_radius=0)
        g_head.pack(fill="x", padx=12, pady=(10, 6))
        ctk.CTkLabel(g_head, text="Comment trouver ton sessionid ?",
                     font=ctk.CTkFont(family=_FONT, size=10, weight="bold"),
                     text_color=_DF, fg_color="transparent").pack(side="left")
        AppleBtn(g_head, text="Ouvrir Instagram →", style="primary",
                 font=ctk.CTkFont(family=_FONT, size=10),
                 height=24,
                 command=lambda: __import__("webbrowser").open("https://www.instagram.com")
                 ).pack(side="right")

        # Étapes
        steps = [
            ("1", "Connecte-toi sur Instagram dans ton navigateur"),
            ("2", "Appuie sur  F12  (outils développeur)"),
            ("3", "Onglet  Application  →  Cookies  →  instagram.com"),
            ("4", "Cherche la ligne  sessionid  — copie la valeur"),
        ]
        for num, txt in steps:
            row = ctk.CTkFrame(guide, fg_color=_DE, corner_radius=0)
            row.pack(fill="x", padx=12, pady=1)
            # Badge numéro
            badge = ctk.CTkFrame(row, fg_color=BLUE, corner_radius=10, width=18, height=18)
            badge.pack(side="left", padx=(0, 8))
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=num,
                         font=ctk.CTkFont(family=_FONT, size=9, weight="bold"),
                         text_color="#ffffff", fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(row, text=txt,
                         font=ctk.CTkFont(family=_FONT, size=10),
                         text_color=_DU, fg_color="transparent").pack(side="left")
        ctk.CTkFrame(guide, fg_color=_DE, height=8, corner_radius=0).pack()  # spacer bas

        # ── Champ sessionid + bouton Coller ──────────────────────────
        sid_row = ctk.CTkFrame(self._sid_frame, fg_color=_DC, corner_radius=0)
        sid_row.pack(anchor="w")
        ctk.CTkLabel(sid_row, text="sessionid :",
                     font=ctk.CTkFont(family=_FONT, size=10, weight="bold"),
                     text_color=_DF, fg_color="transparent").pack(side="left")
        self._sid_var = tk.StringVar()
        entry(sid_row, self._sid_var, width=260).pack(side="left", padx=(8, 6))

        def _paste_sid():
            try:
                val = self.clipboard_get().strip()
                if val:
                    self._sid_var.set(val)
            except Exception:
                pass

        AppleBtn(sid_row, text="Coller", style="secondary",
                 font=ctk.CTkFont(family=_FONT, size=10),
                 height=28,
                 command=_paste_sid).pack(side="left")

        self._pw_frame = ctk.CTkFrame(ig_in, fg_color=_DC, corner_radius=0)
        self._ig_user_var = tk.StringVar()
        self._ig_pass_var = tk.StringVar()
        for lbl_txt, var, show in [
            ("Identifiant",self._ig_user_var,""),
            ("Mot de passe",self._ig_pass_var,"●")]:
            r = ctk.CTkFrame(self._pw_frame, fg_color=_DC, corner_radius=0)
            r.pack(anchor="w", pady=3)
            ctk.CTkLabel(r, text=lbl_txt,
                         font=ctk.CTkFont(family=_FONT,size=10,weight="bold"),
                         text_color=_DF, fg_color="transparent",
                         width=100, anchor="w").pack(side="left")
            entry(r, var, show=show, width=240).pack(side="left", padx=(8,0))

        sep(ig_in)

        brow = ctk.CTkFrame(ig_in, fg_color=_DC, corner_radius=0)
        brow.pack(fill="x")
        self._ig_conn_btn = AppleBtn(brow,"Se connecter",
                                     command=self._ig_connect,
                                     style="primary",
                                     font=(_FONT,10,"bold"),padx=16,pady=8)
        self._ig_conn_btn.pack(side="left")
        self._ig_dot = AnimatedDot(brow, bg=_DC)
        self._ig_dot.pack(side="left", padx=(8,2))
        self._ig_conn_lbl = ctk.CTkLabel(brow, text="Non connecté",
                                         font=ctk.CTkFont(family=_FONT,size=10),
                                         text_color=_DU, fg_color="transparent")
        self._ig_conn_lbl.pack(side="left")

        self._2fa_frame = ctk.CTkFrame(ig_in, fg_color=_DC, corner_radius=0)
        self._2fa_frame.pack(anchor="w",fill="x")
        ctk.CTkLabel(self._2fa_frame, text="Code 2FA :",
                     font=ctk.CTkFont(family=_FONT,size=10,weight="bold"),
                     text_color=ORANGE, fg_color="transparent").pack(side="left")
        self._2fa_var = tk.StringVar()
        entry(self._2fa_frame, self._2fa_var, width=100).pack(side="left", padx=8)
        AppleBtn(self._2fa_frame,"Valider",command=self._ig_2fa,
                 style="secondary",font=(_FONT,9,"bold"),
                 padx=12,pady=6).pack(side="left")
        self._2fa_frame.pack_forget()

    def _build_file_row(self, parent, title, hint, cmd, lbl_attr,
                        exts, drop_fn):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=20, pady=14)

        left = tk.Frame(row, bg=CARD)
        left.pack(side="left", fill="x", expand=True)
        label(left, title, 12, True).pack(anchor="w")
        sublabel(left, hint, 10).pack(anchor="w", pady=(2,8))
        lbl = tk.Label(left, text="Aucun fichier sélectionné",
                       font=(_FONT,10),
                       bg=CARD, fg=SUB)
        lbl.pack(anchor="w")
        setattr(self, lbl_attr, lbl)

        AppleBtn(row,"Choisir",command=cmd,style="secondary",
                 font=(_FONT,9,"bold"),padx=14,pady=7).pack(
                     side="right", anchor="center")

        if DND_OK:
            parent.drop_target_register(DND_FILES)
            parent.dnd_bind("<<Drop>>", drop_fn)


    # ──────────────────────────────────────────────────────────────────
    # UI HELPERS
    # ──────────────────────────────────────────────────────────────────
    def _apple_combo(self, parent, lbl, var, values, row, width):
        tk.Label(parent, text=lbl, font=(_FONT,9,"bold"),
                 bg=CARD, fg=SUB).grid(row=row, column=0,
                 sticky="w", padx=(0,8), pady=2)
        cb = PillDropdown(parent, var, values, bg=CARD, width=width)
        cb.grid(row=row+1, column=0, sticky="w", padx=(0,20), pady=(0,8))
        return cb

    def _apple_entry(self, parent, lbl, var, row, width):
        tk.Label(parent, text=lbl, font=(_FONT,9,"bold"),
                 bg=CARD, fg=SUB).grid(row=row, column=2,
                 sticky="w", padx=(0,8), pady=2)
        e = tk.Entry(parent, textvariable=var,
                     font=(_FONT,10), bg=BG, fg=TEXT,
                     insertbackground=TEXT, relief="flat",
                     highlightthickness=1, highlightbackground=BORDER,
                     width=width)
        e.grid(row=row+1, column=2, sticky="w", padx=(0,20),
               pady=(0,8), ipady=6)
        return e

    # ══════════════════════════════════════════════════════════════════
    # HELPERS PROFIL SEO — réutilisable dans tous les onglets
    # ══════════════════════════════════════════════════════════════════

    def _make_profile_banner(self, parent, on_load_fn,
                              bg_color=None, status_attr=None):
        """
        Bandeau compact « 📁 Profil SEO » pour n'importe quel onglet.
        on_load_fn(profile_name) est appelé quand l'utilisateur clique Charger.
        Retourne le frame.
        """
        bg_color = bg_color or _DE
        frame = tk.Frame(parent, bg=bg_color)
        tk.Label(frame, text="📁 Profil SEO :",
                 font=(_FONT,9,"bold"),
                 bg=bg_color, fg=_DU).pack(side="left", padx=(0,8))
        var = tk.StringVar()
        names = seo_module.profile_names()
        cb  = PillDropdown(frame, var,
                           names,
                           bg=bg_color, width=22)
        cb.pack(side="left", padx=(0,8))
        if names: var.set(names[0])

        status_lbl = tk.Label(frame, text="", font=(_FONT,8),
                              bg=bg_color, fg=GREEN)
        status_lbl.pack(side="left", padx=(8,0))

        def load():
            name = var.get()
            if not name: return
            # Refresh values in case profiles changed
            cb._opts = seo_module.profile_names()
            on_load_fn(name)
            status_lbl.config(text=f"✓ {name}")

        AppleBtn(frame, "Charger", command=load, style="secondary",
                 font=(_FONT,9,"bold"), padx=10, pady=5
                 ).pack(side="left", padx=(0,6))

        if status_attr:
            setattr(self, status_attr, (var, cb))
        return frame, var, cb

    def _gen_from_profile(self, name: str) -> dict:
        """
        Génère titre + description + tags + légende IG à partir d'un profil.
        Retourne un dict avec: title, desc, tags_str, ig_full.
        """
        p       = seo_module.load_profiles().get(name, {})
        a1      = p.get("artist1", "") or name
        a2      = p.get("artist2", "")
        beat    = p.get("beat_name", "") or "Beat"
        genre   = p.get("genre", "Trap")
        contact = p.get("contact", "")
        free    = p.get("free", True)
        custom  = p.get("custom_hashtags", "")
        tags_list = seo_module.generate_beat_hashtags(a1, a2, genre, custom, 30)
        title     = seo_module.generate_beat_title(a1, beat, a2, free)
        desc      = seo_module.generate_beat_description(
                        a1, beat, a2, genre, contact, free)
        ig_cap    = seo_module.generate_beat_ig_caption(a1, beat, a2, free)
        ig_tags   = seo_module.format_ig_tags(tags_list)
        return {
            "title":   title,
            "desc":    desc,
            "tags":    seo_module.format_yt_tags(tags_list),
            "ig_full": f"{ig_cap}\n\n{ig_tags}",
        }

    # ══════════════════════════════════════════════════════════════════
    # LOGIQUE UPLOAD
    # ══════════════════════════════════════════════════════════════════
    def _browse(self):
        for p in filedialog.askopenfilenames(
                title="Vidéos",
                filetypes=[("Vidéos","*.mp4 *.mov *.avi *.mkv *.wmv *.flv *.webm"),
                            ("Tous","*.*")]):
            self._add_file(Path(p))

    def _browse_folder(self):
        d = filedialog.askdirectory(title="Dossier")
        if d:
            for f in sorted(Path(d).iterdir()):
                if f.suffix.lower() in SUPPORTED_EXT: self._add_file(f)

    def _on_drop(self, e):
        for p in self.tk.splitlist(e.data):
            path = Path(p)
            if path.is_dir():
                for f in sorted(path.iterdir()):
                    if f.suffix.lower() in SUPPORTED_EXT: self._add_file(f)
            elif path.suffix.lower() in SUPPORTED_EXT:
                self._add_file(path)

    def _add_file(self, path):
        if any(i["path"]==path for i in self.queue): return
        self.queue.append({"path":path,
            "title":path.stem.replace("_"," ").replace("-"," ").title(),
            "status":"en attente","progress":0,"youtube_id":None})
        self._render_queue()

    def _clear_queue(self):
        if self.uploading:
            messagebox.showwarning("En cours","Arrête l'upload d'abord."); return
        self.queue.clear(); self._render_queue()

    def _render_queue(self):
        for w in self._rows: w.destroy()
        self._rows.clear()
        if not self.queue:
            self._empty_lbl.pack(expand=True); return
        self._empty_lbl.pack_forget()
        for i, item in enumerate(self.queue):
            row = self._make_row(i, item)
            row.pack(fill="x")
            self._rows.append(row)

    def _make_row(self, idx, item):
        bg = CARD if idx%2==0 else CARD2
        row = tk.Frame(self._q_card, bg=bg,
                       highlightthickness=1,
                       highlightbackground=SHADOW)
        row.pack(fill="x")

        dot_c = {
            "en attente": BORDER,
            "upload...":  ORANGE,
            "terminé":    GREEN,
            "erreur":     RED,
        }.get(item["status"], BORDER)

        tk.Label(row, text="⬤", font=(_FONT,9),
                 bg=bg, fg=dot_c).pack(side="left", padx=(14,6), pady=12)

        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="x", expand=True, pady=10)

        nr = tk.Frame(info, bg=bg)
        nr.pack(fill="x")
        tk.Label(nr, text=item["path"].name,
                 font=(_FONT,10,"bold"), bg=bg, fg=TEXT,
                 anchor="w").pack(side="left")
        mb = item["path"].stat().st_size/(1024*1024) if item["path"].exists() else 0
        tk.Label(nr, text=f"  {mb:.1f} MB",
                 font=(_FONT,9), bg=bg, fg=BORDER).pack(side="left")

        if item["status"]=="upload...":
            pb = SmoothBar(info, height=4, color=BLUE, bg=bg)
            pb.config(bg=bg)
            pb.pack(fill="x", pady=(4,0))
            pb.set(item["progress"])
            item["_pb"] = pb
        elif item["status"]=="terminé" and item.get("youtube_id"):
            tk.Label(info, text=f"✓  youtu.be/{item['youtube_id']}",
                     font=(_FONT,9), bg=bg, fg=GREEN).pack(anchor="w")
        elif item["status"]=="erreur":
            tk.Label(info, text="✗  Erreur lors de l'upload",
                     font=(_FONT,9), bg=bg, fg=RED).pack(anchor="w")
        else:
            tk.Label(info, text=item["status"],
                     font=(_FONT,9), bg=bg, fg=SUB).pack(anchor="w")

        if item["status"] not in ("upload...",):
            x = tk.Label(row, text="✕", font=(_FONT,11),
                         bg=bg, fg=BORDER, cursor="hand2")
            x.pack(side="right", padx=14)
            x.bind("<Button-1>", lambda e, i=idx: self._del(i))
            x.bind("<Enter>", lambda e, w=x: w.config(fg=RED))
            x.bind("<Leave>", lambda e, w=x: w.config(fg=BORDER))
        return row

    def _del(self, idx):
        if 0<=idx<len(self.queue):
            del self.queue[idx]; self._render_queue()

    # ══════════════════════════════════════════════════════════════════
    # YOUTUBE
    # ══════════════════════════════════════════════════════════════════
    def _connect_yt(self):
        if not GOOGLE_OK:
            messagebox.showerror("Erreur","Lance installer.bat d'abord."); return
        if not CREDENTIALS_FILE.exists():
            messagebox.showerror("Manquant","client_secrets.json introuvable."); return
        self._yt_dot.config(fg=ORANGE)
        self._yt_btn.configure(text="Connexion...")
        def run():
            try:
                self.youtube = get_youtube()
                self.after(0, lambda: self._yt_dot.config(fg=GREEN))
                self.after(0, lambda: self._yt_btn.configure(text="YouTube ✓"))
                self.after(0, self._ev_sync_status)
            except Exception as e:
                err = str(e)
                self.after(0, lambda: self._yt_dot.config(fg=RED))
                self.after(0, lambda: self._yt_btn.configure(text="Connecter YouTube"))
                self.after(0, lambda m=err: messagebox.showerror("Erreur",m))
        threading.Thread(target=run, daemon=True).start()

    def _privacy(self, var):
        return {"Public":"public","Non répertorié":"unlisted",
                "Privé":"private"}.get(var.get(),"public")

    def _start_upload(self):
        if not self.youtube:
            messagebox.showwarning("Non connecté","Connecte-toi d'abord."); return
        pending = [i for i,it in enumerate(self.queue) if it["status"]=="en attente"]
        if not pending:
            messagebox.showinfo("Vide","Ajoute des vidéos d'abord."); return
        self.uploading = True; self.stop_flag = False
        self._up_btn.disable(); self._stop_btn.enable()
        threading.Thread(target=self._upload_worker,
                         args=(pending,), daemon=True).start()

    def _stop_upload(self):
        self.stop_flag = True; self._status_var.set("Arrêt...")

    def _upload_worker(self, indices):
        priv = self._privacy(self._priv_var)
        desc = self._desc_var.get()
        cat  = CATEGORIES.get(self._cat_var.get(),"22")
        for idx in indices:
            if self.stop_flag: break
            it = self.queue[idx]
            it["status"]="upload..."; it["progress"]=0
            self.after(0, self._render_queue)
            self.after(0, lambda n=it["path"].name:
                       self._status_var.set(f"Upload : {n}"))
            try:
                self._do_upload(it["path"],it["title"],desc,cat,priv,
                    cb_prog=lambda p,i=idx: self._upd(i,p),
                    cb_done=lambda v,i=idx: self._done(i,v))
            except Exception as e:
                it["status"]="erreur"
                err=str(e)
                self.after(0,lambda m=err: messagebox.showerror("Erreur",m))
            self.after(0,self._render_queue)
        self.uploading=False
        done=sum(1 for it in self.queue if it["status"]=="terminé")
        self.after(0,lambda: self._status_var.set(
            f"Terminé — {done}/{len(self.queue)} uploadée(s)"))
        self.after(0,self._up_btn.enable)
        self.after(0,self._stop_btn.disable)

    def _done(self,idx,vid): self.queue[idx]["status"]="terminé"; self.queue[idx]["youtube_id"]=vid
    def _upd(self,idx,pct):
        self.queue[idx]["progress"]=pct
        if "_pb" in self.queue[idx]: self.queue[idx]["_pb"].set(pct)

    def _do_upload(self, path, title, desc, cat, priv, cb_prog=None, cb_done=None):
        body={"snippet":{"title":title,"description":desc,"categoryId":cat},
              "status":{"privacyStatus":priv}}
        media=MediaFileUpload(str(path),mimetype="video/*",resumable=True,
                              chunksize=5*1024*1024)
        req=self.youtube.videos().insert(part="snippet,status",
                                         body=body,media_body=media)
        response=None
        while response is None:
            if self.stop_flag: return
            st,response=req.next_chunk()
            if st and cb_prog: cb_prog(int(st.progress()*100))
        if response and cb_done: cb_done(response["id"])

    # ══════════════════════════════════════════════════════════════════
    # CREATOR
    # ══════════════════════════════════════════════════════════════════
    def _pick_img(self):
        p=filedialog.askopenfilename(title="Image",
            filetypes=[("Images","*.jpg *.jpeg *.png *.bmp *.webp"),("Tous","*.*")])
        if p: self._set_img(Path(p))

    def _pick_mp3(self):
        p=filedialog.askopenfilename(title="Audio",
            filetypes=[("Audio","*.mp3 *.wav *.aac *.ogg *.flac *.m4a"),("Tous","*.*")])
        if p: self._set_mp3(Path(p))

    def _drop_img(self,e):
        paths=self.tk.splitlist(e.data)
        if paths:
            p=Path(paths[0])
            if p.suffix.lower() in IMAGE_EXT: self._set_img(p)

    def _drop_mp3(self,e):
        paths=self.tk.splitlist(e.data)
        if paths:
            p=Path(paths[0])
            if p.suffix.lower() in AUDIO_EXT: self._set_mp3(p)

    def _set_img(self,path):
        self._img_path=path
        mb=path.stat().st_size/(1024*1024)
        self._img_lbl.config(text=f"✓  {path.name}  ({mb:.1f} MB)",fg=GREEN)
        if not self._cr_title.get():
            self._cr_title.set(path.stem.replace("_"," ").replace("-"," ").title())

    def _set_mp3(self,path):
        self._mp3_path=path
        mb=path.stat().st_size/(1024*1024)
        self._mp3_lbl.config(text=f"✓  {path.name}  ({mb:.1f} MB)",fg=GREEN)
        if not self._cr_title.get():
            self._cr_title.set(path.stem.replace("_"," ").replace("-"," ").title())

    def _create_upload(self):
        if not self.youtube:
            messagebox.showwarning("Non connecté","Connecte-toi d'abord."); return
        if not self._img_path:
            messagebox.showwarning("Manquant","Sélectionne une image."); return
        if not self._mp3_path:
            messagebox.showwarning("Manquant","Sélectionne un fichier audio."); return
        title=self._cr_title.get().strip() or self._mp3_path.stem
        self._cr_btn.disable(); self._cr_bar.set(0)
        self._cr_status.set("Étape 1/2 — Création du MP4...")
        threading.Thread(target=self._creator_worker,args=(title,),daemon=True).start()

    def _creator_worker(self,title):
        tmp=Path(tempfile.gettempdir())/f"{title[:40]}_beat.mp4"
        try:
            make_mp4(self._img_path,self._mp3_path,tmp,
                     cb=lambda p: self.after(0,lambda v=p: self._cr_bar.set(v//2)))
            self.after(0,lambda: self._cr_status.set("Étape 2/2 — Upload YouTube..."))
            self.after(0,lambda: self._cr_bar.set(50))
            vid=None
            self._do_upload(tmp,title,self._cr_desc.get(),
                CATEGORIES.get(self._cr_cat.get(),"10"),
                self._privacy(self._cr_priv),
                cb_prog=lambda p: self.after(0,lambda v=p: self._cr_bar.set(50+v//2)),
                cb_done=lambda v: setattr(self,"_tmp_vid",v))
            vid=getattr(self,"_tmp_vid",None)
            self.after(0,lambda: self._cr_bar.set(100))
            url=f"https://youtu.be/{vid}" if vid else "?"
            self.after(0,lambda u=url: self._cr_status.set(f"✅ Terminé !  →  {u}"))
        except Exception as e:
            err=str(e)
            self.after(0,lambda m=err: self._cr_status.set(f"❌ {m}"))
            self.after(0,lambda m=err: messagebox.showerror("Erreur",m))
        finally:
            if tmp.exists():
                try: tmp.unlink()
                except: pass
            self.after(0,self._cr_btn.enable)

    # ══════════════════════════════════════════════════════════════════
    # INSTAGRAM
    # ══════════════════════════════════════════════════════════════════
    def _ig_connect(self):
        self._ig_dot.config(fg=ORANGE)
        self._ig_conn_lbl.configure(text="Connexion...")
        self._ig_conn_btn.disable()
        if self._ig_method.get()=="session":
            sid=self._sid_var.get().strip()
            if not sid:
                messagebox.showwarning("Vide","Colle ton sessionid.")
                self._ig_conn_btn.enable(); self._ig_dot.config(fg=BORDER)
                self._ig_conn_lbl.configure(text="Non connecté"); return
            threading.Thread(target=self._session_worker,
                             args=(sid,),daemon=True).start()
        else:
            u=self._ig_user_var.get().strip(); pw=self._ig_pass_var.get().strip()
            if not u or not pw:
                messagebox.showwarning("Vide","Remplis identifiant et mot de passe.")
                self._ig_conn_btn.enable(); self._ig_dot.config(fg=BORDER)
                self._ig_conn_lbl.configure(text="Non connecté"); return
            self._ig_puser=u; self._ig_ppass=pw
            threading.Thread(target=self._login_worker,
                             args=(u,pw,None),daemon=True).start()

    def _session_worker(self,sid):
        try:
            from instagrapi import Client
            cl=Client(); cl.login_by_sessionid(sid)
            info=cl.account_info(); self._ig_client=cl
            cl.dump_settings(str(ig_module.SESSION_FILE))
            un=info.username
            self.after(0,lambda: self._ig_dot.config(fg=GREEN))
            self.after(0,lambda u=un: self._ig_conn_lbl.configure(
                text=f"Connecté (@{u})"))
            self.after(0, self._ev_sync_status)
        except Exception as e:
            err=str(e)
            self.after(0,lambda: self._ig_dot.config(fg=RED))
            self.after(0,lambda: self._ig_conn_lbl.configure(text="Erreur"))
            self.after(0,lambda m=err: messagebox.showerror("Erreur Instagram",m))
        finally:
            self.after(0,self._ig_conn_btn.enable)

    def _ig_2fa(self):
        code=self._2fa_var.get().strip()
        if not code: return
        self._ig_conn_lbl.configure(text="Vérification...")
        threading.Thread(target=self._login_worker,
                         args=(self._ig_puser,self._ig_ppass,code),
                         daemon=True).start()

    def _login_worker(self,u,pw,code):
        try:
            cl=ig_module.login(u,pw,verification_code=code)
            self._ig_client=cl
            self.after(0,lambda: self._ig_dot.config(fg=GREEN))
            self.after(0,lambda: self._ig_conn_lbl.configure(
                text=f"Connecté (@{u})"))
            self.after(0,self._2fa_frame.pack_forget)
            self.after(0, self._ev_sync_status)
        except Exception as e:
            et=type(e).__name__; em=str(e)
            if "TwoFactorRequired" in et or "two_factor" in em.lower():
                self.after(0,lambda: self._ig_dot.config(fg=ORANGE))
                self.after(0,lambda: self._ig_conn_lbl.configure(text="Code 2FA requis"))
                self.after(0,lambda: self._2fa_frame.pack(anchor="w",pady=(8,0)))
            else:
                self.after(0,lambda: self._ig_dot.config(fg=RED))
                self.after(0,lambda: self._ig_conn_lbl.configure(text="Erreur"))
                self.after(0,lambda m=em: messagebox.showerror("Erreur",m))
        finally:
            self.after(0,self._ig_conn_btn.enable)

    def _ig_pick_vid(self):
        p=filedialog.askopenfilename(title="Vidéo Reel",
            filetypes=[("Vidéos","*.mp4 *.mov *.avi"),("Tous","*.*")])
        if p:
            path=Path(p); self._ig_vid_path=path
            mb=path.stat().st_size/(1024*1024)
            self._ig_vid_lbl.config(
                text=f"✓  {path.name}  ({mb:.1f} MB)",fg=GREEN)

    def _ig_pick_cov(self):
        p=filedialog.askopenfilename(title="Miniature",
            filetypes=[("Images","*.jpg *.jpeg *.png"),("Tous","*.*")])
        if p:
            self._ig_cov_path=Path(p)
            self._ig_cov_lbl.config(text=f"Miniature : {Path(p).name}",fg=SUB)

    def _ig_upload(self):
        if not self._ig_client:
            messagebox.showwarning("Non connecté","Connecte-toi d'abord."); return
        if not self._ig_vid_path:
            messagebox.showwarning("Manquant","Sélectionne une vidéo."); return
        caption=self._ig_cap.get("1.0","end").strip()
        self._ig_up_btn.disable(); self._ig_bar.set(0)
        self._ig_status.set("Préparation...")
        threading.Thread(target=self._ig_worker,args=(caption,),daemon=True).start()

    def _ig_worker(self,caption):
        def prog(pct,msg=""):
            self.after(0,lambda p=pct: self._ig_bar.set(p))
            if msg: self.after(0,lambda m=msg: self._ig_status.set(m))
        try:
            url=ig_module.upload_reel(self._ig_client,self._ig_vid_path,
                                       caption,self._ig_cov_path,
                                       progress_cb=prog)
            self.after(0,lambda: self._ig_bar.set(100))
            self.after(0,lambda u=url: self._ig_status.set(f"✅ Publié !  →  {u}"))
        except Exception as e:
            err=str(e)
            self.after(0,lambda m=err: self._ig_status.set(f"❌ {m}"))
            self.after(0,lambda m=err: messagebox.showerror("Erreur Instagram",m))
        finally:
            self.after(0,self._ig_up_btn.enable)

    # ── Logique Partout ───────────────────────────────────────────────────────

    def _ev_toggle_source(self):
        if self._ev_mode.get()=="video":
            self._ev_mp3img_frame.pack_forget()
            self._ev_vid_frame.pack(fill="x")
        else:
            self._ev_vid_frame.pack_forget()
            self._ev_mp3img_frame.pack(fill="x")

    def _ev_pick_vid(self):
        p=filedialog.askopenfilename(title="Vidéo",
            filetypes=[("Vidéos","*.mp4 *.mov *.avi *.mkv"),("Tous","*.*")])
        if p:
            self._ev_vid_path=Path(p)
            mb=self._ev_vid_path.stat().st_size/(1024*1024)
            self._ev_vid_lbl.configure(
                text=f"✓  {self._ev_vid_path.name}  ({mb:.1f} MB)", text_color=GREEN)
            if not self._ev_title.get():
                self._ev_title.set(
                    self._ev_vid_path.stem.replace("_"," ").replace("-"," ").title())

    def _ev_pick_img(self):
        p=filedialog.askopenfilename(title="Image",
            filetypes=[("Images","*.jpg *.jpeg *.png *.webp"),("Tous","*.*")])
        if p:
            self._ev_img_path=Path(p)
            self._ev_img_lbl.configure(text=f"Image : ✓ {Path(p).name}", text_color=GREEN)

    def _ev_pick_mp3(self):
        p=filedialog.askopenfilename(title="Audio",
            filetypes=[("Audio","*.mp3 *.wav *.aac *.flac"),("Tous","*.*")])
        if p:
            self._ev_mp3_path=Path(p)
            self._ev_mp3_lbl.configure(text=f"Audio : ✓ {Path(p).name}", text_color=GREEN)
            if not self._ev_title.get():
                self._ev_title.set(
                    Path(p).stem.replace("_"," ").replace("-"," ").title())

    def _ev_toggle_gen_mode(self):
        if self._ev_gen_mode.get() == "auto":
            self._ev_gen_profile_frame.pack_forget()
            self._ev_gen_auto_frame.pack(fill="x", pady=(0,4))
        else:
            self._ev_gen_auto_frame.pack_forget()
            self._ev_gen_profile_frame.pack(fill="x", pady=(0,4))

    def _ev_sync_status(self):
        """Met à jour les indicateurs YouTube/Instagram dans Publier Partout."""
        if not hasattr(self, '_ev_yt_dot'): return
        if self.youtube:
            self._ev_yt_dot.config(fg=GREEN)
            self._ev_yt_lbl.configure(text="YouTube ✓")
        else:
            self._ev_yt_dot.config(fg=BORDER)
            self._ev_yt_lbl.configure(text="YouTube — non connecté")
        if self._ig_client:
            self._ev_ig_dot.config(fg=GREEN)
            self._ev_ig_lbl.configure(text="Instagram ✓")
        else:
            self._ev_ig_dot.config(fg=BORDER)
            self._ev_ig_lbl.configure(text="Instagram — non connecté")

    def _ev_load_profile(self, name: str):
        """Charge un profil SEO dans les champs de Publier Partout."""
        d = self._gen_from_profile(name)
        self._ev_title.set(d["title"])
        self._ev_desc.delete("1.0","end")
        self._ev_desc.insert("1.0", d["desc"])
        self._ev_ig_cap.delete("1.0","end")
        self._ev_ig_cap.insert("1.0", d["ig_full"])
        self._ev_ai_status.configure(text=f"✓ Profil « {name} » chargé", text_color=GREEN)

    def _ev_gen_content(self):
        """Génère titre, description, légende — sans clé API."""
        mode = self._ev_gen_mode.get()
        self._ev_ai_status.configure(text="Génération…", text_color=ORANGE)
        self.update_idletasks()
        try:
            if mode == "profile":
                # handled by _ev_load_profile via the banner
                self._ev_ai_status.configure(text="Charge un profil via le sélecteur.", text_color=_DU)
                return
            # Mode auto
            genre   = self._ev_auto_genre.get()
            if genre == "Aléatoire": genre = None
            a1_hint = self._ev_auto_artist.get().strip()
            res = seo_module.generate_auto(
                genre=genre, artist1_hint=a1_hint, free=True)
            self._ev_title.set(res["yt_title"])
            self._ev_desc.delete("1.0","end")
            self._ev_desc.insert("1.0", res["yt_description"])
            ig_full = res["ig_caption"] + "\n\n" + res["ig_hashtags"]
            self._ev_ig_cap.delete("1.0","end")
            self._ev_ig_cap.insert("1.0", ig_full)
            info = res["artist1"]
            if res.get("artist2"): info += f" × {res['artist2']}"
            self._ev_ai_status.configure(
                text=f'✅  {info} — "{res["beat_name"]}"', text_color=GREEN)
        except Exception as e:
            self._ev_ai_status.configure(text=f"❌ {str(e)[:60]}", text_color=RED)

    def _ev_publish(self):
        self._ev_sync_status()
        if not self._ev_yt.get() and not self._ev_ig.get():
            messagebox.showwarning("Aucune plateforme",
                "Sélectionne au moins une plateforme."); return
        title=self._ev_title.get().strip()
        if not title:
            messagebox.showwarning("Titre manquant",
                "Remplis le titre ou génère le contenu d'abord."); return
        if self._ev_yt.get() and not self.youtube:
            messagebox.showwarning("YouTube non connecté",
                "Clique sur « Connecter YouTube » dans cette page\n"
                "puis suis les instructions Google OAuth."); return
        if self._ev_ig.get() and not self._ig_client:
            messagebox.showwarning("Instagram non connecté",
                "Va dans l'onglet 📱 Instagram, connecte-toi,\n"
                "puis reviens ici."); return

        self._ev_btn.disable()
        self._ev_bar.set(0)
        self._ev_status.set("Préparation...")
        threading.Thread(target=self._ev_worker,daemon=True).start()

    def _ev_worker(self):
        import shutil
        title      = self._ev_title.get().strip()
        cat        = seo_module.HASHTAGS.keys().__iter__().__next__()
        cat        = self._ev_cat.get()
        priv       = self._privacy(self._ev_priv)
        yt_desc    = self._ev_desc.get("1.0","end").strip()
        ig_caption = self._ev_ig_cap.get("1.0","end").strip()
        custom_tags= self._ev_tags.get().strip()
        cat_id     = seo_module.HASHTAGS.get(cat,{})

        from seo import HASHTAGS as HB
        cat_id_yt  = {"Music":"10","Gaming":"20","People & Blogs":"22",
                      "Entertainment":"24","Science & Tech":"28",
                      "Sports":"17","Education":"27"}.get(cat,"22")

        # tags YouTube
        tags_list  = seo_module.get_hashtags(cat, custom_tags, 30)
        yt_tags    = seo_module.format_yt_tags(tags_list)
        if not yt_desc:
            yt_desc = seo_module.auto_description_yt(title, cat)
        if not ig_caption:
            ig_caption = seo_module.auto_caption_ig(title, tags_list[:5])

        tmp_yt = tmp_ig = None
        try:
            # ── Étape 1 : créer la vidéo source ──
            self.after(0,lambda: self._ev_status.set("Création de la vidéo..."))
            self.after(0,lambda: self._ev_bar.set(5))

            if self._ev_mode.get()=="mp3img":
                if not self._ev_img_path or not self._ev_mp3_path:
                    raise RuntimeError("Sélectionne image et audio.")
                tmp_yt = Path(tempfile.gettempdir())/f"{title[:30]}_ev_yt.mp4"
                make_mp4(self._ev_img_path, self._ev_mp3_path, tmp_yt,
                         cb=lambda p: self.after(0,
                             lambda v=p: self._ev_bar.set(5+v*0.2)))
                src = tmp_yt
            else:
                if not self._ev_vid_path:
                    raise RuntimeError("Sélectionne une vidéo.")
                src = self._ev_vid_path

            self.after(0,lambda: self._ev_bar.set(25))
            step = 0
            total_steps = self._ev_yt.get() + self._ev_ig.get()

            # ── Étape 2 : YouTube ──
            if self._ev_yt.get():
                self.after(0,lambda: self._ev_status.set(
                    "Upload YouTube en cours..."))
                yt_vid = None
                self._do_upload(
                    src, title, yt_desc, cat_id_yt, priv,
                    cb_prog=lambda pp: self.after(0,
                        lambda v=pp: self._ev_bar.set(25+v*0.35)),
                    cb_done=lambda v: setattr(self,"_ev_yt_id",v))
                yt_vid = getattr(self,"_ev_yt_id",None)
                step += 1
                url_yt = f"https://youtu.be/{yt_vid}" if yt_vid else "?"
                self.after(0,lambda u=url_yt: self._ev_status.set(
                    f"YouTube ✓ → {u}"))
                self.after(0,lambda: self._ev_bar.set(25+35))

            # ── Étape 3 : convertir en vertical pour Instagram ──
            if self._ev_ig.get():
                self.after(0,lambda: self._ev_status.set(
                    "Conversion format vertical Instagram..."))
                tmp_ig = Path(tempfile.gettempdir())/f"{title[:30]}_ev_ig.mp4"
                self._convert_vertical(src, tmp_ig)
                self.after(0,lambda: self._ev_bar.set(70))

                self.after(0,lambda: self._ev_status.set(
                    "Upload Instagram Reel..."))
                url_ig = ig_module.upload_reel(
                    self._ig_client, tmp_ig, ig_caption)
                step += 1
                self.after(0,lambda u=url_ig: self._ev_status.set(
                    f"Instagram ✓ → {u}"))
                self.after(0,lambda: self._ev_bar.set(100))

            self.after(0,lambda: self._ev_status.set(
                f"✅ Publié sur {step}/{total_steps} plateforme(s) !"))
            self.after(0,lambda: self._ev_bar.set(100))

        except Exception as e:
            err=str(e)
            self.after(0,lambda m=err: self._ev_status.set(f"❌ {m}"))
            self.after(0,lambda m=err: messagebox.showerror("Erreur",m))
        finally:
            for f in (tmp_yt, tmp_ig):
                if f and f.exists():
                    try: f.unlink()
                    except: pass
            self.after(0, self._ev_btn.enable)
            self.after(0, self._ev_btn.flash)

    def _convert_vertical(self, src, out):
        """Convertit une vidéo au format vertical 9:16 pour Instagram."""
        ff = find_ffmpeg()
        if not ff: raise RuntimeError("ffmpeg introuvable.")
        cmd = [
            ff,"-y","-i",str(src),
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
            "-c:v","libx264","-preset","fast",
            "-c:a","aac","-b:a","192k",
            str(out)
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("Conversion verticale échouée.")

    # ══════════════════════════════════════════════════════════════════
    # PAGE 5 — SEO & HASHTAGS
    # ══════════════════════════════════════════════════════════════════

    def _build_seo(self, p):
        wrap = ctk.CTkScrollableFrame(p, fg_color=_DK, scrollbar_button_color=_DS,
                                      scrollbar_button_hover_color=_DE)
        wrap.pack(fill="both", expand=True, padx=0, pady=0)
        inner_wrap = ctk.CTkFrame(wrap, fg_color=_DK, corner_radius=0)
        inner_wrap.pack(fill="both", expand=True, padx=40, pady=30)
        wrap = inner_wrap  # alias pour le reste de la méthode

        hero = ctk.CTkFrame(wrap, fg_color=_DK, corner_radius=0)
        hero.pack(fill="x", pady=(0,20))
        acc = ctk.CTkFrame(hero, fg_color=BLUE, width=4, height=52, corner_radius=2)
        acc.pack(side="left", padx=(0,14))
        acc.pack_propagate(False)
        htxt = ctk.CTkFrame(hero, fg_color=_DK, corner_radius=0)
        htxt.pack(side="left")
        label(htxt,"SEO & Hashtags",24,True).pack(anchor="w")
        sublabel(htxt,
            "Génère titres, descriptions et hashtags type beat optimisés.",
            10).pack(anchor="w",pady=(3,0))

        # ══════════════════════════════════════════════════════════════
        # SÉLECTEUR DE MODE — 3 cards cliquables
        # ══════════════════════════════════════════════════════════════
        self._seo_mode = tk.StringVar(value="manual")
        self._seo_mode_btns: dict = {}

        mode_card = card(wrap)
        mode_row  = ctk.CTkFrame(mode_card, fg_color=_DC, corner_radius=0)
        mode_row.pack(fill="x")

        _modes = [
            ("manual",  "🎹", "Manuel",     "Je remplis tout moi-même"),
            ("profile", "📁", "Profil",     "Mes templates sauvegardés"),
            ("auto",    "🤖", "IA Auto",    "Tout automatique · Sans clé API"),
        ]
        for i, (mode_id, icon, title_txt, sub_txt) in enumerate(_modes):
            col = tk.Frame(mode_row, bg=_DC, cursor="hand2",
                           padx=20, pady=18)
            col.grid(row=0, column=i, sticky="nsew")
            mode_row.columnconfigure(i, weight=1)
            # séparateur vertical
            if i < len(_modes) - 1:
                tk.Frame(mode_row, bg=_DS, width=1).grid(
                    row=0, column=i, sticky="nse", pady=14)
            ico = tk.Label(col, text=icon,
                           font=("Segoe UI Emoji", 20), bg=_DC, fg=_DF)
            ico.pack()
            ttl = tk.Label(col, text=title_txt,
                           font=(_FONT, 11, "bold"), bg=_DC, fg=_DF)
            ttl.pack(pady=(2,0))
            sbl = tk.Label(col, text=sub_txt,
                           font=(_FONT, 8), bg=_DC, fg=_DU)
            sbl.pack()
            ind = tk.Frame(col, height=3, bg=_DC)
            ind.pack(fill="x", pady=(12, 0))
            self._seo_mode_btns[mode_id] = {
                "col": col, "ico": ico, "ttl": ttl, "sbl": sbl, "ind": ind
            }
            for w in (col, ico, ttl, sbl):
                w.bind("<Button-1>",
                       lambda e, m=mode_id: self._seo_switch_mode(m))

        # ══════════════════════════════════════════════════════════════
        # CARTE DE CONTENU  (partagée)
        # ══════════════════════════════════════════════════════════════
        content_card = card(wrap)
        cnt = ctk.CTkFrame(content_card, fg_color=_DC, corner_radius=0)
        cnt.pack(fill="x", padx=20, pady=16)

        # ── Bandeau profil (visible seulement en mode "profile") ──────
        self._seo_profile_frame = ctk.CTkFrame(cnt, fg_color=_DC, corner_radius=0)

        prof_header = ctk.CTkFrame(self._seo_profile_frame, fg_color=_DC, corner_radius=0)
        prof_header.pack(fill="x", pady=(0,8))
        label(prof_header, "Profil artiste", 11, True).pack(side="left", padx=(0,12))
        self._prof_var = tk.StringVar()
        self._prof_cb  = PillDropdown(
            prof_header, self._prof_var,
            seo_module.profile_names(),
            bg=_DC, width=24)
        self._prof_cb.pack(side="left", padx=(0,8))
        self._prof_var.trace_add("write", lambda *_: self._seo_load_profile())
        for lbl_txt2, cmd2, sty2 in [
            ("Charger",   self._seo_load_profile,   "primary"),
            ("+ Nouveau", self._seo_new_profile,    "secondary"),
            ("Sauver",    self._seo_save_profile,   "secondary"),
            ("Supprimer", self._seo_delete_profile, "danger"),
        ]:
            AppleBtn(prof_header, lbl_txt2, command=cmd2, style=sty2,
                     font=(_FONT, 9, "bold"),
                     padx=9, pady=5).pack(side="left", padx=(0,4))

        self._prof_status = ctk.CTkLabel(
            self._seo_profile_frame, text="",
            font=ctk.CTkFont(family=_FONT,size=9),
            text_color=_DU, fg_color="transparent")
        self._prof_status.pack(anchor="w", pady=(0,4))
        sep(self._seo_profile_frame)

        # ── Formulaire (Manuel & Profil) ─────────────────────────────
        self._seo_form_frame = ctk.CTkFrame(cnt, fg_color=_DC, corner_radius=0)

        self._seo_a1      = tk.StringVar()
        self._seo_a2      = tk.StringVar()
        self._seo_beat    = tk.StringVar()
        self._seo_genre   = tk.StringVar(value="Trap")
        self._seo_contact = tk.StringVar()
        self._seo_free    = tk.BooleanVar(value=True)
        self._seo_custom  = tk.StringVar()

        # Row A: artistes
        ra = ctk.CTkFrame(self._seo_form_frame, fg_color=_DC, corner_radius=0)
        ra.pack(fill="x", pady=(0,8))
        for lbl_txt3, var3, w3 in [
            ("Artiste 1  (ex: Gunna)",    self._seo_a1, 22),
            ("Artiste 2  (optionnel)",     self._seo_a2, 22),
        ]:
            f3 = ctk.CTkFrame(ra, fg_color=_DC, corner_radius=0)
            f3.pack(side="left", padx=(0,20))
            ctk.CTkLabel(f3, text=lbl_txt3,
                         font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                         text_color=_DU, fg_color="transparent").pack(anchor="w")
            entry(f3, var3, width=180).pack(ipady=2)
            var3.trace_add("write", lambda *_: self._seo_update_title_preview())

        # Row B: nom du beat + genre
        rb = ctk.CTkFrame(self._seo_form_frame, fg_color=_DC, corner_radius=0)
        rb.pack(fill="x", pady=(0,8))
        fb = ctk.CTkFrame(rb, fg_color=_DC, corner_radius=0)
        fb.pack(side="left", padx=(0,20))
        ctk.CTkLabel(fb, text="Nom du beat",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        entry(fb, self._seo_beat, width=140).pack(ipady=2)
        self._seo_beat.trace_add("write", lambda *_: self._seo_update_title_preview())
        fg_ = ctk.CTkFrame(rb, fg_color=_DC, corner_radius=0)
        fg_.pack(side="left", padx=(0,20))
        ctk.CTkLabel(fg_, text="Genre",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        PillDropdown(fg_, self._seo_genre,
                     list(seo_module.ARTIST_TAGS.keys()),
                     bg=_DC, width=16).pack(anchor="w")

        # Row C: contact + FREE
        rc = ctk.CTkFrame(self._seo_form_frame, fg_color=_DC, corner_radius=0)
        rc.pack(fill="x", pady=(0,8))
        fc = ctk.CTkFrame(rc, fg_color=_DC, corner_radius=0)
        fc.pack(side="left", padx=(0,20))
        ctk.CTkLabel(fc, text="Email de contact (optionnel)",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        entry(fc, self._seo_contact, width=230).pack(ipady=2)
        ff = ctk.CTkFrame(rc, fg_color=_DC, corner_radius=0)
        ff.pack(side="left", pady=(18,0))
        tog_row = ctk.CTkFrame(ff, fg_color=_DC, corner_radius=0)
        tog_row.pack(anchor="w")
        ctk.CTkLabel(tog_row, text='[FREE] dans le titre',
                     font=ctk.CTkFont(family=_FONT,size=10,weight="bold"),
                     text_color=_DF, fg_color="transparent").pack(side="left", padx=(0,8))
        ToggleSwitch(tog_row, self._seo_free, bg=_DC,
                     command=self._seo_update_title_preview).pack(side="left")

        # Row D: hashtags perso
        rd = ctk.CTkFrame(self._seo_form_frame, fg_color=_DC, corner_radius=0)
        rd.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(rd, text="Hashtags perso  (ex: #monbeatstore #paris)",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        entry(rd, self._seo_custom, width=500).pack(fill="x")

        # Aperçu titre
        sep(self._seo_form_frame)
        ctk.CTkLabel(self._seo_form_frame, text="Aperçu du titre",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        self._seo_title_prev = ctk.CTkLabel(
            self._seo_form_frame,
            text='[FREE] ARTISTE TYPE BEAT "NOM"',
            font=ctk.CTkFont(family="Impact", size=13),
            text_color=W_RED, fg_color="transparent",
            anchor="w", wraplength=680)
        self._seo_title_prev.pack(anchor="w", pady=(4, 10))

        # Bouton générer (Manuel / Profil)
        btn_mp = ctk.CTkFrame(self._seo_form_frame, fg_color=_DC, corner_radius=0)
        btn_mp.pack(anchor="w", pady=(4, 0))
        AppleBtn(btn_mp, "✅  Générer le SEO",
                 command=self._seo_generate_manual,
                 style="primary", font=(_FONT, 11, "bold"),
                 padx=20, pady=10).pack(side="left", padx=(0, 12))
        self._seo_gen_status = ctk.CTkLabel(
            btn_mp, text="",
            font=ctk.CTkFont(family=_FONT,size=9),
            text_color=_DU, fg_color="transparent")
        self._seo_gen_status.pack(side="left")

        # ── Panneau IA Auto ───────────────────────────────────────────
        self._seo_auto_frame = ctk.CTkFrame(cnt, fg_color=_DC, corner_radius=0)

        ctk.CTkLabel(self._seo_auto_frame,
                     text="🤖  L'IA analyse les tendances et génère tout automatiquement.",
                     font=ctk.CTkFont(family=_FONT,size=10,weight="bold"),
                     text_color=_DF, fg_color="transparent").pack(anchor="w")
        ctk.CTkLabel(self._seo_auto_frame,
                     text="Indices optionnels — laisse vide pour laisser décider l'IA.",
                     font=ctk.CTkFont(family=_FONT,size=9),
                     text_color=_DU, fg_color="transparent").pack(anchor="w", pady=(2, 14))

        hints1 = ctk.CTkFrame(self._seo_auto_frame, fg_color=_DC, corner_radius=0)
        hints1.pack(fill="x", pady=(0, 8))

        # Genre hint
        fg2 = ctk.CTkFrame(hints1, fg_color=_DC, corner_radius=0)
        fg2.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(fg2, text="Genre (optionnel)",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        self._auto_genre = tk.StringVar(value="Aléatoire")
        PillDropdown(fg2, self._auto_genre,
                     ["Aléatoire"] + list(seo_module.ARTIST_TAGS.keys()),
                     bg=_DC, width=18).pack(anchor="w")

        # Artist hint
        fa2 = ctk.CTkFrame(hints1, fg_color=_DC, corner_radius=0)
        fa2.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(fa2, text="Style d'artiste (optionnel)",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        self._auto_a1_hint = tk.StringVar()
        entry(fa2, self._auto_a1_hint, width=150).pack(ipady=2)
        ctk.CTkLabel(fa2, text="ex: Gunna, Yeat, The Weeknd…",
                     font=ctk.CTkFont(family=_FONT,size=7),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")

        hints2 = ctk.CTkFrame(self._seo_auto_frame, fg_color=_DC, corner_radius=0)
        hints2.pack(fill="x", pady=(0, 14))

        fa3 = ctk.CTkFrame(hints2, fg_color=_DC, corner_radius=0)
        fa3.pack(side="left", pady=(14,0), padx=(0,28))
        self._auto_free = tk.BooleanVar(value=True)
        tog_row2 = ctk.CTkFrame(fa3, fg_color=_DC, corner_radius=0)
        tog_row2.pack(anchor="w")
        ctk.CTkLabel(tog_row2, text='[FREE] dans le titre',
                     font=ctk.CTkFont(family=_FONT,size=10,weight="bold"),
                     text_color=_DF, fg_color="transparent").pack(side="left", padx=(0,8))
        ToggleSwitch(tog_row2, self._auto_free, bg=_DC).pack(side="left")

        fa4 = ctk.CTkFrame(hints2, fg_color=_DC, corner_radius=0)
        fa4.pack(side="left")
        ctk.CTkLabel(fa4, text="Email de contact (optionnel)",
                     font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                     text_color=_DU, fg_color="transparent").pack(anchor="w")
        self._auto_contact = tk.StringVar()
        entry(fa4, self._auto_contact, width=210).pack(ipady=2)

        btn_auto = ctk.CTkFrame(self._seo_auto_frame, fg_color=_DC, corner_radius=0)
        btn_auto.pack(anchor="w", pady=(0, 4))
        AppleBtn(btn_auto, "🤖  Générer tout automatiquement",
                 command=self._seo_generate_auto,
                 style="primary", font=(_FONT, 12, "bold"),
                 padx=24, pady=12).pack(side="left", padx=(0, 14))
        self._auto_status = ctk.CTkLabel(
            btn_auto, text="",
            font=ctk.CTkFont(family=_FONT,size=9),
            text_color=_DU, fg_color="transparent")
        self._auto_status.pack(side="left")

        # ══════════════════════════════════════════════════════════════
        # RÉSULTATS
        # ══════════════════════════════════════════════════════════════
        res_card = card(wrap)
        res_in   = ctk.CTkFrame(res_card, fg_color=_DC, corner_radius=0)
        res_in.pack(fill="x", padx=20, pady=16)

        res_hdr = ctk.CTkFrame(res_in, fg_color=_DC, corner_radius=0)
        res_hdr.pack(fill="x", pady=(0,12))
        label(res_hdr, "Résultats générés", 13, True).pack(side="left")
        AppleBtn(res_hdr, "📌  Injecter dans l'upload",
                 command=self._seo_inject_upload,
                 style="secondary", font=(_FONT,9,"bold"),
                 padx=12, pady=6).pack(side="right")

        for lbl_r, attr_r, h_r in [
            ("Titre YouTube",                      "_seo_r_title",  40),
            ("Tags YouTube  (séparés par virgule)", "_seo_r_tags",  60),
            ("Description YouTube",                "_seo_r_desc",  140),
            ("Légende Instagram",                  "_seo_r_ig_cap", 40),
            ("Hashtags Instagram",                 "_seo_r_ig_tags",60),
        ]:
            ctk.CTkLabel(res_in, text=lbl_r,
                         font=ctk.CTkFont(family=_FONT,size=9,weight="bold"),
                         text_color=_DU, fg_color="transparent").pack(anchor="w", pady=(8,2))
            t = ctk.CTkTextbox(res_in, fg_color=_DE, border_color=_DS,
                               text_color=_DF, corner_radius=8, border_width=1,
                               height=h_r,
                               font=ctk.CTkFont(family=_FONT,size=9))
            t.pack(fill="x")
            setattr(self, attr_r, t)
            cr = ctk.CTkFrame(res_in, fg_color=_DC, corner_radius=0)
            cr.pack(anchor="e", pady=(2, 0))
            AppleBtn(cr, "📋 Copier",
                     command=lambda w=t: self._copy_text(w),
                     style="ghost", font=(_FONT,8),
                     padx=8, pady=3).pack()

        # ══════════════════════════════════════════════════════════════
        # NAVIGATEUR HASHTAGS ARTISTES
        # ══════════════════════════════════════════════════════════════
        ht_card = card(wrap)
        ht_in   = ctk.CTkFrame(ht_card, fg_color=_DC, corner_radius=0)
        ht_in.pack(fill="x", padx=20, pady=16)
        label(ht_in, "Hashtags par artiste", 13, True).pack(anchor="w", pady=(0,6))
        sublabel(ht_in,
            "Clique sur un artiste pour voir ses hashtags ciblés — "
            "copie et colle dans tes profils.", 10).pack(anchor="w", pady=(0,10))

        artists_frame = ctk.CTkFrame(ht_in, fg_color=_DC, corner_radius=0)
        artists_frame.pack(fill="x", pady=(0,10))
        for artist in sorted(seo_module.ARTIST_TAGS.keys()):
            AppleBtn(artists_frame, artist,
                     command=lambda a=artist: self._show_artist_tags(a),
                     style="secondary", font=(_FONT,8,"bold"),
                     padx=8, pady=4).pack(side="left", padx=2, pady=2)

        self._htag_display = ctk.CTkTextbox(
            ht_in, fg_color=_DE, border_color=_DS,
            text_color=_DF, corner_radius=8, border_width=1, height=70,
            font=ctk.CTkFont(family=_FONT,size=10))
        self._htag_display.pack(fill="x")
        cr2 = ctk.CTkFrame(ht_in, fg_color=_DC, corner_radius=0)
        cr2.pack(anchor="e", pady=(4, 0))
        AppleBtn(cr2, "📋 Copier",
                 command=lambda: self._copy_text(self._htag_display),
                 style="ghost", font=(_FONT,8),
                 padx=8, pady=3).pack()

        # Init
        self._seo_refresh_profiles()
        self._seo_switch_mode("manual")

    # ══════════════════════════════════════════════════════════════════
    # LOGIQUE SEO
    # ══════════════════════════════════════════════════════════════════

    def _seo_switch_mode(self, mode: str):
        """Bascule entre les 3 modes : manual / profile / auto."""
        self._seo_mode.set(mode)
        # Styles des boutons de mode
        for m_id, w in self._seo_mode_btns.items():
            active   = (m_id == mode)
            bg_col   = _DE if active else _DC
            ind_col  = W_RED  if active else _DC
            ttl_col  = W_RED  if active else _DF
            for widget in (w["col"], w["ico"], w["ttl"], w["sbl"]):
                try: widget.configure(bg=bg_col)
                except Exception: pass
            w["ind"].configure(bg=ind_col)
            w["ttl"].configure(fg=ttl_col)
        # Affichage des panneaux
        self._seo_profile_frame.pack_forget()
        self._seo_form_frame.pack_forget()
        self._seo_auto_frame.pack_forget()
        if mode == "auto":
            self._seo_auto_frame.pack(fill="x", pady=(0, 8))
        else:
            if mode == "profile":
                self._seo_profile_frame.pack(fill="x", pady=(0, 4))
            self._seo_form_frame.pack(fill="x", pady=(0, 4))

    # ── Aperçu titre en temps réel ────────────────────────────────────
    def _seo_update_title_preview(self):
        a1   = self._seo_a1.get().strip()   or "ARTISTE"
        a2   = self._seo_a2.get().strip()
        name = self._seo_beat.get().strip() or "NOM"
        free = self._seo_free.get()
        self._seo_title_prev.configure(
            text=seo_module.generate_beat_title(a1, name, a2, free))

    # ── Profils ───────────────────────────────────────────────────────
    def _seo_refresh_profiles(self):
        names = seo_module.profile_names()
        self._prof_cb._opts = names
        if names and not self._prof_var.get():
            self._prof_var.set(names[0])

    def _seo_load_profile(self):
        name = self._prof_var.get()
        if not name: return
        p = seo_module.load_profiles().get(name, {})
        self._seo_a1.set(p.get("artist1",""))
        self._seo_a2.set(p.get("artist2",""))
        self._seo_beat.set(p.get("beat_name",""))
        self._seo_free.set(p.get("free", True))
        self._seo_genre.set(p.get("genre","Trap"))
        self._seo_contact.set(p.get("contact",""))
        self._seo_custom.set(p.get("custom_hashtags",""))
        self._seo_update_title_preview()
        self._prof_status.configure(
            text=f"✓ Profil « {name} » chargé", text_color=GREEN)

    def _seo_save_profile(self):
        name = self._prof_var.get().strip()
        if not name:
            self._seo_new_profile(); return
        seo_module.save_profile(name, {
            "artist1":         self._seo_a1.get().strip(),
            "artist2":         self._seo_a2.get().strip(),
            "beat_name":       self._seo_beat.get().strip(),
            "free":            self._seo_free.get(),
            "genre":           self._seo_genre.get(),
            "contact":         self._seo_contact.get().strip(),
            "custom_hashtags": self._seo_custom.get().strip(),
        })
        self._seo_refresh_profiles()
        self._prof_status.configure(
            text=f"✓ Profil « {name} » sauvegardé", text_color=GREEN)

    def _seo_new_profile(self):
        top = tk.Toplevel(self)
        top.title("Nouveau profil")
        top.geometry("380x150")
        top.resizable(False, False)
        top.configure(bg=_DC)
        top.grab_set()
        tk.Label(top, text="Nom du profil  (ex: Gunna Type Beat)",
                 font=(_FONT,10,"bold"), bg=_DC, fg=_DF
                 ).pack(pady=(22, 6))
        var = tk.StringVar()
        e   = tk.Entry(top, textvariable=var, font=(_FONT,11),
                       bg=_DE, fg=_DF, relief="flat",
                       highlightthickness=1, highlightbackground=_DS,
                       insertbackground=_DF, width=30)
        e.pack(ipady=6, padx=30); e.focus()
        def ok():
            n = var.get().strip()
            if not n: return
            self._prof_var.set(n); top.destroy()
            self._seo_save_profile()
        tk.Frame(top, bg=_DC, height=10).pack()
        AppleBtn(top, "Créer", command=ok, style="primary",
                 font=(_FONT,10,"bold"), padx=20, pady=8).pack()
        top.bind("<Return>", lambda e: ok())

    def _seo_delete_profile(self):
        name = self._prof_var.get()
        if not name: return
        if not messagebox.askyesno("Supprimer",
                f"Supprimer le profil « {name} » ?"): return
        seo_module.delete_profile(name)
        self._prof_var.set("")
        self._seo_refresh_profiles()
        self._prof_status.configure(
            text=f"✓ Profil « {name} » supprimé", text_color=_DU)

    # ── Génération Manuel / Profil ────────────────────────────────────
    def _seo_generate_manual(self):
        a1 = self._seo_a1.get().strip()
        if not a1:
            messagebox.showwarning("Artiste manquant",
                "Entre au moins l'Artiste 1."); return
        a2      = self._seo_a2.get().strip()
        name    = self._seo_beat.get().strip() or "BEAT"
        genre   = self._seo_genre.get()
        free    = self._seo_free.get()
        contact = self._seo_contact.get().strip()
        custom  = self._seo_custom.get().strip()
        tags_list = seo_module.generate_beat_hashtags(a1, a2, genre, custom, 30)
        self._seo_fill_results({
            "yt_title":       seo_module.generate_beat_title(a1, name, a2, free),
            "yt_tags":        seo_module.format_yt_tags(tags_list),
            "yt_description": seo_module.generate_beat_description(
                                  a1, name, a2, genre, contact, free),
            "ig_caption":     seo_module.generate_beat_ig_caption(
                                  a1, name, a2, free),
            "ig_hashtags":    seo_module.format_ig_tags(tags_list),
        })
        self._seo_gen_status.configure(text="✅ Généré !", text_color=GREEN)

    # ── Génération IA Auto (0 clé API) ───────────────────────────────
    def _seo_generate_auto(self):
        genre   = self._auto_genre.get()
        if genre == "Aléatoire": genre = None
        a1_hint = self._auto_a1_hint.get().strip()
        free    = self._auto_free.get()
        contact = self._auto_contact.get().strip()
        self._auto_status.configure(text="Génération en cours…", text_color=ORANGE)
        self.update_idletasks()
        try:
            res = seo_module.generate_auto(
                genre=genre, artist1_hint=a1_hint,
                free=free, contact=contact)
            self._seo_fill_results(res)
            # Sync les champs du formulaire pour réutilisation
            self._seo_a1.set(res.get("artist1",""))
            self._seo_a2.set(res.get("artist2",""))
            self._seo_beat.set(res.get("beat_name",""))
            if res.get("genre"):
                self._seo_genre.set(res["genre"])
            info = res.get("artist1","")
            if res.get("artist2"): info += f" × {res['artist2']}"
            self._auto_status.configure(
                text=f'✅  {info} — "{res.get("beat_name","")}"',
                text_color=GREEN)
        except Exception as exc:
            self._auto_status.configure(
                text=f"❌ {str(exc)[:70]}", text_color=RED)

    # ── Injecter dans l'onglet Upload ────────────────────────────────
    def _seo_inject_upload(self):
        title = self._seo_r_title.get("1.0", "end").strip()
        desc  = self._seo_r_desc.get("1.0", "end").strip()
        if not title:
            messagebox.showwarning("Aucun résultat",
                "Génère d'abord le SEO avant d'injecter."); return
        if hasattr(self, "_desc_var") and desc:
            self._desc_var.set(desc[:5000])
        self.clipboard_clear()
        self.clipboard_append(title)
        messagebox.showinfo(
            "Injecté ✓",
            f"Description injectée dans l'onglet Upload.\n\n"
            f"Le titre a été copié dans le presse-papier :\n{title[:80]}…")

    # ── Fill results ──────────────────────────────────────────────────
    def _seo_fill_results(self, res: dict):
        for key, attr in [
            ("yt_title",       "_seo_r_title"),
            ("yt_tags",        "_seo_r_tags"),
            ("yt_description", "_seo_r_desc"),
            ("ig_caption",     "_seo_r_ig_cap"),
            ("ig_hashtags",    "_seo_r_ig_tags"),
        ]:
            val = res.get(key, "")
            if val:
                w = getattr(self, attr)
                w.delete("1.0", "end")
                w.insert("1.0", val)

    def _show_artist_tags(self, artist: str):
        tags = seo_module.ARTIST_TAGS.get(artist, [])
        tags = tags + [t for t in seo_module.BASE_BEAT_TAGS if t not in tags]
        self._htag_display.delete("1.0", "end")
        self._htag_display.insert("1.0", " ".join(tags[:30]))

    def _copy_text(self, widget):
        content = widget.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(content)


# ══════════════════════════════════════════════════════════════════════
# STYLES TTK
# ══════════════════════════════════════════════════════════════════════
def styles():
    s=ttk.Style(); s.theme_use("clam")
    s.configure("TCombobox",
                fieldbackground=BG,background=BG,foreground=TEXT,
                selectbackground=SHADOW,bordercolor=BORDER,
                arrowcolor=SUB,insertcolor=TEXT)
    s.map("TCombobox",fieldbackground=[("readonly",BG)],
          background=[("readonly",BG)])
    s.configure("Vertical.TScrollbar",
                background=SHADOW,troughcolor=BG,
                bordercolor=BG,arrowcolor=BORDER,width=5)


if __name__=="__main__":
    app=App()
    styles()
    app.mainloop()
