# -*- coding: utf-8 -*-
"""Soát độ dài và độ lớn của mọi câu giọng, sinh lại câu nhỏ tiếng hoặc quá ngắn, sinh thêm câu giải thích ở màn tổng kết.

    python -X utf8 sua_giong.py
"""
import os
import subprocess

import numpy as np
import soundfile as sf

import tai_tai_nguyen as T

DAY = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(T.RA, "giong")
THEM = {"vi_dung": "Hình của bạn giống những hình mình đã học, nên mình đoán ra.",
        "vi_sai": "Hình của bạn giống hình khác mình đã học, nên mình đoán nhầm.",
        "tong_ket": "Bấm vào từng hình để xem mình đã đoán gì nhé."}


def do(f):
    tho = f + ".do.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, tho], check=True)
    a, sr = sf.read(tho)
    os.remove(tho)
    khung = int(sr * .02)
    e = np.array([np.sqrt(np.mean(a[i:i + khung] ** 2)) for i in range(0, max(len(a) - khung, 1), khung)])
    return len(a) / sr, float((e > 0.02).mean() * len(a) / sr)


def sinh(v, ten, cau, sr):
    ra = os.path.join(D, ten + ".mp3")
    for lan in range(4):
        a = np.asarray(v.infer(text=cau, voice=T.GIONG, temperature=0.7))
        tho = ra + ".wav"
        sf.write(tho, a, sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tho, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5",
                        "-ac", "1", "-ar", "24000", "-b:a", "32k", ra], check=True)
        os.remove(tho)
        dai, co = do(ra)
        if co >= max(0.4, 0.05 * len(cau)):
            return dai, co
    return dai, co


if __name__ == "__main__":
    ds = T.danh_sach()
    ds.update(THEM)
    hong = []
    for k, c in ds.items():
        f = os.path.join(D, k + ".mp3")
        if not os.path.exists(f):
            hong.append(k)
            continue
        dai, co = do(f)
        if co < max(0.4, 0.05 * len(c)):
            hong.append(k)
    print("cần sinh lại", len(hong), hong[:60], flush=True)
    from vieneu import Vieneu
    v = Vieneu()
    sr = int(getattr(v, "sample_rate", 48000))
    for k in hong:
        print(k, ds[k], sinh(v, k, ds[k], sr), flush=True)
    print("xong")
