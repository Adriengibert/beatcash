#!/usr/bin/env python3
"""Beat Cash — Génération beat_cash.ico (multi-résolution)"""

import sys, subprocess
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont

from pathlib import Path

W_RED   = (204, 17,  0,  255)
W_BLACK = ( 12, 12, 12,  255)
W_WHITE = (242, 242, 247, 255)

FONT_PATHS = [
    "C:/Windows/Fonts/impact.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

def get_font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, int(size))
        except Exception:
            pass
    return ImageFont.load_default()

def make_frame(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    pad = max(1, size // 14)

    # Fond cercle noir
    d.ellipse([pad, pad, size - pad - 1, size - pad - 1], fill=W_BLACK)

    # Anneau rouge
    ring = max(1, size // 18)
    d.ellipse([pad, pad, size - pad - 1, size - pad - 1],
              outline=W_RED, width=ring)

    # Signe $
    fs   = int(size * 0.58)
    font = get_font(fs)

    def ct(text, color, ox=0, oy=0):
        bb = d.textbbox((0, 0), text, font=font)
        x  = (size - (bb[2]-bb[0])) // 2 - bb[0] + ox
        y  = (size - (bb[3]-bb[1])) // 2 - bb[1] + oy + int(size*0.02)
        d.text((x, y), text, font=font, fill=color)

    off = max(1, size // 28)
    ct("$", W_RED,   ox= off, oy= off)
    ct("$", W_WHITE, ox=-off, oy=-off)

    return img

def build_ico(out="beat_cash.ico"):
    SIZES = [16, 24, 32, 48, 64, 128, 256]

    # Créer toutes les frames
    frames = [make_frame(s) for s in SIZES]

    # Méthode manuelle : écrire le fichier ICO depuis zéro
    import struct, io

    def frame_to_bmp_bytes(img):
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    icon_data = []
    for img in frames:
        icon_data.append(frame_to_bmp_bytes(img))

    # ICO header
    n = len(SIZES)
    header = struct.pack("<HHH", 0, 1, n)  # reserved, type=1 (ICO), count

    # Chaque image commence après : header(6) + directory(16*n)
    offset = 6 + 16 * n
    directory = b""
    for i, img in enumerate(frames):
        s    = SIZES[i]
        data = icon_data[i]
        w    = s if s < 256 else 0
        h    = s if s < 256 else 0
        directory += struct.pack("<BBBBHHII",
            w, h,       # width, height (0 = 256)
            0,          # color count
            0,          # reserved
            1,          # planes
            32,         # bit count
            len(data),  # bytes in image
            offset      # offset
        )
        offset += len(data)

    with open(out, "wb") as f:
        f.write(header)
        f.write(directory)
        for data in icon_data:
            f.write(data)

    sz = Path(out).stat().st_size
    print(f"OK  {out}  ({sz // 1024} KB, {n} tailles : {SIZES})")

if __name__ == "__main__":
    build_ico()
