# SOFIA EXPERT — Telegram kanal avtomatlashtiruvi

Kanal **GitHub serverlarida** ishlaydi. Kompyuteringiz o'chiq bo'lsa ham,
har kuni Toshkent vaqti bilan **10:00** da kanalga bitta post avtomatik chiqadi.
Bepul.

## Tizim qanday ishlaydi?

```
postlar/  →  yubor.py  →  Telegram kanal
   ↑            ↑
   |     GitHub Actions har kuni 10:00 da ishga tushiradi
   |
 siz yangi postlar qo'shasiz
```

- `postlar/` — postlar navbati, raqam tartibida yuboriladi
- `yuborilgan.txt` — yuborilganlar ro'yxati, hech qachon takrorlanmaydi
- Postlar tugasa, tizim jim to'xtaydi (xato bermaydi)

## Fayllar

| Fayl | Vazifasi |
|------|----------|
| `postlar/` | Postlar navbati (28 ta tayyor) |
| `yubor.py` | Post yuboruvchi dastur |
| `.github/workflows/post.yml` | Kunlik jadval |
| `sozlamalar.json` | Token — **faqat kompyuterda**, GitHub'ga chiqmaydi |
| `yuborilgan.txt` | Yuborilganlar ro'yxati (avtomatik) |
| `jurnal.log` | Yuborish tarixi (avtomatik) |

## Vaqtni o'zgartirish

`.github/workflows/post.yml` dagi cron qatorini tahrirlang.
GitHub **UTC** vaqtida ishlaydi, Toshkent = UTC + 5 soat:

| Toshkent | cron |
|----------|------|
| 09:00 | `0 4 * * *` |
| 10:00 | `0 5 * * *` |
| 13:00 | `0 8 * * *` |
| 19:00 | `0 14 * * *` |
| 21:00 | `0 16 * * *` |

> GitHub jadvali band paytlarda 5–30 daqiqa kechikishi mumkin — bu normal.

## Yangi post qo'shish

`postlar/` papkasiga keyingi raqamli `.txt` fayl qo'shing (`029-...txt`),
keyin GitHub saytida faylni yuklang yoki `git push` qiling.

Formatlash: `<b>qalin</b>`, `<i>qiya</i>`, emojilar bemalol.

## Qo'lda ishga tushirish

- **GitHub'da:** repozitoriya → **Actions** → *Kanalga post yuborish* → **Run workflow**
- **Kompyuterda:** `python yubor.py`

## Xavfsizlik

- Bot tokeni GitHub'da **Secrets** ichida saqlanadi, kodda emas
- `sozlamalar.json` `.gitignore` da — GitHub'ga hech qachon yuklanmaydi
- Tokenni hech kimga bermang. Sizib chiqqan bo'lsa: @BotFather → `/mybots` → *API Token* → **Revoke** qilib yangisini oling
