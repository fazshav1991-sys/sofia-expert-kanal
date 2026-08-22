# -*- coding: utf-8 -*-
"""
SOFIA EXPERT — Telegram kanalga avtomatik post yuboruvchi dastur.

Ishlash tartibi:
  1. "postlar" papkasidagi eng kichik raqamli, hali yuborilmagan .txt faylni topadi
  2. Uni Telegram kanalga yuboradi
  3. Fayl nomini "yuborilgan.txt" ga yozadi (qayta yubormaslik uchun)

Token qayerdan olinadi:
  - GitHub Actions'da  -> BOT_TOKEN / KANAL muhit o'zgaruvchilaridan (Secrets)
  - Kompyuterda        -> sozlamalar.json faylidan
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

PAPKA = Path(__file__).parent
POSTLAR = PAPKA / "postlar"
YUBORILGAN_FAYL = PAPKA / "yuborilgan.txt"
LOG_FAYL = PAPKA / "jurnal.log"
SOZLAMALAR_FAYL = PAPKA / "sozlamalar.json"


def log(xabar):
    print(xabar)
    with open(LOG_FAYL, "a", encoding="utf-8") as f:
        f.write("[{:%Y-%m-%d %H:%M:%S}] {}\n".format(datetime.now(), xabar))


def sozlamalarni_ol():
    """Avval muhit o'zgaruvchilari (GitHub Secrets), keyin sozlamalar.json."""
    token = os.environ.get("BOT_TOKEN", "").strip()
    kanal = os.environ.get("KANAL", "").strip()

    if not (token and kanal) and SOZLAMALAR_FAYL.exists():
        with open(SOZLAMALAR_FAYL, encoding="utf-8") as f:
            s = json.load(f)
        token = token or s.get("bot_token", "").strip()
        kanal = kanal or s.get("kanal", "").strip()

    if not token or "BU_YERGA" in token:
        log("XATO: bot token topilmadi (BOT_TOKEN secret yoki sozlamalar.json).")
        sys.exit(1)
    if not kanal:
        log("XATO: kanal nomi topilmadi (KANAL secret yoki sozlamalar.json).")
        sys.exit(1)

    return token, kanal


def main():
    token, kanal = sozlamalarni_ol()

    yuborilganlar = set()
    if YUBORILGAN_FAYL.exists():
        yuborilganlar = set(YUBORILGAN_FAYL.read_text(encoding="utf-8").split())

    navbat = sorted(p for p in POSTLAR.glob("*.txt") if p.name not in yuborilganlar)
    if not navbat:
        log("Navbatda post qolmadi. 'postlar' papkasiga yangilarini qo'shing.")
        return

    post_fayl = navbat[0]
    matn = post_fayl.read_text(encoding="utf-8").strip()

    url = "https://api.telegram.org/bot{}/sendMessage".format(token)
    data = urllib.parse.urlencode({
        "chat_id": kanal,
        "text": matn,
        "parse_mode": "HTML",
    }).encode("utf-8")

    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as javob:
            natija = json.load(javob)
    except urllib.error.HTTPError as e:
        # Tokenni jurnal va GitHub loglariga tushirmaymiz
        log("XATO: Telegram rad etdi ({}): {}".format(
            e.code, e.read().decode("utf-8", errors="replace")))
        sys.exit(1)
    except urllib.error.URLError as e:
        log("XATO: internetga ulanib bo'lmadi: {}".format(e.reason))
        sys.exit(1)

    if natija.get("ok"):
        with open(YUBORILGAN_FAYL, "a", encoding="utf-8") as f:
            f.write(post_fayl.name + "\n")
        log("YUBORILDI: {} -> {} (navbatda yana {} ta)".format(
            post_fayl.name, kanal, len(navbat) - 1))
    else:
        log("XATO: {}".format(natija))
        sys.exit(1)


if __name__ == "__main__":
    main()
