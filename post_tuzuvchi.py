# -*- coding: utf-8 -*-
"""
Uch tilli postni yig'ish.

O'zbekcha matn kanalda ochiq ko'rinadi.
Rus va ingliz versiyalari Telegraph sahifasiga joylanadi, kanalda
esa ko'k havola turadi — bosilganda Telegram ichida darhol ochiladi.

Telegraph ishlamasa, tarjimalar <tg-spoiler> ichida beriladi (zaxira yo'l).
Telegram rasm izohi 1024 ko'rinadigan belgi bilan cheklangan.
"""

import re

import telegram
import telegraph

BOLIM = re.compile(r"^\[(UZ|RU|EN)\]\s*$", re.M)

ZAXIRA = 130            # imzo va rasm krediti uchun
ENG_KAM_SPOYLER = 60


def bolimlarga_ajrat(javob):
    """Modelning [UZ]/[RU]/[EN] javobini lug'atga ajratadi."""
    qismlar = BOLIM.split(javob.strip())
    natija = {}
    for i in range(1, len(qismlar) - 1, 2):
        natija[qismlar[i]] = qismlar[i + 1].strip()
    return natija


def _qisqartir(matn, chegara):
    if len(matn) <= chegara:
        return matn
    if chegara <= 1:
        return ""
    kesilgan = matn[:chegara - 1].rsplit(" ", 1)[0].rstrip(" ,.;:—-")
    return (kesilgan + "…") if kesilgan else ""


def _sarlavha(uz):
    """O'zbekcha matnning birinchi qatoridan sarlavha ajratadi."""
    birinchi = uz.strip().split("\n")[0]
    return re.sub(r"<[^>]+>", "", birinchi).strip() or "Sofia Expert"


def _havolali(uz, manba_nomi, ru_url, en_url):
    qismlar = [uz, "", "<i>Manba: {}</i>".format(manba_nomi), ""]
    havolalar = []
    if ru_url:
        havolalar.append('🇷🇺 <a href="{}">Читать по-русски</a>'.format(ru_url))
    if en_url:
        havolalar.append('🇬🇧 <a href="{}">Read in English</a>'.format(en_url))
    qismlar.append("\n".join(havolalar))
    return "\n".join(qismlar).rstrip()


def _spoylerli(uz, ru, en, manba_nomi):
    qismlar = [uz, "", "<i>Manba: {}</i>".format(manba_nomi)]
    if ru:
        qismlar += ["", "🇷🇺 <b>Русский</b>", "<tg-spoiler>{}</tg-spoiler>".format(ru)]
    if en:
        qismlar += ["", "🇬🇧 <b>English</b>", "<tg-spoiler>{}</tg-spoiler>".format(en)]
    return "\n".join(qismlar)


def _spoylerga_moslash(uz, ru, en, manba_nomi):
    """Zaxira yo'l: spoylerlarni 1024 belgi chegarasiga sig'diradi."""
    chegara = telegram.CAPTION_CHEGARA - ZAXIRA
    olchov = telegram.korinadigan_uzunlik

    toliq = _spoylerli(uz, ru, en, manba_nomi)
    if olchov(toliq) <= chegara:
        return toliq

    asos = olchov(_spoylerli(uz, "x", "x", manba_nomi)) - 2
    if asos > chegara:
        uz = _qisqartir(uz, max(len(uz) - (asos - chegara) - 1, 100))
        asos = olchov(_spoylerli(uz, "x", "x", manba_nomi)) - 2

    bosh_joy = chegara - asos
    if bosh_joy < ENG_KAM_SPOYLER * 2:
        if bosh_joy >= ENG_KAM_SPOYLER:
            return _spoylerli(uz, _qisqartir(ru, bosh_joy), "", manba_nomi)
        return _spoylerli(uz, "", "", manba_nomi)

    ru_joy = int(bosh_joy * 0.55)
    en_joy = bosh_joy - ru_joy
    if len(ru) < ru_joy:
        en_joy += ru_joy - len(ru)
    elif len(en) < en_joy:
        ru_joy += en_joy - len(en)
    return _spoylerli(uz, _qisqartir(ru, ru_joy), _qisqartir(en, en_joy), manba_nomi)


def yig(bolimlar, manba_nomi, mavzu=""):
    """
    Yakuniy post matnini va qanday usul ishlatilganini qaytaradi.
    Imzo va rasm krediti keyinroq telegram.yubor() da qo'shiladi.

    Qaytaradi: (matn, usul_izohi)
    """
    uz = bolimlar.get("UZ", "").strip()
    ru = bolimlar.get("RU", "").strip()
    en = bolimlar.get("EN", "").strip()
    if not uz:
        raise ValueError("O'zbekcha matn yo'q")

    if not ru and not en:
        return _spoylerli(uz, "", "", manba_nomi), "tarjimasiz"

    sarlavha = mavzu or _sarlavha(uz)
    izoh = "Manba: {}".format(manba_nomi)

    ru_url = telegraph.sahifa_yarat(sarlavha, ru, izoh) if ru else None
    ru_sabab = telegraph.oxirgi_sabab
    en_url = telegraph.sahifa_yarat(sarlavha, en, izoh) if en else None

    if ru_url or en_url:
        matn = _havolali(uz, manba_nomi, ru_url, en_url)
        if telegram.korinadigan_uzunlik(matn) <= telegram.CAPTION_CHEGARA - ZAXIRA:
            return matn, "Telegraph havolalari"
        # Havolali variant ham sig'masa, o'zbekchani qisqartiramiz
        ortiqcha = (telegram.korinadigan_uzunlik(matn)
                    - (telegram.CAPTION_CHEGARA - ZAXIRA))
        uz_q = _qisqartir(uz, max(len(uz) - ortiqcha - 1, 100))
        return _havolali(uz_q, manba_nomi, ru_url, en_url), "Telegraph (matn qisqartirildi)"

    return (_spoylerga_moslash(uz, ru, en, manba_nomi),
            "spoyler (Telegraph ishlamadi: {})".format(ru_sabab))
