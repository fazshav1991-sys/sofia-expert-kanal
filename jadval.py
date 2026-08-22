# -*- coding: utf-8 -*-
"""
Keyingi postlar jadvalini ko'rsatadi (hech narsa yubormaydi).

Ishlatish:
    python jadval.py          -> keyingi 3 kun
    python jadval.py 7        -> keyingi 7 kun
"""

import sys
from datetime import datetime, timedelta, timezone

import manba_post

# Toshkent vaqti bilan post chiqish soatlari
SOATLAR = [9, 12, 15, 18, 21]
TOSHKENT = timezone(timedelta(hours=5))


def main():
    kunlar = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    ishlatilgan = set()
    if manba_post.ISHLATILGAN_FAYL.exists():
        ishlatilgan = set(
            manba_post.ISHLATILGAN_FAYL.read_text(encoding="utf-8").splitlines())

    navbat = [(k, m, b) for k, m, b in manba_post.barcha_juftlar()
              if k not in ishlatilgan]

    hozir = datetime.now(TOSHKENT)
    vaqtlar = []
    kun = hozir.date()
    while len(vaqtlar) < kunlar * len(SOATLAR):
        for soat in SOATLAR:
            t = datetime.combine(kun, datetime.min.time(), TOSHKENT).replace(hour=soat)
            if t > hozir:
                vaqtlar.append(t)
        kun += timedelta(days=1)

    print("Navbatda {} ta mavzu ({} kunga yetadi)".format(
        len(navbat), len(navbat) // len(SOATLAR)))
    print("Chiqish soatlari (Toshkent): " + ", ".join("%02d:00" % s for s in SOATLAR))
    print()

    oxirgi_kun = None
    for t, (kalit, manba, burchak) in zip(vaqtlar, navbat):
        if t.date() != oxirgi_kun:
            oxirgi_kun = t.date()
            print("\n=== {:%d-%m-%Y, %A} ===".format(t).replace("Monday", "Dushanba")
                  .replace("Tuesday", "Seshanba").replace("Wednesday", "Chorshanba")
                  .replace("Thursday", "Payshanba").replace("Friday", "Juma")
                  .replace("Saturday", "Shanba").replace("Sunday", "Yakshanba"))
        print("{:%H:%M}  {:<28} — {}".format(t, manba["mavzu"], burchak.split(" - ")[0]))


if __name__ == "__main__":
    main()
