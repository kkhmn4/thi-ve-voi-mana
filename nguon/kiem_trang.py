# -*- coding: utf-8 -*-
"""Kiểm thi-ve-voi-ai.html: mở bằng file://, không mạng, đo độ đoán đúng với nét vẽ thật, kể cả nét AI Quick, Draw! không nhận ra.

    python -X utf8 kiem_trang.py <thư mục ndjson> <ra.json>
"""
import json
import os
import sys
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright

DAY = os.path.dirname(os.path.abspath(__file__))
TRANG = os.path.join(os.path.dirname(DAY), "thi-ve-voi-ai.html")
DE = ["cat", "fish", "house", "tree", "sun", "flower", "apple", "car", "bicycle", "star", "umbrella", "butterfly", "clock", "ice_cream", "banana", "moon",
      "elephant", "snake", "rabbit", "duck", "pig", "dog", "bird", "cup"]
SO = 40


def lay(lop, nd):
    tot, xau = [], []
    t = os.path.join(nd, lop + "-kiem.ndjson")
    if not os.path.exists(t):
        req = urllib.request.Request("https://storage.googleapis.com/quickdraw_dataset/full/simplified/%s.ndjson" % urllib.parse.quote(lop.replace("_", " ")),
                                     headers={"Range": "bytes=0-8000000"})
        with urllib.request.urlopen(req, timeout=180) as r:
            du = r.read()
        open(t, "wb").write(du[:du.rfind(b"\n")])
    for i, dong in enumerate(open(t, encoding="utf-8")):
        m = json.loads(dong)
        ns = [[[x, y] for x, y in zip(a, b)] for a, b in m["drawing"]]
        if m.get("recognized"):
            if i > 400 and len(tot) < SO:
                tot.append(ns)
        elif len(xau) < SO:
            xau.append(ns)
        if len(tot) >= SO and len(xau) >= SO:
            break
    return tot, xau


if __name__ == "__main__":
    nd, ra = sys.argv[1], sys.argv[2]
    kq = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        ctx = b.new_context(viewport={"width": 1280, "height": 720}, offline=True)
        pg = ctx.new_page()
        loi = []
        pg.on("pageerror", lambda e: loi.append(str(e)))
        pg.goto("file:///" + TRANG.replace("\\", "/"))
        pg.wait_for_function("() => window.__thu && window.__thu.xong()", timeout=60000)
        print("mở không mạng được, lỗi:", loi)
        for lop in DE:
            tot, xau = lay(lop, nd)
            dong = {}
            for nhom, ds in (("tot", tot), ("xau", xau)):
                r = pg.evaluate("(ds) => ds.map(n => window.__thu.dat(n))", ds)
                dong[nhom] = {"so": len(r), "top1": sum(1 for x in r if x[0][0] == lop), "top3": sum(1 for x in r if lop in [y[0] for y in x])}
            kq[lop] = dong
            print(lop, dong, flush=True)
        pg.screenshot(path=os.path.join(DAY, "thu.png"))
        b.close()
    json.dump(kq, open(ra, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    t = {n: [sum(kq[l][n][k] for l in kq) for k in ("top1", "top3", "so")] for n in ("tot", "xau")}
    print("tổng", t)
