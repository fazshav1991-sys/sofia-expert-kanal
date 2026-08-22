# -*- coding: utf-8 -*-
"""
Postga mos rasm topish (Pexels API).

Pexels litsenziyasi tijorat maqsadida bepul foydalanishga ruxsat beradi,
ammo API orqali olinganda muallifni ko'rsatish SHART — shuning uchun
har bir postga "📷 Foto: <muallif> / Pexels" qatori qo'shiladi.

Bir rasm ikki marta ishlatilmaydi (ishlatilgan_rasmlar.txt).
PEXELS_API_KEY bo'lmasa, post rasmsiz yuboriladi (xato bermaydi).
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import konfig

PAPKA = Path(__file__).parent
ISHLATILGAN_RASMLAR = PAPKA / "ishlatilgan_rasmlar.txt"


def _ishlatilganlar():
    if ISHLATILGAN_RASMLAR.exists():
        return set(ISHLATILGAN_RASMLAR.read_text(encoding="utf-8").split())
    return set()


def _belgila(rasm_id):
    with open(ISHLATILGAN_RASMLAR, "a", encoding="utf-8") as f:
        f.write(str(rasm_id) + "\n")


def rasm_top(qidiruv):
    """
    Berilgan kalit so'z bo'yicha hali ishlatilmagan rasm qaytaradi.
    Qaytaradi: {"url":..., "muallif":..., "id":...} yoki None
    """
    kalit = konfig.ol("PEXELS_API_KEY")
    if not kalit:
        return None

    ishlatilgan = _ishlatilganlar()
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": qidiruv,
        "per_page": 30,
        "orientation": "landscape",
    })
    so_rov = urllib.request.Request(url, headers={"Authorization": kalit})

    try:
        with urllib.request.urlopen(so_rov, timeout=30) as javob:
            natija = json.load(javob)
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
        return None

    for foto in natija.get("photos", []):
        if str(foto["id"]) not in ishlatilgan:
            return {
                "url": foto["src"]["large"],
                "muallif": foto.get("photographer", "Pexels"),
                "id": foto["id"],
            }
    return None   # hammasi ishlatilgan


def belgilangan(rasm_id):
    _belgila(rasm_id)
