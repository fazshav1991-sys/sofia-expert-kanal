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
import post_tuzuvchi
import rasm
import telegram

PAPKA = Path(__file__).parent
MANBALAR_FAYL = PAPKA / "manbalar.json"
ISHLATILGAN_FAYL = PAPKA / "ishlatilgan.txt"
LOG_FAYL = PAPKA / "jurnal.log"

MODEL = "claude-opus-5"
MAX_MANBA_BELGI = 12000

YONALISH = """Sen professional mutaxassis Sofia Mulladjanovaning Telegram kanali uchun post yozasan.
Kanal auditoriyasi — O'zbekistondagi oddiy odamlar, tibbiy ma'lumotga ega emas.

Har bir post UCH TILDA yoziladi. Javobingni AYNAN shu ko'rinishda ber:

[UZ]
(o'zbekcha post, lotin alifbosida)
[RU]
(ruscha versiya)
[EN]
(inglizcha versiya)
[IMG]
(shu postga mos rasm uchun INGLIZ tilida 3-5 ta qidiruv so'zi)

HAJM:
- [UZ] — 300-400 belgi. Bu kanalda ochiq ko'rinadi, shuning uchun qisqa bo'lishi shart.
- [RU] va [EN] — 500-800 belgi. Bular alohida sahifada chiqadi, cheklov yo'q,
  shuning uchun TO'LIQROQ va batafsilroq yozilsin: mavzuni to'liq ochib ber.

[RU] va [EN] — o'zbekchaning so'zma-so'z tarjimasi emas, o'sha manbaga
tayangan mustaqil, to'liqroq matn.

QOIDALAR:
1. [UZ] bo'limi sarlavha bilan boshlanadi: emoji + <b>qalin matn</b>.
   [RU] va [EN] bo'limlarida sarlavha SHART EMAS, to'g'ridan-to'g'ri mazmun.
2. Manbadagi matnni so'zma-so'z tarjima QILMA — mazmunini o'z so'zlaring bilan yoz.
3. Formatlash: faqat <b>qalin</b> va <i>qiya</i>. Boshqa HTML teg ISHLATMA.
   Ro'yxat uchun ▪️ ishlat.
4. Manbada YO'Q ma'lumotni O'ZINGDAN QO'SHMA. Dori nomlari, dozalar, raqamlar —
   faqat manbada bo'lsa.
5. Hech qachon tashxis qo'yma va davolash tayinlama. Jiddiy holatlarda
   "mutaxassisga murojaat qiling" deb yoz.
6. Manba havolasi va imzoni O'ZING YOZMA — ular avtomatik qo'shiladi.

[IMG] BO'LIMI (rasm sifati shunga bog'liq):
- Ingliz tilida, 3-5 so'z. Aynan SHU POSTNING mazmuniga mos bo'lsin.
- Stok-fotoda topiladigan CHIROYLI, ijobiy sahna tasvirlansin:
  parvarish, krem surtish, salon, sog'lom teri, quyoshdan himoya kabi.
- Kasallik, yara, toshma, tibbiy asbob, qon, shifoxona kabi so'zlarni ISHLATMA -
  ular kanalga yoqimsiz rasm olib keladi.
- Yomon misol: "acne skin disease closeup", "psoriasis lesion"
- Yaxshi misol: "woman applying face cream", "sunscreen on beach summer",
  "hair care routine bathroom", "clean fresh face portrait"

Javobingda faqat [UZ] [RU] [EN] [IMG] bo'limlarini ber, boshqa hech narsa yozma."""


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


def manba_nomini_top(url):
    """Havolaga qarab manba nomini aniqlaydi."""
    if "niams.nih.gov" in url:
        return "NIH / NIAMS"
    if "fda.gov" in url:
        return "FDA (AQSH)"
    return "MedlinePlus (NIH)"


def navbatdagi_juftlar(nechta=5):
    """
    Hali ishlatilmagan birinchi `nechta` juftni qaytaradi.

    Bir nechtasi kerak: agar manba sahifasi ochilmasa (sayt o'zgargan,
    404 bo'lgan), tizim to'xtamasdan keyingisiga o'tadi.
    """
    ishlatilgan = set()
    if ISHLATILGAN_FAYL.exists():
        ishlatilgan = set(ISHLATILGAN_FAYL.read_text(encoding="utf-8").splitlines())

    juftlar = barcha_juftlar()
    qolgan = [(k, m, b) for k, m, b in juftlar if k not in ishlatilgan]
    return qolgan[:nechta], len(ishlatilgan), len(juftlar)


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
    xom = "".join(b.text for b in javob.content if b.type == "text").strip()
    bolimlar = post_tuzuvchi.bolimlarga_ajrat(xom)
    if not bolimlar.get("UZ"):
        raise ValueError("Model [UZ] bo'limini bermadi. Javob boshi: " + xom[:120])
    return bolimlar


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

    nomzodlar, tugagan, jami = navbatdagi_juftlar()
    if not nomzodlar:
        log("Barcha {} mavzu ishlatilgan. manbalar.json ga yangi manba qo'shing.".format(jami))
        return

    # Manba ochilmasa keyingisiga o'tamiz
    kalit = manba = burchak = manba_matni = None
    for n_kalit, n_manba, n_burchak in nomzodlar:
        try:
            matn = matn_ajratib_ol(n_manba["url"])
        except Exception as e:
            log("MANBA OCHILMADI ({}): {} - keyingisiga o'tilmoqda".format(n_manba["mavzu"], e))
            continue
        if len(matn) < 500:
            log("MANBA JUDA QISQA ({}) - keyingisiga o'tilmoqda".format(n_manba["mavzu"]))
            continue
        kalit, manba, burchak, manba_matni = n_kalit, n_manba, n_burchak, matn
        break

    if manba_matni is None:
        log("XATO: {} ta manbaning hech biri ochilmadi.".format(len(nomzodlar)))
        sys.exit(1)

    log("Tayyorlanmoqda: {} | {}".format(manba["mavzu"], burchak[:45]))

    manba_nomi = manba_nomini_top(manba["url"])

    try:
        bolimlar = post_yozdir(manba["mavzu"], burchak, manba_matni, manba_nomi)
    except anthropic.APIStatusError as e:
        log("XATO: Claude API ({}): {}".format(e.status_code, e.message))
        sys.exit(1)
    except anthropic.APIConnectionError:
        log("XATO: Claude API ga ulanib bo'lmadi.")
        sys.exit(1)
    except ValueError as e:
        log("XATO: {}".format(e))
        sys.exit(1)

    post, usul = post_tuzuvchi.yig(bolimlar, manba_nomi, manba["mavzu"])
    log("Tillar: {} | Tarjima usuli: {}".format(", ".join(sorted(bolimlar)), usul))

    rasm_soz = bolimlar.get("IMG", "").strip() or manba.get("rasm_soz", "skincare beauty")
    log("Rasm qidiruvi: {}".format(rasm_soz))
    topilgan = rasm.rasm_top(rasm_soz)
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
