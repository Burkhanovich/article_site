# 🧪 Tarjimalarni Sinash / Testing Translations

## Tez Sinov / Quick Test

### 1. Serverni Ishga Tushiring:

```bash
python manage.py runserver
```

### 2. Uch Tilda Ochib Ko'ring:

#### O'zbekcha (Default):
http://127.0.0.1:8000/uz/

**Kutilgan ko'rinish:**
- Navigatsiya: **Bosh sahifa**, **Maqolalar**, **Kirish**, **Ro'yxatdan o'tish**
- Tugmalar: **Yuborish**, **Saqlash**, **Bekor qilish**

#### Ruscha:
http://127.0.0.1:8000/ru/

**Kutilgan ko'rinish:**
- Навигация: **Главная**, **Статьи**, **Вход**, **Регистрация**
- Кнопки: **Отправить**, **Сохранить**, **Отмена**

#### Inglizcha:
http://127.0.0.1:8000/en/

**Kutilgan ko'rinish:**
- Navigation: **Home**, **Articles**, **Login**, **Register**
- Buttons: **Submit**, **Save**, **Cancel**

### 3. Til Almashtirgichni Sinab Ko'ring:

1. Yuqori o'ng burchakdagi **🌐** belgisini bosing
2. Tilni tanlang (O'zbekcha / Русский / English)
3. Sahifa avtomatik ravishda yangi tilda ko'rinishi kerak

---

## ✅ Muvaffaqiyat Kriteriylari

Tarjimalar to'g'ri ishlasa:

- ✅ Har bir tilda URL prefiksi o'zgaradi (`/uz/`, `/ru/`, `/en/`)
- ✅ Navigatsiya menyusi to'liq tarjima qilingan
- ✅ Barcha tugmalar yangi tilda
- ✅ Xabarlar va ogohlantirishlar tarjima qilingan
- ✅ Til almashtirgich dropdown ko'rsatiladi
- ✅ Tanlangan til dropdown-da aktiv ko'rinadi

---

## 🎯 Sinov Ro'yxati

### Bosh Sahifa (Home Page):
- [ ] Sarlavha tarjima qilingan
- [ ] Navigatsiya menyusi to'liq tarjima qilingan
- [ ] Footer matni tarjima qilingan
- [ ] Til almashtirgich ishlaydi

### Ro'yxatdan O'tish (Registration):
- [ ] Forma maydonlari tarjima qilingan (Username, Email, Password)
- [ ] Tugmalar tarjima qilingan
- [ ] Xato xabarlari tarjima qilingan
- [ ] Muvaffaqiyat xabarlari tarjima qilingan

### Kirish (Login):
- [ ] Forma maydonlari tarjima qilingan
- [ ] "Kirish" tugmasi tarjima qilingan
- [ ] Xato xabarlari tarjima qilingan

### Maqolalar Ro'yxati (Articles List):
- [ ] Sarlavha tarjima qilingan
- [ ] Qidirish maydoni tarjima qilingan
- [ ] "Hech narsa topilmadi" xabari tarjima qilingan
- [ ] Pagination tarjima qilingan

### Xato Sahifalari (Error Pages):
- [ ] 404 sahifasi tarjima qilingan
- [ ] 403 sahifasi tarjima qilingan
- [ ] 500 sahifasi tarjima qilingan

---

## 🐛 Agar Tarjimalar Ko'rinmasa

### Muammo 1: Sahifa inglizchada qoladi

**Yechim:**
```bash
# Tarjimalarni qayta kompilyatsiya qiling:
python compile_translations.py

# Serverni qayta ishga tushiring:
python manage.py runserver
```

### Muammo 2: Til almashtirgich ishlamaydi

**Tekshiring:**
1. URL to'g'ri formatda: `/uz/`, `/ru/`, `/en/`
2. `config/urls.py` da `i18n_patterns` ishlatilganligini tekshiring
3. Middleware ro'yxatida `LocaleMiddleware` borligini tekshiring

**settings.py ni tekshiring:**
```python
MIDDLEWARE = [
    ...
    'django.middleware.locale.LocaleMiddleware',  # Bu bo'lishi kerak
    ...
]
```

### Muammo 3: Ba'zi so'zlar tarjima qilinmagan

**Sabab:** Template faylda `{% trans %}` tag ishlatilmagan

**Yechim:**
```django
{% load i18n %}

<!-- Noto'g'ri: -->
<h1>Home</h1>

<!-- To'g'ri: -->
<h1>{% trans "Home" %}</h1>
```

---

## 📸 Screenshot Test

Quyidagi sahifalardan screenshot oling va taqqoslang:

1. **Bosh sahifa O'zbekcha** - `/uz/`
2. **Bosh sahifa Ruscha** - `/ru/`
3. **Bosh sahifa Inglizcha** - `/en/`

Barcha sahifalar har xil tilda ko'rinishi kerak!

---

## ✨ Qo'shimcha Sinov

### Admin Panel:
1. http://127.0.0.1:8000/uz/admin/ - O'zbekcha
2. http://127.0.0.1:8000/ru/admin/ - Ruscha
3. http://127.0.0.1:8000/en/admin/ - Inglizcha

Admin panel ham tilga mos ravishda o'zgarishi kerak!

---

## 🎊 Barcha Testlar O'tsa...

**Tabriklaymiz! Tarjimalar to'liq ishga tushdi! 🎉**

Saytingiz endi professional multilingual platforma!

---

*Tarjimalar sinovi - Test Translations - Тест переводов*
