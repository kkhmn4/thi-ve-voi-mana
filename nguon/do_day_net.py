# -*- coding: utf-8 -*-
"""Tìm độ dày nét cho kết quả đoán tốt nhất trên 12 đề dễ.

    python -X utf8 do_day_net.py <thư mục ndjson>
"""
import os
import sys

from playwright.sync_api import sync_playwright

import kiem_trang as K

DE = ["sun", "umbrella", "bicycle", "fish", "flower", "cat", "tree", "house", "star", "ice_cream", "apple", "clock"]

if __name__ == "__main__":
    nd = sys.argv[1]
    bo = {l: K.lay(l, nd) for l in DE}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        pg = b.new_context(viewport={"width": 1280, "height": 720}, offline=True).new_page()
        pg.goto("file:///" + K.TRANG.replace("\\", "/"))
        pg.wait_for_function("() => window.__thu && window.__thu.xong()", timeout=60000)
        for day in (3, 4, 5, 6, 8, 10, 12):
            pg.evaluate("(d) => { DU.day_net = d; }", day)
            t = {"tot": [0, 0, 0], "xau": [0, 0, 0]}
            for lop in DE:
                for nhom, ds in zip(("tot", "xau"), bo[lop]):
                    r = pg.evaluate("(ds) => ds.map(n => window.__thu.dat(n))", ds)
                    t[nhom][0] += sum(1 for x in r if x[0][0] == lop)
                    t[nhom][1] += sum(1 for x in r if lop in [y[0] for y in x])
                    t[nhom][2] += len(r)
            print("dày", day, t, flush=True)
        b.close()
