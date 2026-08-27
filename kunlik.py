# -*- coding: utf-8 -*-
"""
Kunlik dispetcher. Navbat bilan uch manbani sinab ko'radi:

  1. postlar/    - qo'lda yozilgan postlar (bo'lsa, ular birinchi chiqadi)
  2. kanallar    - ochiq Telegram kanallardagi yangi kosmetologiya postlari
  3. manbalar    - NIH/NIAMS va MedlinePlus (har doim zaxirada bor)

Kanalda yangi mos post bo'lmasa (yoki hammasi reklama bo'lsa), avtomatik
ravishda NIH manbalariga o'tadi - shu tufayli kuniga 5 ta post uzilmaydi.
"""

import subprocess
import sys
from pathlib import Path

import konfig

PAPKA = Path(__file__).parent
POSTLAR = PAPKA / "postlar"
YUBORILGAN = PAPKA / "yuborilgan.txt"


def qolgan_qolda_postlar():
    if not POSTLAR.is_dir():
        return []
    yuborilgan = set()
    if YUBORILGAN.exists():
        yuborilgan = set(YUBORILGAN.read_text(encoding="utf-8").split())
    return [p for p in POSTLAR.glob("*.txt") if p.name not in yuborilgan]


def ishga_tushir(skript):
    return subprocess.run([sys.executable, str(PAPKA / skript)]).returncode


def main():
    konfig.muhitni_tozala("BOT_TOKEN", "KANAL", "ANTHROPIC_API_KEY",
                          "PEXELS_API_KEY", "PIXABAY_API_KEY", "TELEGRAPH_TOKEN")

    qolgan = qolgan_qolda_postlar()
    if qolgan:
        print("Rejim: qo'lda yozilgan post (navbatda {} ta)".format(len(qolgan)))
        return ishga_tushir("yubor.py")

    if (PAPKA / "kanallar.json").exists():
        print("Rejim: kanallardan post qidirilmoqda")
        if ishga_tushir("kanal_post.py") == 0:
            return 0
        print("Kanalda mos post yo'q - manbalarga o'tilmoqda")

    print("Rejim: manbadan AI post")
    return ishga_tushir("manba_post.py")


if __name__ == "__main__":
    sys.exit(main())
