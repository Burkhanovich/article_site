# Keyword Qo'shish Debug Qo'llanma

## Test qilish:

1. Serverni ishga tushiring:
```bash
python manage.py runserver
```

2. Article yaratish sahifasiga o'ting:
```
http://localhost:8000/articles/create/
```

3. Browser console'ni oching:
- Chrome/Edge: F12 yoki Ctrl+Shift+I
- Firefox: F12

4. Console'da quyidagi xabarlarni ko'ring:
```
=== Keyword Script Starting ===
Elements found:
- keywordsContainer: YES/NO
- keywordInput: YES/NO
- addBtn: YES/NO
- hiddenInput: YES/NO
- keywordError: YES/NO
- articleForm: YES/NO
```

5. Keyword kiriting va "Add" tugmasini bosing

6. Console'da quyidagilarni kuzating:
```
Add button clicked
addKeyword called
Input value: "test"
Keyword added. Total: 1
Rendering keywords: ["test"]
Hidden input synced: ["test"]
```

## Agar xatolik bo'lsa:

### Agar "hiddenInput: NO" ko'rsatsa:
- Console'da barcha hidden input'lar ro'yxati ko'rsatiladi
- Screenshot oling va yuboring

### Agar "Add button clicked" ko'rinmasa:
- Button element topilmayapti
- HTML strukturasida xatolik bor

### Agar keyword qo'shilmasa:
- Console'dagi xabarlarni to'liq ko'rsating

## Natijani yuboring:
Console'dagi barcha xabarlarni copy qilib yuboring.
