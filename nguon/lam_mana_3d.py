# -*- coding: utf-8 -*-
"""Làm bộ Mana 3D động sạch từ slide/anh/mana-dong-3d/gif/: bỏ khung 10 có dấu ngôi sao của máy vẽ, cắt chung một khung.

    python -X utf8 lam_mana_3d.py

Ra lop-4-5/slide/anh/mana-3d/mana_3d_<tư thế>.gif (512 px, cho slide) và tai-nguyen/mana/<khóa>.webp (360 px, cho game).
"""
import glob
import os

from PIL import Image, ImageDraw

DAY = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.abspath(os.path.join(DAY, "..", "..", "..", ".."))
VAO = os.path.join(GOC, "slide", "anh", "mana-dong-3d", "gif")
RA_SLIDE = os.path.join(GOC, "demo-nhan-dien-cam-xuc", "lop-4-5", "slide", "anh", "mana-3d")
RA_GAME = os.path.join(DAY, "tai-nguyen", "mana")
GAME = {"hao_hung": "chao", "cho_doi": "cho", "ngac_nhien": "ngac_nhien", "gai_dau": "nghi", "vo_tay": "vo_tay", "tu_tin": "noi"}
BO_KHUNG = 10


def doc(tu_the):
    g = Image.open(os.path.join(VAO, "mana_dong_%s.gif" % tu_the))
    giay = []
    for i in range(g.n_frames):
        g.seek(i)
        giay.append(g.info.get("duration", 190))
    tep = sorted(glob.glob(os.path.join(VAO, "mana_dong_%s-khung" % tu_the, "*.png")))[:BO_KHUNG - 1]
    return [Image.open(f).convert("RGBA") for f in tep], giay[:BO_KHUNG - 1]


def bit_lo(k):
    """Bít chỗ trong suốt nằm trong thân Mana, như tròng kính, bằng nền trắng. Nền ngoài giữ trong suốt."""
    a = k.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    ngoai = a.copy()
    r, c = ngoai.size
    for d in ((0, 0), (r - 1, 0), (0, c - 1), (r - 1, c - 1)):
        if ngoai.getpixel(d) == 0:
            ImageDraw.floodfill(ngoai, d, 128)
    than = ngoai.point(lambda v: 0 if v == 128 else 255)
    nen = Image.new("RGBA", k.size, (255, 255, 255, 255))
    nen.alpha_composite(k)
    ra = Image.composite(nen, k, than)
    alpha = Image.composite(Image.new("L", k.size, 255), k.getchannel("A"), than)
    ra.putalpha(alpha)
    return ra


def cat_chung(ds):
    ds = [bit_lo(k) for k in ds]
    hop =[k.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox() for k in ds]
    x0, y0 = min(h[0] for h in hop), min(h[1] for h in hop)
    x1, y1 = max(h[2] for h in hop), max(h[3] for h in hop)
    return [k.crop((x0, y0, x1, y1)) for k in ds]


def gif(ds, giay, ra):
    p = []
    for k in ds:
        nen = Image.new("RGBA", k.size, (255, 255, 255, 0))
        nen.paste(k, (0, 0), k.getchannel("A").point(lambda v: 255 if v > 110 else 0))
        q = nen.convert("RGB").quantize(colors=255, dither=Image.FLOYDSTEINBERG)
        kq = q.copy()
        kq.putpalette(q.getpalette()[:765] + [0, 0, 0])
        dl = kq.load()
        a = nen.getchannel("A").load()
        for y in range(kq.height):
            for x in range(kq.width):
                if a[x, y] == 0:
                    dl[x, y] = 255
        p.append(kq)
    p[0].save(ra, save_all=True, append_images=p[1:], duration=giay, loop=0, transparency=255, disposal=2, optimize=False)


if __name__ == "__main__":
    os.makedirs(RA_SLIDE, exist_ok=True)
    os.makedirs(RA_GAME, exist_ok=True)
    for f in glob.glob(os.path.join(RA_GAME, "*.webp")):
        os.remove(f)
    tu_the = sorted(os.path.basename(d)[10:-6] for d in glob.glob(os.path.join(VAO, "*-khung")))
    for t in tu_the:
        ds, giay = doc(t)
        ds = cat_chung(ds)
        gif(ds, giay, os.path.join(RA_SLIDE, "mana_3d_%s.gif" % t))
    for khoa, t in GAME.items():
        ds, giay = doc(t)
        ds = [k.copy() for k in cat_chung(ds)]
        for k in ds:
            k.thumbnail((360, 360), Image.LANCZOS)
        ds[0].save(os.path.join(RA_GAME, khoa + ".webp"), save_all=True, append_images=ds[1:], duration=giay, loop=0, quality=80, method=6)
    co = [os.path.getsize(f) for f in glob.glob(os.path.join(RA_GAME, "*.webp"))]
    print("slide", len(tu_the), tu_the, "| game", len(co), "tổng", sum(co))
