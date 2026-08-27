# -*- coding: utf-8 -*-
"""
Rus va ingliz versiyalarini Telegraph sahifasiga joylash.

Telegraph — Telegram'ning o'z xizmati. Sahifa kanaldagi havolani bosganda
darhol, Telegram ichida ochiladi. Uzunlik cheklovi yo'q, kalit ham,
to'lov ham talab qilinmaydi.

Xizmat ishlamasa, post baribir yuboriladi — shunchaki havolasiz.
"""

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request

import konfig
import imzo

API = "https://api.telegra.ph/"
MUALLIF = "Sofia Mulladjanova — Integrative Aesthetic Medicine"

_TEG = re.compile(r"<[^>]+>")

oxirgi_sabab = ""


def _chaqir(metod, **maydonlar):
    data = urllib.parse.urlencode({
        k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)
        for k, v in maydonlar.items()
    }).encode("utf-8")
    so_rov = urllib.request.Request(API + metod, data=data)
    with urllib.request.urlopen(so_rov, timeout=30) as javob:
        return json.load(javob)


def _token():
    """Secret'dagi token yoki yangi hisob ochib olingan token."""
    mavjud = konfig.ol("TELEGRAPH_TOKEN")
    if mavjud:
        return mavjud
    natija = _chaqir("createAccount",
                     short_name="SofiaExpert",
                     author_name=MUALLIF,
                     author_url=imzo.INSTAGRAM)
    return natija["result"]["access_token"]


def _tugunlar(matn):
    """Matnni Telegraph tugunlariga (paragraflarga) aylantiradi."""
    toza = html.unescape(_TEG.sub("", matn))
    return [{"tag": "p", "children": [q.strip()]}
            for q in toza.split("\n") if q.strip()]


def sahifa_yarat(sarlavha, matn, izoh=None):
    """
    Sahifa yaratib, havolasini qaytaradi. Muvaffaqiyatsiz bo'lsa None.
    Sabab `telegraph.oxirgi_sabab` da qoladi.
    """
    global oxirgi_sabab
    if not matn.strip():
        oxirgi_sabab = "matn bo'sh"
        return None

    tugunlar = _tugunlar(matn)
    if izoh:
        tugunlar.append({"tag": "p", "children": [{"tag": "i", "children": [izoh]}]})
    tugunlar.append({"tag": "p", "children": [
        {"tag": "a", "attrs": {"href": imzo.INSTAGRAM}, "children": [MUALLIF]}]})

    try:
        natija = _chaqir("createPage",
                         access_token=_token(),
                         title=sarlavha[:250],
                         author_name=MUALLIF,
                         author_url=imzo.INSTAGRAM,
                         content=tugunlar)
    except urllib.error.HTTPError as e:
        oxirgi_sabab = "Telegraph xatosi {}".format(e.code)
        return None
    except urllib.error.URLError as e:
        oxirgi_sabab = "Telegraph'ga ulanib bo'lmadi: {}".format(e.reason)
        return None
    except (ValueError, KeyError):
        oxirgi_sabab = "Telegraph javobi tushunarsiz"
        return None

    if not natija.get("ok"):
        oxirgi_sabab = "Telegraph rad etdi: {}".format(natija.get("error"))
        return None

    oxirgi_sabab = "ok"
    return natija["result"]["url"]
