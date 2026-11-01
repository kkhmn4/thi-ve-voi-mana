# -*- coding: utf-8 -*-
"""Sinh thêm các câu của luật 20 giây mỗi hình, cùng giọng và cách xử lý với sua_giong.py.

    python -X utf8 sinh_cau_them.py
"""
import sua_giong as G
import tai_tai_nguyen as T
from vieneu import Vieneu

CAU = {"het_hinh": "Hết giờ hình này rồi. Mình sang hình khác nhé.", "xong_luot": "Xong rồi! Cùng xem các bạn đã vẽ gì nhé.",
       "thu_thach": "Thử thách khó đây, cố lên nhé!"}
for t in ("guitar", "lighthouse", "castle", "train"):
    CAU["v_" + t] = "Hãy vẽ %s nhé!" % T.NHAN[t]
    CAU["w_" + t] = "À, mình biết rồi! Đó là %s!" % T.NHAN[t]
v = Vieneu()
sr = int(getattr(v, "sample_rate", 48000))
for k, c in CAU.items():
    print(k, G.sinh(v, k, c, sr), flush=True)
