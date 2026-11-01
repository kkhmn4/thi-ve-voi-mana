# -*- coding: utf-8 -*-
"""Chơi thi-ve-voi-ai.html như học sinh, tắt mạng, thao tác chuột thật: hết 60 giây, có gôm, có bỏ qua. Đo giây, đo chồng tiếng, chụp ảnh.

    python -X utf8 thu_nhu_giao_vien.py <thư mục ndjson> <thư mục ảnh> [rong cao]
"""
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

import kiem_trang as K

THEO_DOI = """() => { const A = window.Audio; window.__tieng = []; const P = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () { window.__tieng.push({ bat: performance.now(), dai: 0 });
    this.addEventListener('loadedmetadata', () => { const m = window.__tieng[window.__tieng.length - 1]; m.dai = this.duration; }, { once: true });
    window.__so_kenh = (window.__so_kenh || new Set()).add(this); return P.call(this); }; }"""


def ve(pg, ns, nhanh=1):
    h = pg.locator("#ve").bounding_box()
    if not h or not h["width"]:
        return
    tl = min(h["width"], h["height"]) * 0.85 / 255
    for n in ns:
        if not pg.evaluate("() => window.__thu.the().dangVe"):
            return
        pts = [(h["x"] + 30 + x * tl, h["y"] + 20 + y * tl) for x, y in n]
        pg.mouse.move(*pts[0])
        pg.mouse.down()
        for q in pts[1:]:
            pg.mouse.move(*q, steps=2)
        pg.mouse.up()
        pg.wait_for_timeout(120)


def choi(pg, nd, ra, kq):
    t0 = time.time()
    pg.locator("#nut_choi").click()
    da_gom = da_bo = False
    while time.time() - t0 < 170:
        if pg.locator("#m_ket.hien").count():
            break
        if pg.evaluate("() => window.__thu.the().dangVe") is False:
            pg.wait_for_timeout(200)
            continue
        th = pg.evaluate("() => window.__thu.the()")
        lop = pg.evaluate("() => window.__thu.netDe()")
        if th["deThu"] == 1 and not da_bo:
            pg.screenshot(path=os.path.join(ra, "3-truoc-bo-qua.png"))
            pg.locator("#nut_bo").click()
            da_bo = True
            kq["bo_qua"] = pg.evaluate("() => window.__thu.the().ketQua")
            pg.wait_for_timeout(600)
            continue
        tot, xau = K.lay(lop, nd)
        hinh = xau[th["deThu"]] if th["deThu"] in (3, 5) else tot[th["deThu"] % len(tot)]
        if th["deThu"] == 2 and not da_gom:
            h = pg.locator("#ve").bounding_box()
            pg.mouse.move(h["x"] + 60, h["y"] + 120)
            pg.mouse.down()
            pg.mouse.move(h["x"] + 400, h["y"] + 120, steps=12)
            pg.mouse.up()
            truoc = pg.evaluate("() => window.__thu.the()")
            pg.locator("#nut_gom").click()
            pg.mouse.move(h["x"] + 230, h["y"] + 100)
            pg.mouse.down()
            pg.mouse.move(h["x"] + 230, h["y"] + 140, steps=6)
            pg.wait_for_timeout(200)
            pg.screenshot(path=os.path.join(ra, "4-gom.png"))
            pg.mouse.up()
            sau = pg.evaluate("() => window.__thu.the()")
            kq["gom"] = {"net_truoc": truoc["soNet"], "net_sau": sau["soNet"], "diem_truoc": truoc["soDiem"], "diem_sau": sau["soDiem"]}
            pg.locator("#nut_xoa").click()
            kq["xoa_het"] = pg.evaluate("() => window.__thu.the().soNet")
            pg.locator("#nut_but").click()
            da_gom = True
        pg.wait_for_timeout(2500)
        ve(pg, hinh)
        pg.wait_for_timeout(700)
        if th["deThu"] == 0:
            pg.screenshot(path=os.path.join(ra, "2-choi.png"))
        if pg.evaluate("() => window.__thu.the().dangVe") and pg.evaluate("() => window.__thu.the().deThu") == th["deThu"]:
            pg.wait_for_timeout(900)
            if pg.evaluate("() => window.__thu.the().dangVe") and pg.evaluate("() => window.__thu.the().deThu") == th["deThu"]:
                pg.locator("#nut_bo").click(timeout=3000)
                pg.wait_for_timeout(300)
    kq["giay_ca_luot"] = round(time.time() - t0, 1)
    pg.wait_for_timeout(1500)
    pg.screenshot(path=os.path.join(ra, "5-ket-qua.png"))
    kq["ket"] = pg.evaluate("() => window.__thu.the()")
    kq["ket_tom"] = pg.evaluate("() => window.__thu.xemKetQua()")
    for ten, chon in (("6-doan-dung.png", ".ket.dung"), ("7-doan-sai.png", ".ket.sai")):
        for i in range(pg.locator(chon).count()):
            pg.locator(chon).nth(i).click()
            pg.wait_for_timeout(800)
            ok = chon == ".ket.dung" or pg.locator("#tu_nham").is_visible()
            if ok:
                pg.screenshot(path=os.path.join(ra, ten))
                pg.locator("#nut_dong").click()
                break
            pg.locator("#nut_dong").click()
            pg.wait_for_timeout(300)


if __name__ == "__main__":
    nd, ra = sys.argv[1], sys.argv[2]
    rong, cao = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1366, 768)
    os.makedirs(ra, exist_ok=True)
    loi = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist", "--autoplay-policy=no-user-gesture-required"])
        ctx = b.new_context(viewport={"width": rong, "height": cao}, offline=True)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: loi.append(str(e)))
        pg.on("console", lambda m: loi.append(m.text) if m.type == "error" else None)
        pg.add_init_script("(" + THEO_DOI + ")()")
        t = time.time()
        pg.goto("file:///" + K.TRANG.replace("\\", "/"))
        pg.wait_for_function("() => window.__thu && window.__thu.xong()", timeout=90000)
        kq = {"giay_nap": round(time.time() - t, 1)}
        pg.wait_for_timeout(600)
        pg.screenshot(path=os.path.join(ra, "1-mo-dau.png"))
        choi(pg, nd, ra, kq)
        tieng = pg.evaluate("() => window.__tieng")
        kq["so_kenh"] = pg.evaluate("() => window.__so_kenh ? window.__so_kenh.size : 0")
        kq["so_cau"] = len(tieng)
        kq["tieng_loi"] = sum(1 for x in tieng if not x["dai"])
        kq["ngang"] = pg.evaluate("() => document.documentElement.scrollWidth <= innerWidth")
        kq["cau"] = [x[1] for x in pg.evaluate("() => window.__thu.nhatKi")]
        kq["loi_trang"] = loi
        b.close()
    print(json.dumps(kq, ensure_ascii=False, indent=0)[:2500])
