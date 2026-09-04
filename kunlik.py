# -*- coding: utf-8 -*-
"""
Kunlik dispetcher.

  1. postlar/  - qo'lda yozilgan postlar (bo'lsa, ular birinchi chiqadi)
  2. manbalar  - ishonchli tibbiy saytlardan AI yozgan post

Telegram kanallardan olish olib tashlandi: manbalar noaniq ma'lumot
berardi va sifatini nazorat qilib bo'lmasdi.
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

    print("Rejim: manbadan AI post")
    return ishga_tushir("manba_post.py")


if __name__ == "__main__":
    sys.exit(main())
