# -*- coding: utf-8 -*-
"""
Uch tilli postni yig'ish.

O'zbekcha matn ochiq ko'rinadi, rus va inglizcha versiyalar
<tg-spoiler> ichida — ustiga bosilganda ochiladi.

Telegram rasm izohi 1024 ko'rinadigan belgi bilan cheklangan.
Sig'masa, spoylerlar aniq hisob bo'yicha qisqartiriladi
(butunlay tashlab yuborilmaydi).
"""

import re

import telegram

BOLIM = re.compile(r"^\[(UZ|RU|EN)\]\s*$", re.M)

# Imzo va rasm krediti uchun zaxira
ZAXIRA = 130
# Spoyler shundan qisqa bo'lsa, ko'rsatishning ma'nosi yo'q
ENG_KAM_SPOYLER = 60


def bolimlarga_ajrat(javob):
    """Modelning [UZ]/[RU]/[EN] javobini lug'atga ajratadi."""
    qismlar = BOLIM.split(javob.strip())
    natija = {}
    # split natijasi: ['', 'UZ', matn, 'RU', matn, 'EN', matn]
    for i in range(1, len(qismlar) - 1, 2):
        natija[qismlar[i]] = qismlar[i + 1].strip()
    return natija


def _qisqartir(matn, chegara):
    """Matnni so'z chegarasida kesadi."""
    if len(matn) <= chegara:
        return matn
    if chegara <= 1:
        return ""
    kesilgan = matn[:chegara - 1].rsplit(" ", 1)[0].rstrip(" ,.;:—-")
    return (kesilgan + "…") if kesilgan else ""


def _tuz(uz, ru, en, manba_nomi):
    qismlar = [uz, "", "<i>Manba: {}</i>".format(manba_nomi)]
    if ru:
        qismlar += ["", "🇷🇺 <b>Русский</b>", "<tg-spoiler>{}</tg-spoiler>".format(ru)]
    if en:
        qismlar += ["", "🇬🇧 <b>English</b>", "<tg-spoiler>{}</tg-spoiler>".format(en)]
    return "\n".join(qismlar)


def yig(bolimlar, manba_nomi):
    """
    Yakuniy post matnini qaytaradi.
    Imzo va rasm krediti keyinroq telegram.yubor() da qo'shiladi.
    """
    uz = bolimlar.get("UZ", "").strip()
    ru = bolimlar.get("RU", "").strip()
    en = bolimlar.get("EN", "").strip()
    if not uz:
        raise ValueError("O'zbekcha matn yo'q")

    chegara = telegram.CAPTION_CHEGARA - ZAXIRA
    olchov = telegram.korinadigan_uzunlik

    # Hammasi sig'sa - o'zgartirmaymiz
    toliq = _tuz(uz, ru, en, manba_nomi)
    if olchov(toliq) <= chegara:
        return toliq

    # Asos (o'zbekcha + manba + sarlavhalar) qancha joy egallaydi?
    asos = olchov(_tuz(uz, "x", "x", manba_nomi)) - 2

    # O'zbekchaning o'zi sig'masa - uni ham qisqartiramiz
    if asos > chegara:
        ortiqcha = asos - chegara
        uz = _qisqartir(uz, max(len(uz) - ortiqcha - 1, 100))
        asos = olchov(_tuz(uz, "x", "x", manba_nomi)) - 2

    bosh_joy = chegara - asos
    if bosh_joy < ENG_KAM_SPOYLER * 2:
        # Faqat bittasiga joy bor - ruschani qoldiramiz
        if bosh_joy >= ENG_KAM_SPOYLER:
            return _tuz(uz, _qisqartir(ru, bosh_joy), "", manba_nomi)
        return _tuz(uz, "", "", manba_nomi)

    # Bo'sh joyni ikkiga bo'lamiz: ruschaga 55%, inglizchaga 45%
    ru_joy = int(bosh_joy * 0.55)
    en_joy = bosh_joy - ru_joy

    # Biri kalta bo'lsa, ortgan joyni ikkinchisiga beramiz
    if len(ru) < ru_joy:
        en_joy += ru_joy - len(ru)
    elif len(en) < en_joy:
        ru_joy += en_joy - len(en)

    return _tuz(uz, _qisqartir(ru, ru_joy), _qisqartir(en, en_joy), manba_nomi)
