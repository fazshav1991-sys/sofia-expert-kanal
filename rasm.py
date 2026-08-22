# -*- coding: utf-8 -*-
"""
Postga mos rasm topish (Pexels API).

Pexels litsenziyasi tijorat maqsadida bepul foydalanishga ruxsat beradi,
ammo API orqali olinganda muallifni ko'rsatish SHART — shuning uchun
har bir postga "📷 Foto: <muallif> / Pexels" qatori qo'shiladi.

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

# Oxirgi urinish nima bilan tugagani — chaqiruvchi jurnalga yozishi uchun
oxirgi_sabab = ""


def _ishlatilganlar():
    if ISHLATILGAN_RASMLAR.exists():
        return set(ISHLATILGAN_RASMLAR.read_text(encoding="utf-8").split())
    return set()


def rasm_top(qidiruv):
    """
    Kalit so'z bo'yicha hali ishlatilmagan rasm qaytaradi.
    Qaytaradi: {"url":..., "muallif":..., "id":...} yoki None.
    Sabab `rasm.oxirgi_sabab` da qoladi.
    """
    global oxirgi_sabab

    kalit = konfig.ol("PEXELS_API_KEY")
    if not kalit:
        oxirgi_sabab = "PEXELS_API_KEY yo'q"
        return None

    ishlatilgan = _ishlatilganlar()
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": qidiruv,
        "per_page": 40,
        "orientation": "landscape",
    })
    so_rov = urllib.request.Request(url, headers={
        "Authorization": kalit,
        "User-Agent": "SofiaExpertBot/1.0",
    })

    try:
        with urllib.request.urlopen(so_rov, timeout=30) as javob:
            natija = json.load(javob)
    except urllib.error.HTTPError as e:
        tafsilot = e.read().decode("utf-8", errors="replace")[:200]
        if e.code == 401:
            oxirgi_sabab = "Pexels kaliti noto'g'ri (401)"
        elif e.code == 429:
            oxirgi_sabab = "Pexels limiti tugadi (429)"
        else:
            oxirgi_sabab = "Pexels xatosi {}: {}".format(e.code, tafsilot)
        return None
    except urllib.error.URLError as e:
        oxirgi_sabab = "Pexels'ga ulanib bo'lmadi: {}".format(e.reason)
        return None
    except ValueError:
        oxirgi_sabab = "Pexels javobi tushunarsiz"
        return None

    fotolar = natija.get("photos", [])
    if not fotolar:
        oxirgi_sabab = "'{}' bo'yicha rasm topilmadi".format(qidiruv)
        return None

    for foto in fotolar:
        if str(foto["id"]) not in ishlatilgan:
            oxirgi_sabab = "ok"
            return {
                "url": foto["src"]["large"],
                "muallif": foto.get("photographer", "Pexels"),
                "id": foto["id"],
            }

    oxirgi_sabab = "'{}' bo'yicha {} ta rasmning hammasi ishlatilgan".format(
        qidiruv, len(fotolar))
    return None


def belgilangan(rasm_id):
    with open(ISHLATILGAN_RASMLAR, "a", encoding="utf-8") as f:
        f.write(str(rasm_id) + "\n")
