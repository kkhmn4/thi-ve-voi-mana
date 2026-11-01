# -*- coding: utf-8 -*-
"""Đóng gói một tệp ../thi-ve-voi-ai.html: thư viện, mô hình, tên tiếng Việt, nét vẽ mẫu, giọng, biểu tượng, phông, ảnh Mana. Chạy không cần mạng.

    python -X utf8 tai_tai_nguyen.py                   một lần, tạo tai-nguyen/
    python -X utf8 dong_goi.py <thư mục mô hình> <thư mục ndjson> [độ dày nét]

Mô hình: DoodleNet của Yining Shi, ml5-data-and-models, giấy phép MIT. Nét vẽ mẫu: Quick, Draw! dataset, CC BY 4.0.
Tệp mô hình lấy từ cdn.jsdelivr.net/gh/ml5js/ml5-data-and-models@main/models/doodlenet/, tf.min.js bản 3.21.0.
"""
import base64
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from nhan_vi import AN, NHAN

DAY = os.path.dirname(os.path.abspath(__file__))
TN = os.path.join(DAY, "tai-nguyen")
GOC = "https://storage.googleapis.com/quickdraw_dataset/full/simplified/%s.ndjson"
DE = {"cat": "cat", "fish": "fish", "sun": "sun", "umbrella": "umbrella", "bicycle": "bicycle", "flower": "flower", "tree": "tree", "house": "house",
      "star": "star", "ice_cream": "ice-cream", "bird": "bird", "clock": "clock",
      "guitar": "guitar", "lighthouse": "lighthouse", "castle": "castle-turret", "train": "train"}
# Đề thử thách: khó vẽ với học sinh nhưng AI nhận ra tốt khi vẽ đúng (số đo do_de_kho.py: 32 đến 38 trên 40).
KHO = {"bicycle", "guitar", "lighthouse", "castle", "train"}
SO_MAU = 18


def mau(lop, thu_muc):
    t = os.path.join(thu_muc, lop + ".ndjson")
    if not os.path.exists(t):
        req = urllib.request.Request(GOC % urllib.parse.quote(lop.replace("_", " ")), headers={"Range": "bytes=0-900000"})
        with urllib.request.urlopen(req, timeout=120) as r:
            du = r.read()
        open(t, "wb").write(du[:du.rfind(b"\n")])
    ra = []
    for dong in open(t, encoding="utf-8"):
        m = json.loads(dong)
        if m.get("recognized") and len(ra) < SO_MAU:
            ra.append(m["drawing"])
    return ra


def mau_nhe(lop, thu_muc):
    """6 nét vẽ mỗi loại hình, dùng cho phần Mana nghĩ là ... ở màn tổng kết."""
    t = os.path.join(thu_muc, lop + "-nhe.ndjson")
    if not os.path.exists(t):
        req = urllib.request.Request(GOC % urllib.parse.quote(lop.replace("_", " ")), headers={"Range": "bytes=0-60000"})
        with urllib.request.urlopen(req, timeout=120) as r:
            du = r.read()
        open(t, "wb").write(du[:du.rfind(b"\n")])
    ra = []
    for dong in open(t, encoding="utf-8"):
        m = json.loads(dong)
        if m.get("recognized") and len(ra) < 6:
            ra.append(m["drawing"])
    return ra


def b64(f):
    return base64.b64encode(open(f, "rb").read()).decode()


def phong():
    ra = []
    for tep, nang, vung in (("nunito-vietnamese-700-normal", 700, "U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+1EA0-1EF9,U+20AB"),
                            ("nunito-latin-700-normal", 700, "U+0000-00FF"),
                            ("nunito-vietnamese-900-normal", 900, "U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+1EA0-1EF9,U+20AB"),
                            ("nunito-latin-900-normal", 900, "U+0000-00FF")):
        ra.append('@font-face{font-family:Nunito;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2");unicode-range:%s}'
                  % (nang, b64(os.path.join(TN, "phong", tep + ".woff2")), vung))
    return "".join(ra)


def icon():
    d = os.path.join(TN, "icon")
    ra = {}
    for f in os.listdir(d):
        s = open(os.path.join(d, f), encoding="utf-8").read()
        ra[f[:-4]] = re.sub(r"<svg[^>]*>", '<svg class="ic" viewBox="0 0 256 256" aria-hidden="true">', s).strip()
    return ra


def main(mo, nd, day_net):
    ten = open(os.path.join(mo, "class_names.txt"), encoding="utf-8").read().split()
    thieu = [t for t in ten if t not in NHAN]
    assert not thieu, thieu
    gd = os.path.join(TN, "giong")
    du = {"ten": ten, "vi": ["" if t in AN else NHAN[t] for t in ten],
          "de": [{"ten": NHAN[t], "so": ten.index(t), "ic": ic, "kho": t in KHO, "hinh": mau(t, nd)} for t, ic in DE.items()],
          "day_net": day_net,
          "mo_hinh": json.load(open(os.path.join(mo, "model.json"), encoding="utf-8")),
          "trong_so": b64(os.path.join(mo, "group1-shard1of1.bin")),
          "icon": icon(),
          "mana": {f[:-5]: "data:image/webp;base64," + b64(os.path.join(TN, "mana", f)) for f in os.listdir(os.path.join(TN, "mana"))},
          "giong": {f[:-4]: b64(os.path.join(gd, f)) for f in os.listdir(gd) if f.endswith(".mp3")}}
    with ThreadPoolExecutor(12) as tp:
        ds = list(tp.map(lambda t: [] if t in AN else mau_nhe(t, nd), ten))
    du["mau"] = ds
    tr = open(os.path.join(DAY, "trang.html"), encoding="utf-8").read()
    tr = tr.replace("/*PHONG*/", phong())
    tr = tr.replace("/*TF*/", open(os.path.join(mo, "tf.min.js"), encoding="utf-8").read().replace("</script>", "<\\/script>"))
    tr = tr.replace("/*DU_LIEU*/", json.dumps(du, ensure_ascii=False, separators=(",", ":")))
    ra = os.path.join(os.path.dirname(DAY), "thi-ve-voi-ai.html")
    open(ra, "w", encoding="utf-8").write(tr)
    print("ghi", ra, os.path.getsize(ra), "giọng", len(du["giong"]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 6)
