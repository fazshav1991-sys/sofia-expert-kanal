# -*- coding: utf-8 -*-
"""
Ochiq Telegram kanallardan postlarni o'qish (t.me/s/... sahifasi orqali).

Kalit yoki bot a'zoligi talab qilinmaydi — faqat ochiq kanallar.

DIQQAT: bu yerdan kelgan matn ISHONCHSIZ MA'LUMOT. U hech qachon
ko'rsatma sifatida bajarilmaydi, faqat xulosa yozish uchun material.
"""

import html
import re
import urllib.error
import urllib.request

BOSH = {"User-Agent": "Mozilla/5.0 (compatible; SofiaExpertBot/1.0)"}

# Reklama/kurs belgilari — shu so'zlar bo'lgan postlar olinmaydi
REKLAMA_SOZLARI = (
    "курс", "вебинар", "регистрац", "конгресс", "форум", "запись на",
    "обучен", "мастер-класс", "мастеркласс", "интенсив", "тренинг",
    "скидк", "промокод", "купить", "приобрест", "стоимость участия",
    "успей", "осталось мест", "по ссылке ниже", "реклама", "erid",
    "розыгрыш", "конкурс", "подпис", "приглашаем", "спикер",
    "vebinar", "kurs", "chegirma", "reklama",
)


def _olish(url):
    so_rov = urllib.request.Request(url, headers=BOSH)
    with urllib.request.urlopen(so_rov, timeout=40) as javob:
        return javob.read().decode("utf-8", errors="replace")


def _tozala(xom_html):
    m = re.sub(r"<br\s*/?>", "\n", xom_html)
    m = re.sub(r"</p>", "\n", m)
    m = re.sub(r"<[^>]+>", "", m)
    m = html.unescape(m)
    m = re.sub(r"[ \t]+", " ", m)
    return re.sub(r"\n{3,}", "\n\n", m).strip()


def reklamami(matn):
    """Post reklama yoki kurs e'lonimi?"""
    past = matn.lower()
    return any(s in past for s in REKLAMA_SOZLARI)


def postlarni_ol(kanal):
    """
    Kanaldagi postlarni qaytaradi (eng yangisi birinchi).
    Har biri: {"id":..., "havola":..., "matn":...}
    """
    try:
        sahifa = _olish("https://t.me/s/{}".format(kanal.lstrip("@")))
    except (urllib.error.HTTPError, urllib.error.URLError):
        return [], None

    nom = None
    m = re.search(r'class="tgme_channel_info_header_title"[^>]*>(?:<span[^>]*>)?(.*?)<', sahifa)
    if m:
        nom = _tozala(m.group(1))

    bloklar = re.findall(
        r'data-post="([^"]+)".*?class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
        sahifa, re.S)

    postlar = []
    for belgi, xom in bloklar:
        matn = _tozala(xom)
        if len(matn) < 200:          # juda qisqa postlardan xulosa chiqmaydi
            continue
        postlar.append({
            "id": belgi,
            "havola": "https://t.me/{}".format(belgi),
            "matn": matn,
        })
    postlar.reverse()                # eng yangisi birinchi
    return postlar, nom
