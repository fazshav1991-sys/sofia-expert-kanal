# -*- coding: utf-8 -*-
"""
Ochiq manbadan post tayyorlab, mos rasm bilan Telegram kanalga yuboradi.

Ish tartibi:
  1. manbalar.json dan hali ishlatilmagan (manba + burchak) juftini oladi
  2. Manba sahifasi matnini yuklaydi (faqat matn)
  3. Claude API orqali o'zbek tilida post yozdiradi
  4. Mavzuga mos rasm topadi (Pexels)
  5. Kanalga yuboradi va juftni "ishlatilgan" deb belgilaydi

Manbalar: NIH/NIAMS va MedlinePlus — ochiq mulk (public domain).
Rasmlar: Pexels — muallif nomi postda ko'rsatiladi.

GitHub Secrets: ANTHROPIC_API_KEY, BOT_TOKEN, KANAL, PEXELS_API_KEY
"""

import html
import json
import os
import random
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import anthropic

import konfig
import rasm
import telegram

PAPKA = Path(__file__).parent
MANBALAR_FAYL = PAPKA / "manbalar.json"
ISHLATILGAN_FAYL = PAPKA / "ishlatilgan.txt"
LOG_FAYL = PAPKA / "jurnal.log"

MODEL = "claude-opus-5"
MAX_MANBA_BELGI = 12000

YONALISH = """Sen professional kosmetolog Sofia Mulladjanovaning Telegram kanali uchun post yozasan.
Kanal auditoriyasi — O'zbekistondagi oddiy odamlar, tibbiy ma'lumotga ega emas.

QOIDALAR:
1. Faqat o'zbek tilida (lotin alifbosida) yoz. Rus yoki ingliz so'zlarini ishlatma.
2. Manbadagi matnni so'zma-so'z tarjima QILMA — mazmunini o'zlashtirib, o'z so'zlaring bilan qaytadan yoz.
3. Hajmi: 90-130 so'z. JAMI 700 BELGIDAN OSHMASIN — post rasm ostiga izoh bo'lib chiqadi
   va ostiga imzo qo'shiladi.
4. Formatlash: <b>qalin</b> va <i>qiya</i> teglari. Boshqa HTML teg ISHLATMA.
   Ro'yxat uchun ▪️ yoki 1️⃣ 2️⃣ 3️⃣ ishlat.
5. Sarlavha bilan boshla (emoji + <b>qalin matn</b>).
6. Manbada YO'Q ma'lumotni O'ZINGDAN QO'SHMA. Dori nomlari, dozalar, aniq raqamlar —
   faqat manbada bo'lsa yoz.
7. Hech qachon tashxis qo'yma va davolash tayinlama. Jiddiy holatlarda
   "mutaxassisga murojaat qiling" deb yoz.
8. Postni aynan shu qator bilan tugat:

<i>Manba: {manba_nomi}</i>

Javobingda faqat postning o'zini ber — izoh yoki muqaddima yozma."""


def log(xabar):
    print(xabar)
    with open(LOG_FAYL, "a", encoding="utf-8") as f:
        f.write("[{:%Y-%m-%d %H:%M:%S}] {}\n".format(datetime.now(), xabar))


def matn_ajratib_ol(url):
    """Sahifadan faqat o'qiladigan matnni ajratib oladi."""
    so_rov = urllib.request.Request(url, headers={"User-Agent": "SofiaExpertBot/1.0"})
    with urllib.request.urlopen(so_rov, timeout=45) as javob:
        xom = javob.read().decode("utf-8", errors="replace")

    for teg in ("script", "style", "nav", "header", "footer", "form"):
        xom = re.sub(r"<{0}\b.*?</{0}>".format(teg), " ", xom, flags=re.S | re.I)
    matn = re.sub(r"<[^>]+>", " ", xom)
    matn = html.unescape(matn)
    matn = re.sub(r"\s+", " ", matn).strip()
    return matn[:MAX_MANBA_BELGI]


def barcha_juftlar():
    """
    Barcha (manba, burchak) juftlarini BIR XIL tartibda qaytaradi.

    Tartib aralashtirilgan, lekin urug' (seed) qat'iy — shuning uchun
    har safar bir xil ketma-ketlik chiqadi va jadvalni oldindan ko'rish mumkin.
    Aralashtirishdan maqsad: ketma-ket kunlarda bir xil uslubdagi postlar
    chiqib qolmasligi.
    """
    cfg = json.loads(MANBALAR_FAYL.read_text(encoding="utf-8"))
    juftlar = [
        ("{}|{}".format(manba["url"], b_raqam), manba, burchak)
        for b_raqam, burchak in enumerate(cfg["burchaklar"])
        for manba in cfg["manbalar"]
    ]
    random.Random(20260823).shuffle(juftlar)
    return juftlar


def navbatdagi_juft():
    """Hali ishlatilmagan (manba, burchak) juftini qaytaradi."""
    ishlatilgan = set()
    if ISHLATILGAN_FAYL.exists():
        ishlatilgan = set(ISHLATILGAN_FAYL.read_text(encoding="utf-8").splitlines())

    juftlar = barcha_juftlar()
    for kalit, manba, burchak in juftlar:
        if kalit not in ishlatilgan:
            return kalit, manba, burchak, len(ishlatilgan), len(juftlar)
    return None, None, None, len(ishlatilgan), len(juftlar)


def post_yozdir(mavzu, burchak, manba_matni, manba_nomi):
    mijoz = anthropic.Anthropic()
    javob = mijoz.messages.create(
        model=MODEL,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        system=YONALISH.format(manba_nomi=manba_nomi),
        messages=[{
            "role": "user",
            "content": (
                "MAVZU: {}\n\n"
                "BU POSTNING BURCHAGI: {}\n\n"
                "MANBA MATNI (ingliz tilida, ochiq mulk):\n---\n{}\n---\n\n"
                "Shu manbaga tayanib, yuqoridagi burchak bo'yicha bitta Telegram posti yoz."
            ).format(mavzu, burchak, manba_matni),
        }],
    )
    return "".join(b.text for b in javob.content if b.type == "text").strip()


def main():
    konfig.muhitni_tozala("ANTHROPIC_API_KEY", "PEXELS_API_KEY")
    token = konfig.ol("BOT_TOKEN")
    kanal = konfig.ol("KANAL")
    if not token or not kanal:
        log("XATO: BOT_TOKEN yoki KANAL topilmadi.")
        sys.exit(1)
    if not konfig.ol("ANTHROPIC_API_KEY"):
        log("XATO: ANTHROPIC_API_KEY topilmadi.")
        sys.exit(1)

    kalit, manba, burchak, tugagan, jami = navbatdagi_juft()
    if kalit is None:
        log("Barcha {} mavzu ishlatilgan. manbalar.json ga yangi manba qo'shing.".format(jami))
        return

    log("Tayyorlanmoqda: {} | {}".format(manba["mavzu"], burchak[:45]))

    try:
        manba_matni = matn_ajratib_ol(manba["url"])
    except Exception as e:
        log("XATO: manbani yuklab bo'lmadi ({}): {}".format(manba["url"], e))
        sys.exit(1)

    if len(manba_matni) < 500:
        log("XATO: manba matni juda qisqa, sahifa o'zgargan: {}".format(manba["url"]))
        sys.exit(1)

    manba_nomi = "NIH / NIAMS" if "niams.nih.gov" in manba["url"] else "MedlinePlus (NIH)"

    try:
        post = post_yozdir(manba["mavzu"], burchak, manba_matni, manba_nomi)
    except anthropic.APIStatusError as e:
        log("XATO: Claude API ({}): {}".format(e.status_code, e.message))
        sys.exit(1)
    except anthropic.APIConnectionError:
        log("XATO: Claude API ga ulanib bo'lmadi.")
        sys.exit(1)

    if not post:
        log("XATO: bo'sh post qaytdi.")
        sys.exit(1)

    topilgan = rasm.rasm_top(manba.get("rasm_soz", "skincare beauty"))
    if not topilgan:
        log("RASM YO'Q: {}".format(rasm.oxirgi_sabab))

    ok, izoh = telegram.yubor(token, kanal, post,
                             rasm_url=topilgan["url"] if topilgan else None,
                             kredit=topilgan.get("kredit") if topilgan else None)
    if not ok:
        log("XATO: Telegram rad etdi: {}".format(izoh))
        sys.exit(1)

    if topilgan:
        rasm.belgilangan(topilgan["belgi"])
    with open(ISHLATILGAN_FAYL, "a", encoding="utf-8") as f:
        f.write(kalit + "\n")

    log("YUBORILDI: {} [{}] | qolgan mavzu: {}".format(
        manba["mavzu"], izoh, jami - tugagan - 1))


if __name__ == "__main__":
    main()
