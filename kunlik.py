# -*- coding: utf-8 -*-
"""
Kunlik dispetcher.

Avval "postlar" papkasidagi qo'lda yozilgan postlarni yuboradi.
Ular tugagach, avtomatik ravishda manbalardan AI post tayyorlashga o'tadi.
"""

import subprocess
import sys
from pathlib import Path

import konfig

PAPKA = Path(__file__).parent
POSTLAR = PAPKA / "postlar"
YUBORILGAN = PAPKA / "yuborilgan.txt"


def qolgan_qolda_postlar():
    yuborilgan = set()
    if YUBORILGAN.exists():
        yuborilgan = set(YUBORILGAN.read_text(encoding="utf-8").split())
    if not POSTLAR.is_dir():
        return []
    return [p for p in POSTLAR.glob("*.txt") if p.name not in yuborilgan]


def ishga_tushir(skript):
    return subprocess.run([sys.executable, str(PAPKA / skript)]).returncode


def main():
    konfig.muhitni_tozala("BOT_TOKEN", "KANAL",
                          "ANTHROPIC_API_KEY", "PEXELS_API_KEY")
    qolgan = qolgan_qolda_postlar()
    if qolgan:
        print("Rejim: qo'lda yozilgan post (navbatda {} ta)".format(len(qolgan)))
        return ishga_tushir("yubor.py")
    print("Rejim: manbadan AI post")
    return ishga_tushir("manba_post.py")


# Himoya: fayl import qilinganda ishga tushmasin, faqat to'g'ridan-to'g'ri
# chaqirilganda ishlasin.
if __name__ == "__main__":
    sys.exit(main())
