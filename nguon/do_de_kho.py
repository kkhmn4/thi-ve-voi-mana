# -*- coding: utf-8 -*-
"""Đo đề thử thách: hình khó vẽ nhưng AI vẫn nhận ra khi vẽ đúng. Xếp theo tỉ lệ trúng trong 3 dự đoán.

    python -X utf8 do_de_kho.py <thư mục ndjson>
"""
import sys
from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import sync_playwright

import kiem_trang as K

UNG_VIEN = ["bicycle", "helicopter", "castle", "butterfly", "spider", "windmill", "lighthouse", "crab", "octopus", "guitar", "train", "sailboat",
            "tractor", "hot_air_balloon", "elephant", "giraffe", "penguin", "owl", "scissors", "bus"]

if __name__ == "__main__":
    nd = sys.argv[1]
    with ThreadPoolExecutor(8) as tp:
        bo = dict(zip(UNG_VIEN, tp.map(lambda l: K.lay(l, nd), UNG_VIEN)))
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        pg = b.new_context(viewport={"width": 1280, "height": 720}).new_page()
        pg.goto("file:///" + K.TRANG.replace("\\", "/"))
        pg.wait_for_function("() => window.__thu && window.__thu.xong()", timeout=60000)
        kq = []
        for l in UNG_VIEN:
            tot, xau = bo[l]
            r = pg.evaluate("(ds) => ds.map(n => window.__thu.dat(n))", tot)
            r2 = pg.evaluate("(ds) => ds.map(n => window.__thu.dat(n))", xau)
            tinh = lambda rr: sum(1 for x in rr if l in [y[0] for y in x if y[1] >= 0.1])
            kq.append((tinh(r), tinh(r2), l, len(r)))
        b.close()
    for x in sorted(kq, reverse=True):
        print(x, flush=True)
