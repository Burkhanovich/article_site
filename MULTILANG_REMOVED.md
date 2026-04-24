# ✅ Ko'p Tillilik Olib Tashlandi

## O'zgarishlar:

### Oldin (6 ta field):
- Title (Uzbek) *
- Title (Russian)
- Title (English)
- Content (Uzbek) *
- Content (Russian)
- Content (English)

### Endi (2 ta field):
- Title *
- Content *

## O'zgartirilgan fayllar:

1. **articles/forms.py**
   - `title_ru`, `title_en` o'chirildi
   - `content_ru`, `content_en` o'chirildi
   - Faqat `title_uz` va `content_uz` qoldi
   - Label'lar soddalashtirildi

2. **templates/articles/article_form.html**
   - 6 ta field o'rniga 2 ta field
   - Icon qo'shildi (card-heading, file-text)
   - Sodda va tushunarli

## Natija:

Endi foydalanuvchilar article yaratishda:
- ✅ Faqat 1 marta title yozadi
- ✅ Faqat 1 marta content yozadi
- ✅ Tezroq va osonroq
- ✅ Chalkashlik yo'q

Database'da hali ham `title_uz`, `content_uz` field'lari ishlatiladi, lekin foydalanuvchi uchun oddiy "Title" va "Content" ko'rinadi.
