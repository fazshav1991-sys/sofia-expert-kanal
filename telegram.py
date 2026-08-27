# -*- coding: utf-8 -*-
"""Telegram kanalga post yuborish (rasm bilan yoki rasmsiz)."""

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request

import imzo

CAPTION_CHEGARA = 1024   # Telegram rasm izohi uchun belgi chegarasi
MATN_CHEGARA = 4096      # Oddiy xabar chegarasi

_TEG = re.compile(r"<[^>]+>")


def korinadigan_uzunlik(matn):
    """
    Telegram chegarani KO'RINADIGAN belgilar bo'yicha hisoblaydi.
    HTML teglar (<b>, <a href=...>, <tg-spoiler>) hisobga olinmaydi.
    """
    return len(html.unescape(_TEG.sub("", matn)))


def _so_rov(token, metod, maydonlar):
    url = "https://api.telegram.org/bot{}/{}".format(token, metod)
    data = urllib.parse.urlencode(maydonlar).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=45) as j:
            return json.load(j)
    except urllib.error.HTTPError as e:
        return {"ok": False, "description": e.read().decode("utf-8", errors="replace")}
    except urllib.error.URLError as e:
        return {"ok": False, "description": "ulanish xatosi: {}".format(e.reason)}


def yubor(token, kanal, matn, rasm_url=None, kredit=None):
    """
    Matn oxiriga imzo, undan keyin (bo'lsa) rasm krediti qo'shiladi.
    Rasm berilgan va izoh chegarasiga sig'sa — rasm + izoh.
    Aks holda oddiy matn xabari.

    Qaytaradi: (muvaffaqiyatmi, izoh)
    """
    matn = imzo.qosh(matn, kredit)
    uzunlik = korinadigan_uzunlik(matn)

    if rasm_url and uzunlik <= CAPTION_CHEGARA:
        natija = _so_rov(token, "sendPhoto", {
            "chat_id": kanal,
            "photo": rasm_url,
            "caption": matn,
            "parse_mode": "HTML",
        })
        if natija.get("ok"):
            return True, "rasm bilan, {} belgi".format(uzunlik)
        # Rasm yuborilmadi (masalan, URL ochilmadi) — matn bilan davom etamiz
        sabab = natija.get("description", "")[:80]
    else:
        sabab = ("matn uzun: {} > {}".format(uzunlik, CAPTION_CHEGARA)
                 if rasm_url else "rasm yo'q")

    natija = _so_rov(token, "sendMessage", {
        "chat_id": kanal,
        "text": matn,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    })
    if natija.get("ok"):
        return True, "rasmsiz ({})".format(sabab)
    return False, natija.get("description", "noma'lum xato")
