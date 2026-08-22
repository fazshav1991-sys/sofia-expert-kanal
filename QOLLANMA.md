# SOFIA EXPERT — Telegram kanal avtomatlashtiruvi

Kanal **GitHub serverlarida** ishlaydi. Kompyuter o'chiq bo'lsa ham,
har kuni **5 ta post** avtomatik chiqadi.

## Jadval

Toshkent vaqti bilan: **09:00, 12:00, 15:00, 18:00, 21:00**

> GitHub jadvali band paytlarda 5–30 daqiqa kechikishi mumkin — bu normal.

## Tizim qanday ishlaydi?

```
NIH/NIAMS + MedlinePlus  →  Claude o'zbekcha post yozadi  →  rasm qo'shiladi  →  kanal
       (ochiq mulk)              (manbaga havola bilan)        (Pixabay)
```

1. `manbalar.json` dan hali ishlatilmagan (manba + burchak) juftini oladi
2. Manba sahifasini o'qiydi
3. Claude uni o'zbek tilida qayta yozadi — so'zma-so'z tarjima emas
4. Mavzuga mos rasm topadi
5. Imzo qo'shib kanalga yuboradi

**Takrorlanmaydi:** har bir mavzu `ishlatilgan.txt` ga, har bir rasm
`ishlatilgan_rasmlar.txt` ga yozib boriladi.

## Keyingi postlarni ko'rish

```bash
python jadval.py 7
```

Keyingi 7 kunda qaysi mavzu qaysi soatda chiqishini ko'rsatadi.

## Fayllar

| Fayl | Vazifasi |
|------|----------|
| `manbalar.json` | Manbalar va burchaklar ro'yxati |
| `manba_post.py` | Manbadan post yozib yuboradi |
| `rasm.py` | Rasm topadi (Pixabay → Pexels) |
| `imzo.py` | Post oxiridagi imzo va Instagram havolasi |
| `telegram.py` | Kanalga yuborish |
| `konfig.py` | Kalitlarni tozalab o'qish |
| `kunlik.py` | Dispetcher — qaysi rejimda ishlashni hal qiladi |
| `jadval.py` | Kelgusi postlar jadvali |
| `yubor.py` | Qo'lda yozilgan postlarni yuboradi |
| `postlar/` | Qo'lda yozilgan postlar (hozir bo'sh, ixtiyoriy) |
| `ishlatilgan.txt` · `ishlatilgan_rasmlar.txt` · `jurnal.log` | Avtomatik yuritiladi |
| `sozlamalar.json` | Token — **faqat kompyuterda**, GitHub'ga chiqmaydi |

## GitHub Secrets

| Nom | Nima uchun | Majburiymi |
|-----|-----------|-----------|
| `BOT_TOKEN` | Telegram bot tokeni (46 belgi) | ✅ Ha |
| `KANAL` | `@sofiamulladjanovakosmetolog` | ✅ Ha |
| `ANTHROPIC_API_KEY` | Post yozish uchun | ✅ Ha |
| `PIXABAY_API_KEY` | Rasm (kredit talab qilmaydi) | Tavsiya |
| `PEXELS_API_KEY` | Zaxira rasm manbasi (kredit majburiy) | Ixtiyoriy |

⚠️ Kalitni joylashda `Enter` bosmang va bo'sh joy qoldirmang.

## Mavzu tugaganda

`manbalar.json` ga yangi manba qo'shing:

```json
{"mavzu": "Nomi", "url": "https://...", "rasm_soz": "search words in english"}
```

Yoki `burchaklar` ro'yxatiga yangi burchak qo'shing — u **barcha** manbalarga
qo'llanadi, ya'ni bitta burchak = 30 ta yangi post.

## Vaqtni o'zgartirish

`.github/workflows/post.yml` dagi cron qatori. GitHub **UTC** da ishlaydi,
Toshkent = UTC + 5:

| Toshkent | UTC |
|----------|-----|
| 09:00 | 04:00 |
| 12:00 | 07:00 |
| 15:00 | 10:00 |
| 18:00 | 13:00 |
| 21:00 | 16:00 |

## Qo'lda ishga tushirish

GitHub → **Actions** → *Kanalga post yuborish* → **Run workflow**

Xato bo'lsa, sababi o'sha sahifadagi **Summary** bo'limida o'zbekcha yoziladi.

## Manbalar va huquq

- **NIH / NIAMS** va **MedlinePlus** davlat sahifalari — ochiq mulk (public domain),
  matnini erkin qayta ishlash mumkin. Har postda manba ko'rsatiladi.
- ❌ MedlinePlus'ning *A.D.A.M. Encyclopedia* bo'limi (`/ency/...`) mualliflik
  huquqi bilan himoyalangan — `manbalar.json` ga qo'shmang.
- **Pixabay** rasmlari kredit talab qilmaydi. **Pexels** API orqali olinganda
  muallif ko'rsatilishi shart — kod buni avtomatik qo'shadi.
