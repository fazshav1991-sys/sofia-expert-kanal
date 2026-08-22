# -*- coding: utf-8 -*-
"""
Postga mos rasm topish.

Ikki manba qo'llab-quvvatlanadi:

  1. PIXABAY  — muallif ko'rsatish SHART EMAS (Pixabay Content License).
                Kalit bo'lsa, birinchi navbatda shundan olinadi.
  2. PEXELS   — API orqali olinganda muallifni ko'rsatish SHART.
                Faqat Pixabay kaliti bo'lmaganda ishlatiladi.

Bir rasm ikki marta ishlatilmaydi (ishlatilgan_rasmlar.txt).
Rasm topilmasa post rasmsiz ketadi — sababi jurnalga yoziladi.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import konfig

PAPKA = Path(__file__).parent
ISHLATILGAN_RASMLAR = PAPKA / "ishlatilgan_rasmlar.txt"

oxirgi_sabab = ""


def _ishlatilganlar():
    if ISHLATILGAN_RASMLAR.exists():
        return set(ISHLATILGAN_RASMLAR.read_text(encoding="utf-8").split())
    return set()


def _so_rov(url, sarlavhalar):
    """JSON qaytaradi yoki (None, sabab)."""
    so_rov = urllib.request.Request(url, headers=sarlavhalar)
    try:
        with urllib.request.urlopen(so_rov, timeout=30) as javob:
            return json.load(javob), None
    except urllib.error.HTTPError as e:
        tafsilot = e.read().decode("utf-8", errors="replace")[:150]
        if e.code in (400, 401, 403):
            return None, "kalit noto'g'ri ({})".format(e.code)
        if e.code == 429:
            return None, "limit tugadi (429)"
        return None, "xato {}: {}".format(e.code, tafsilot)
    except urllib.error.URLError as e:
        return None, "ulanib bo'lmadi: {}".format(e.reason)
    except ValueError:
        return None, "javob tushunarsiz"


def _pixabay(qidiruv, kalit, ishlatilgan):
    url = "https://pixabay.com/api/?" + urllib.parse.urlencode({
        "key": kalit,
        "q": qidiruv,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": 50,
    })
    natija, xato = _so_rov(url, {"User-Agent": "SofiaExpertBot/1.0"})
    if xato:
        return None, "Pixabay: " + xato

    fotolar = natija.get("hits", [])
    if not fotolar:
        return None, "Pixabay: '{}' bo'yicha rasm yo'q".format(qidiruv)

    for foto in fotolar:
        belgi = "pixabay-{}".format(foto["id"])
        if belgi not in ishlatilgan:
            return {
                "url": foto.get("largeImageURL") or foto["webformatURL"],
                "belgi": belgi,
                "kredit": None,          # Pixabay kredit talab qilmaydi
            }, None
    return None, "Pixabay: '{}' bo'yicha {} ta rasmning hammasi ishlatilgan".format(
        qidiruv, len(fotolar))


def _pexels(qidiruv, kalit, ishlatilgan):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": qidiruv,
        "per_page": 40,
        "orientation": "landscape",
    })
    natija, xato = _so_rov(url, {
        "Authorization": kalit,
        "User-Agent": "SofiaExpertBot/1.0",
    })
    if xato:
        return None, "Pexels: " + xato

    fotolar = natija.get("photos", [])
    if not fotolar:
        return None, "Pexels: '{}' bo'yicha rasm yo'q".format(qidiruv)

    for foto in fotolar:
        belgi = "pexels-{}".format(foto["id"])
        if belgi not in ishlatilgan:
            return {
                "url": foto["src"]["large"],
                "belgi": belgi,
                # Pexels API shartiga ko'ra muallif ko'rsatilishi SHART
                "kredit": "📷 <i>Foto: {} / Pexels</i>".format(
                    foto.get("photographer", "Pexels")),
            }, None
    return None, "Pexels: '{}' bo'yicha {} ta rasmning hammasi ishlatilgan".format(
        qidiruv, len(fotolar))


def rasm_top(qidiruv):
    """
    Qaytaradi: {"url":..., "belgi":..., "kredit": matn yoki None} yoki None.
    Sabab `rasm.oxirgi_sabab` da qoladi.
    """
    global oxirgi_sabab
    ishlatilgan = _ishlatilganlar()
    sabablar = []

    pixabay_kalit = konfig.ol("PIXABAY_API_KEY")
    if pixabay_kalit:
        topilgan, sabab = _pixabay(qidiruv, pixabay_kalit, ishlatilgan)
        if topilgan:
            oxirgi_sabab = "ok (Pixabay, kreditsiz)"
            return topilgan
        sabablar.append(sabab)

    pexels_kalit = konfig.ol("PEXELS_API_KEY")
    if pexels_kalit:
        topilgan, sabab = _pexels(qidiruv, pexels_kalit, ishlatilgan)
        if topilgan:
            oxirgi_sabab = "ok (Pexels, kredit bilan)"
            return topilgan
        sabablar.append(sabab)

    if not pixabay_kalit and not pexels_kalit:
        sabablar.append("PIXABAY_API_KEY ham, PEXELS_API_KEY ham yo'q")

    oxirgi_sabab = "; ".join(sabablar)
    return None


def belgilangan(belgi):
    with open(ISHLATILGAN_RASMLAR, "a", encoding="utf-8") as f:
        f.write(str(belgi) + "\n")
