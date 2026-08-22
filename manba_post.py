# -*- coding: utf-8 -*-
"""
Ochiq manbadan post tayyorlab, Telegram kanalga yuboradi.

Ish tartibi:
  1. manbalar.json dan hali ishlatilmagan (manba + burchak) juftini oladi
  2. Manba sahifasi matnini yuklaydi (faqat matn, rasm olinmaydi)
  3. Claude API orqali o'zbek tilida post yozdiradi
  4. Kanalga yuboradi va juftni "ishlatilgan" deb belgilaydi

Manbalar: NIH/NIAMS va MedlinePlus davlat sahifalari — ochiq mulk (public domain).

Muhit o'zgaruvchilari (GitHub Secrets):
  ANTHROPIC_API_KEY, BOT_TOKEN, KANAL
"""

import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import anthropic

PAPKA = Path(__file__).parent
MANBALAR_FAYL = PAPKA / "manbalar.json"
ISHLATILGAN_FAYL = PAPKA / "ishlatilgan.txt"
LOG_FAYL = PAPKA / "jurnal.log"

MODEL = "claude-opus-5"
MAX_MANBA_BELGI = 12000     # manbadan olinadigan matn hajmi

YONALISH = """Sen professional kosmetolog Sofia Mulladjanovaning Telegram kanali uchun post yozasan.
Kanal auditoriyasi — O'zbekistondagi oddiy odamlar, tibbiy ma'lumotga ega emas.

QOIDALAR:
1. Faqat o'zbek tilida (lotin alifbosida) yoz. Rus yoki ingliz so'zlarini ishlatma.
2. Manbadagi matnni so'zma-so'z tarjima QILMA — mazmunini o'zlashtirib, o'z so'zlaring bilan qaytadan yoz.
3. Hajmi: 120–200 so'z. Telegram posti — qisqa va o'qishga oson bo'lsin.
4. Formatlash: <b>qalin</b> va <i>qiya</i> teglari ishlatiladi. Boshqa HTML teg ISHLATMA.
   Ro'yxatlar uchun ▪️ yoki raqamli emoji (1️⃣ 2️⃣) ishlat.
5. Sarlavha bilan boshla (emoji + <b>qalin matn</b>).
6. Manbada YO'Q ma'lumotni O'ZINGDAN QO'SHMA. Dori nomlari, dozalar, aniq raqamlar —
   faqat manbada bo'lsa yoz.
7. Hech qachon tashxis qo'yma va davolash tayinlama. Jiddiy holatlar uchun
   "mutaxassisga murojaat qiling" deb yoz.
8. Postni shu ikki qator bilan tugat (aynan shu ko'rinishda):

💬 Savolingiz bormi? Yozing!
<i>Manba: {manba_nomi}</i>

Javobingda faqat postning o'zini ber — izoh, muqaddima yoki "mana post" degan gap yozma."""


def log(xabar):
    print(xabar)
    with open(LOG_FAYL, "a", encoding="utf-8") as f:
        f.write("[{:%Y-%m-%d %H:%M:%S}] {}\n".format(datetime.now(), xabar))


def matn_ajratib_ol(url):
    """Sahifadan faqat o'qiladigan matnni ajratib oladi."""
    so_rov = urllib.request.Request(url, headers={"User-Agent": "SofiaExpertBot/1.0"})
    with urllib.request.urlopen(so_rov, timeout=45) as javob:
        xom = javob.read().decode("utf-8", errors="replace")

    # script/style/nav bloklarini olib tashlaymiz
    for teg in ("script", "style", "nav", "header", "footer", "form"):
        xom = re.sub(r"<{0}\b.*?</{0}>".format(teg), " ", xom, flags=re.S | re.I)
    matn = re.sub(r"<[^>]+>", " ", xom)
    matn = html.unescape(matn)
    matn = re.sub(r"\s+", " ", matn).strip()
    return matn[:MAX_MANBA_BELGI]


def navbatdagi_juft():
    """Hali ishlatilmagan (manba, burchak) juftini qaytaradi."""
    cfg = json.loads(MANBALAR_FAYL.read_text(encoding="utf-8"))
    ishlatilgan = set()
    if ISHLATILGAN_FAYL.exists():
        ishlatilgan = set(ISHLATILGAN_FAYL.read_text(encoding="utf-8").splitlines())

    # Burchaklar bo'ylab aylanamiz: avval hamma mavzuga 1-burchak, keyin 2-burchak...
    for b_raqam, burchak in enumerate(cfg["burchaklar"]):
        for manba in cfg["manbalar"]:
            kalit = "{}|{}".format(manba["url"], b_raqam)
            if kalit not in ishlatilgan:
                return kalit, manba, burchak, len(ishlatilgan), len(cfg["manbalar"]) * len(cfg["burchaklar"])
    return None, None, None, len(ishlatilgan), len(ishlatilgan)


def post_yozdir(mavzu, burchak, manba_matni, manba_nomi):
    mijoz = anthropic.Anthropic()   # ANTHROPIC_API_KEY muhitdan olinadi
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


def telegramga_yubor(matn, token, kanal):
    url = "https://api.telegram.org/bot{}/sendMessage".format(token)
    data = urllib.parse.urlencode({
        "chat_id": kanal,
        "text": matn,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as j:
            return json.load(j)
    except urllib.error.HTTPError as e:
        return {"ok": False, "description": e.read().decode("utf-8", errors="replace")}


def main():
    token = os.environ.get("BOT_TOKEN", "").strip()
    kanal = os.environ.get("KANAL", "").strip()
    if not token or not kanal:
        log("XATO: BOT_TOKEN yoki KANAL topilmadi.")
        sys.exit(1)
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        log("XATO: ANTHROPIC_API_KEY topilmadi.")
        sys.exit(1)

    kalit, manba, burchak, tugagan, jami = navbatdagi_juft()
    if kalit is None:
        log("Barcha mavzular ishlatilgan ({} ta). manbalar.json ga yangi manba yoki burchak qo'shing.".format(jami))
        return

    log("Tayyorlanmoqda: {} | {}".format(manba["mavzu"], burchak[:40]))

    try:
        manba_matni = matn_ajratib_ol(manba["url"])
    except Exception as e:
        log("XATO: manbani yuklab bo'lmadi ({}): {}".format(manba["url"], e))
        sys.exit(1)

    if len(manba_matni) < 500:
        log("XATO: manba matni juda qisqa, sahifa o'zgargan bo'lishi mumkin: {}".format(manba["url"]))
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

    natija = telegramga_yubor(post, token, kanal)
    if not natija.get("ok"):
        log("XATO: Telegram rad etdi: {}".format(natija.get("description")))
        sys.exit(1)

    with open(ISHLATILGAN_FAYL, "a", encoding="utf-8") as f:
        f.write(kalit + "\n")

    log("YUBORILDI: {} | qolgan mavzular: {}".format(manba["mavzu"], jami - tugagan - 1))


if __name__ == "__main__":
    main()
