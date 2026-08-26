# -*- coding: utf-8 -*-
"""
Qo'lda yozilgan navbatdagi postni mos rasm bilan Telegram kanalga yuboradi.

  1. "postlar" papkasidagi eng kichik raqamli, hali yuborilmagan .txt faylni topadi
  2. post_rasmlari.json dan mos rasm kalit so'zini oladi va Pexels'dan rasm topadi
  3. Kanalga yuboradi
  4. Fayl nomini "yuborilgan.txt" ga yozadi

Token: GitHub Secrets (BOT_TOKEN / KANAL) yoki kompyuterda sozlamalar.json
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import konfig
import rasm
import telegram

PAPKA = Path(__file__).parent
POSTLAR = PAPKA / "postlar"
YUBORILGAN_FAYL = PAPKA / "yuborilgan.txt"
LOG_FAYL = PAPKA / "jurnal.log"
SOZLAMALAR_FAYL = PAPKA / "sozlamalar.json"
RASM_KALITLARI = PAPKA / "post_rasmlari.json"


def log(xabar):
    print(xabar)
    with open(LOG_FAYL, "a", encoding="utf-8") as f:
        f.write("[{:%Y-%m-%d %H:%M:%S}] {}\n".format(datetime.now(), xabar))


def sozlamalarni_ol():
    """Avval muhit o'zgaruvchilari (GitHub Secrets), keyin sozlamalar.json."""
    token = konfig.ol("BOT_TOKEN")
    kanal = konfig.ol("KANAL")

    if not (token and kanal) and SOZLAMALAR_FAYL.exists():
        with open(SOZLAMALAR_FAYL, encoding="utf-8") as f:
            s = json.load(f)
        token = token or konfig.tozala(s.get("bot_token", ""))
        kanal = kanal or konfig.tozala(s.get("kanal", ""))

    if not token or "BU_YERGA" in token:
        log("XATO: bot token topilmadi (BOT_TOKEN secret yoki sozlamalar.json).")
        sys.exit(1)
    if not kanal:
        log("XATO: kanal nomi topilmadi (KANAL secret yoki sozlamalar.json).")
        sys.exit(1)
    return token, kanal


def rasm_sozi(fayl_nomi):
    """Fayl nomining raqamiga qarab rasm kalit so'zini qaytaradi."""
    if not RASM_KALITLARI.exists():
        return "skincare beauty cosmetology"
    kalitlar = json.loads(RASM_KALITLARI.read_text(encoding="utf-8"))
    raqam = fayl_nomi.split("-")[0]
    return kalitlar.get(raqam, "skincare beauty cosmetology")


def main():
    token, kanal = sozlamalarni_ol()

    yuborilganlar = set()
    if YUBORILGAN_FAYL.exists():
        yuborilganlar = set(YUBORILGAN_FAYL.read_text(encoding="utf-8").split())

    navbat = sorted(p for p in POSTLAR.glob("*.txt") if p.name not in yuborilganlar)
    if not navbat:
        log("Navbatda qo'lda yozilgan post qolmadi.")
        return

    post_fayl = navbat[0]
    matn = post_fayl.read_text(encoding="utf-8").strip()

    topilgan = rasm.rasm_top(rasm_sozi(post_fayl.name))
    if not topilgan:
        log("RASM YO'Q: {}".format(rasm.oxirgi_sabab))

    ok, izoh = telegram.yubor(token, kanal, matn,
                             rasm_url=topilgan["url"] if topilgan else None,
                             kredit=topilgan.get("kredit") if topilgan else None)
    if not ok:
        log("XATO: Telegram rad etdi: {}".format(izoh))
        sys.exit(1)

    if topilgan:
        rasm.belgilangan(topilgan["belgi"])
    with open(YUBORILGAN_FAYL, "a", encoding="utf-8") as f:
        f.write(post_fayl.name + "\n")

    log("YUBORILDI: {} [{}] | navbatda yana {} ta".format(
        post_fayl.name, izoh, len(navbat) - 1))


if __name__ == "__main__":
    main()
