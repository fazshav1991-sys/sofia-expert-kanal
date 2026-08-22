# -*- coding: utf-8 -*-
"""Telegram kanalga post yuborish (rasm bilan yoki rasmsiz)."""

import json
import urllib.error
import urllib.parse
import urllib.request

import imzo

CAPTION_CHEGARA = 1024   # Telegram rasm izohi uchun belgi chegarasi


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


def yubor(token, kanal, matn, rasm_url=None):
    """
    Matn oxiriga imzo avtomatik qo'shiladi.
    Rasm berilgan bo'lsa, rasm + izoh qilib yuboradi.
    Matn izoh chegarasidan uzun bo'lsa yoki rasm yuborilmasa, oddiy matn yuboradi.
    Qaytaradi: (muvaffaqiyatmi, izoh)
    """
    matn = imzo.qosh(matn)

    if rasm_url and len(matn) <= CAPTION_CHEGARA:
        natija = _so_rov(token, "sendPhoto", {
            "chat_id": kanal,
            "photo": rasm_url,
            "caption": matn,
            "parse_mode": "HTML",
        })
        if natija.get("ok"):
            return True, "rasm bilan"
        # Rasm yuborilmadi (masalan, URL ochilmadi) - matn bilan davom etamiz
        sabab = natija.get("description", "")
    else:
        sabab = "matn uzun ({} belgi)".format(len(matn)) if rasm_url else "rasm yo'q"

    natija = _so_rov(token, "sendMessage", {
        "chat_id": kanal,
        "text": matn,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    })
    if natija.get("ok"):
        return True, "rasmsiz ({})".format(sabab)
    return False, natija.get("description", "noma'lum xato")
