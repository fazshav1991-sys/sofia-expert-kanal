# SOFIA EXPERT — Telegram kanalni avtomatlashtirish qo'llanmasi

## Tizim qanday ishlaydi?

- `postlar/` papkasida postlaringiz turadi (har biri alohida .txt fayl, raqamlangan)
- `yubor.py` dasturi ishga tushganda **navbatdagi** postni kanalga yuboradi
- Yuborilgan postlar `yuborilgan.txt` da qayd qilinadi — hech qachon ikki marta yuborilmaydi
- Windows "Vazifalar rejalashtiruvchisi" (Task Scheduler) dasturni har kuni belgilangan vaqtda avtomatik ishga tushiradi

## SIZ BAJARADIGAN QADAMLAR (Telegram'da)

### 1. Kanal ochish
1. Telegram → chap yuqoridagi menyu → **"Yangi kanal"** (New Channel)
2. Nom: masalan **"Sofia Expert | Kosmetolog"**
3. Tavsif yozing (nima haqida kanal ekanligi)
4. **Ommaviy kanal** (Public) qiling va username tanlang, masalan: `sofia_expert_uz`

### 2. Bot yaratish
1. Telegram'da **@BotFather** ni qidirib toping va oching
2. `/newbot` yuboring
3. Bot nomi: `Sofia Expert Bot`
4. Bot username: masalan `sofia_expert_post_bot` (oxiri `bot` bilan tugashi shart)
5. BotFather bergan **TOKEN** ni nusxalab oling (masalan `1234567890:AAExxx...`)
   - ⚠️ Bu token — kalit! Hech kimga bermang, kanalda e'lon qilmang.

### 3. Botni kanalga admin qilish
1. Kanalingizni oching → nomini bosing → **Administratorlar** → **Administrator qo'shish**
2. Botingizni username orqali qidiring va qo'shing
3. **"Xabarlarni joylash"** (Post Messages) huquqi yoqilgan bo'lsin

### 4. Sozlamalarni kiritish
`sozlamalar.json` faylini oching va to'ldiring:

```json
{
  "bot_token": "1234567890:AAExxx...",
  "kanal": "@sofia_expert_uz"
}
```

## SINOV

Terminalda shu buyruqni bajaring (yoki menga ayting, men bajaraman):

```
python yubor.py
```

Birinchi post (001-tanishuv.txt) kanalga tushishi kerak.

## AVTOMATIK JADVAL

Sozlamalar tayyor bo'lgach, Windows har kuni belgilangan soatda (masalan 10:00) dasturni o'zi ishga tushiradigan qilib qo'yamiz — buni men sozlab beraman.

## YANGI POSTLAR QO'SHISH

`postlar/` papkasiga yangi .txt fayl qo'shing, nomini keyingi raqam bilan boshlang:
- `006-yangi-post.txt`
- `007-boshqa-post.txt`

Postlar raqam tartibida, kuniga bittadan chiqadi. Formatlash uchun:
- `<b>qalin matn</b>`
- `<i>qiya matn</i>`
- Emojilardan bemalol foydalaning 😊

## FAYLLAR

| Fayl | Vazifasi |
|------|----------|
| `sozlamalar.json` | Bot token va kanal nomi |
| `yubor.py` | Post yuboruvchi dastur |
| `postlar/` | Postlar navbati |
| `yuborilgan.txt` | Yuborilgan postlar ro'yxati (avtomatik) |
| `jurnal.log` | Har bir yuborish tarixi (avtomatik) |
