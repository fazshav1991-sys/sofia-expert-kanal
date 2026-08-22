# -*- coding: utf-8 -*-
"""
Sozlamalarni muhitdan xavfsiz o'qish.

Secret'larni nusxalashda ko'pincha ko'rinmas belgilar (qator tashlash,
bo'sh joy, \r) tushib qoladi. Token va kalitlarda bunday belgilar
BO'LMAYDI, shuning uchun ularni butunlay olib tashlaymiz.
"""

import os
import re

# Har qanday bo'sh joy va boshqaruv belgisi
AXLAT = re.compile(r"[\s\x00-\x1f\x7f]+")


def tozala(qiymat):
    """Qiymatdan barcha bo'sh joy va ko'rinmas belgilarni olib tashlaydi."""
    if not qiymat:
        return ""
    return AXLAT.sub("", qiymat)


def ol(nom, majburiy=False):
    """Muhit o'zgaruvchisini tozalab qaytaradi."""
    qiymat = tozala(os.environ.get(nom, ""))
    if majburiy and not qiymat:
        raise SystemExit("XATO: {} topilmadi yoki bo'sh.".format(nom))
    return qiymat


def muhitni_tozala(*nomlar):
    """
    Ko'rsatilgan muhit o'zgaruvchilarini tozalab, o'z joyiga qaytarib qo'yadi.
    Anthropic SDK kabi kutubxonalar muhitdan o'zi o'qigani uchun kerak.
    """
    for nom in nomlar:
        xom = os.environ.get(nom)
        if xom:
            os.environ[nom] = tozala(xom)
