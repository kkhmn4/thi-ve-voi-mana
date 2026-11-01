# -*- coding: utf-8 -*-
"""Chuẩn bị tài nguyên cho trang: biểu tượng Phosphor (MIT), phông Nunito (OFL), ảnh Mana thu nhỏ, giọng đọc.

    python -X utf8 tai_tai_nguyen.py

Ra tai-nguyen/. Giọng: VieNeu chạy trên máy, giọng Thục Đoan, tông tự nhiên. Mỗi tên hình có 2 câu: Mình thấy ..., Hay là ...?
Mỗi đề có thêm 2 câu: Hãy vẽ ..., À, mình biết rồi! Đó là ... Mỗi tệp cắt lặng, một kênh, 24 kHz, 32 kb/s.
Lúc sinh in các câu dài bất thường để soát: câu dưới 0,45 giây hoặc trên 4,5 giây sinh lại tối đa 3 lần.
"""
import json
import os
import subprocess
import urllib.request

import numpy as np
import soundfile as sf
from PIL import Image

from nhan_vi import AN, NHAN

DAY = os.path.dirname(os.path.abspath(__file__))
RA = os.path.join(DAY, "tai-nguyen")
GOC = os.path.abspath(os.path.join(DAY, "..", "..", "..", ".."))
ICON = ["pencil-simple", "eraser", "trash", "skip-forward", "play", "arrow-counter-clockwise", "x", "check", "timer", "star", "speaker-high", "speaker-slash", "images",
        "cat", "fish", "sun", "umbrella", "bicycle", "flower", "tree", "house", "ice-cream", "bird", "clock", "fire", "guitar", "lighthouse", "castle-turret", "train"]
PHONG = ["nunito-vietnamese-700-normal", "nunito-latin-700-normal", "nunito-vietnamese-900-normal", "nunito-latin-900-normal"]
TU_THE = ["hao_hung", "cho_doi", "ngac_nhien", "gai_dau", "vo_tay", "tu_tin"]
DE = ["cat", "fish", "sun", "umbrella", "bicycle", "flower", "tree", "house", "star", "ice_cream", "bird", "clock", "guitar", "lighthouse", "castle", "train"]
CAU = {"gioi_thieu": "Bạn vẽ, mình đoán nhé!", "bat_dau": "Bắt đầu nào!", "het_gio": "Hết giờ rồi! Cùng xem các bạn đã vẽ gì nhé.", "bo_qua": "Mình bỏ qua hình này nhé.",
       "thuong": "Giỏi quá! Vẽ thêm hình thưởng nhé."}
GIONG = "Thục Đoan"


def tai(url, ra):
    if not os.path.exists(ra):
        urllib.request.urlretrieve(url, ra)
    return ra


def lam_icon():
    d = os.path.join(RA, "icon")
    os.makedirs(d, exist_ok=True)
    for t in ICON:
        tai("https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2.1.1/assets/fill/%s-fill.svg" % t, os.path.join(d, t + ".svg"))
    print("icon", len(ICON), flush=True)


def lam_phong():
    d = os.path.join(RA, "phong")
    os.makedirs(d, exist_ok=True)
    for t in PHONG:
        tai("https://cdn.jsdelivr.net/npm/@fontsource/nunito@5.0.18/files/%s.woff2" % t, os.path.join(d, t + ".woff2"))
    print("phông", len(PHONG), flush=True)


def lam_mana():
    d = os.path.join(RA, "mana")
    os.makedirs(d, exist_ok=True)
    for t in TU_THE:
        im = Image.open(os.path.join(GOC, "slide", "anh", "mana-goc", "cat", "mana_%s.png" % t)).convert("RGBA")
        im = im.crop(im.getchannel("A").getbbox())
        im.thumbnail((420, 420), Image.LANCZOS)
        im.save(os.path.join(d, t + ".webp"), quality=86, method=6)
    print("mana", len(TU_THE), flush=True)


def danh_sach():
    ds = dict(CAU)
    for t, v in NHAN.items():
        if t in AN:
            continue
        k = t.replace("-", "_")
        ds["a_" + k] = "Mình thấy %s." % v
        ds["b_" + k] = "Hay là %s?" % v
    for t in DE:
        k = t.replace("-", "_")
        ds["v_" + k] = "Hãy vẽ %s nhé!" % NHAN[t]
        ds["w_" + k] = "À, mình biết rồi! Đó là %s!" % NHAN[t]
    return ds


def lam_giong():
    from vieneu import Vieneu
    d = os.path.join(RA, "giong")
    os.makedirs(d, exist_ok=True)
    ds = danh_sach()
    v = Vieneu()
    sr = int(getattr(v, "sample_rate", 48000))
    la = []
    for i, (ten, cau) in enumerate(ds.items()):
        ra = os.path.join(d, ten + ".mp3")
        if os.path.exists(ra):
            continue
        for lan in range(3):
            a = np.asarray(v.infer(text=cau, voice=GIONG, temperature=0.7))
            dai = len(a) / sr
            if 0.45 <= dai <= 4.5:
                break
        else:
            la.append((ten, cau, round(dai, 2)))
        tho = ra + ".wav"
        sf.write(tho, a, sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tho, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5",
                        "-ac", "1", "-ar", "24000", "-b:a", "32k", ra], check=True)
        os.remove(tho)
        if i % 100 == 0:
            print(i, "trên", len(ds), flush=True)
    co = [os.path.getsize(os.path.join(d, f)) for f in os.listdir(d)]
    print("giọng", len(co), "tệp, tổng", sum(co), "byte. Bất thường:", la, flush=True)


if __name__ == "__main__":
    os.makedirs(RA, exist_ok=True)
    lam_icon()
    lam_phong()
    lam_mana()
    lam_giong()
    json.dump({"giong": GIONG}, open(os.path.join(RA, "ghi-chu.json"), "w", encoding="utf-8"), ensure_ascii=False)
