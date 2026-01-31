# Django Article Platform

Maqolalarni nashr qilish platformasi - taqrizchilar tizimi bilan.

## Xususiyatlar

- Mualliflar maqola yaratadi va yuboradi
- Adminlar taqrizchilarni tayinlaydi
- Taqrizchilar tasdiqlasa - maqola avtomatik nashr bo'ladi
- Ko'p tilli qo'llab-quvvatlash (O'zbek, Rus, Ingliz)
- Email va in-app bildirishnomalar

---

## O'rnatish

### 1. Loyihani yuklab olish

```bash
git clone https://github.com/Burkhanovich/article_site.git
cd article_site
```

### 2. Virtual muhit yaratish

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. Ma'lumotlar bazasini sozlash

```bash
python manage.py migrate
```

### 5. Superuser yaratish

```bash
python manage.py createsuperuser
```

Quyidagilarni kiriting:
- Username: `admin`
- Email: `admin@example.com`
- Password: (o'zingiz tanlang)

### 6. Statik fayllarni yig'ish (production uchun)

```bash
python manage.py collectstatic
```

### 7. Serverni ishga tushirish

```bash
python manage.py runserver
```

### 8. Brauzerni ochish

- **Sayt:** http://127.0.0.1:8000/
- **Admin panel:** http://127.0.0.1:8000/admin/

---

## Dastlabki sozlashlar (Admin panelda)

### 1. Turkumlar yaratish
`Admin → Articles → Categories → Add Category`

### 2. Taqrizchilar yaratish
`Admin → Users → Users → Add User`
- Role: **Reviewer**
- Keyin turkumlarga tayinlang

### 3. Mualliflar yaratish
`Admin → Users → Users → Add User`
- Role: **Author**

---

## Ish oqimi (Workflow)

```
Avtor maqola yuboradi → Admin taqrizchi tayinlaydi → Taqrizchi tasdiqlaydi → Avtomatik nashr
```

### Batafsil:

1. **Avtor** maqola yaratadi va "Submit for Review" bosadi
2. **Admin** bildirishnoma oladi va taqrizchi tayinlaydi
3. **Taqrizchi** maqolani ko'rib chiqadi:
   - "Approve" → Maqola **avtomatik nashr bo'ladi**
   - "Request Changes" → Avtor tuzatish qiladi
4. Barcha tomonlarga bildirishnomalar yuboriladi

---

## Foydalanuvchi rollari

| Rol | Imkoniyatlar |
|-----|--------------|
| **Reader** | Maqolalarni o'qish |
| **Author** | Maqola yaratish va yuborish |
| **Reviewer** | Maqolalarni ko'rib chiqish va tasdiqlash |
| **Admin** | To'liq boshqaruv |

---

## Muhim fayllar

| Fayl | Tavsif |
|------|--------|
| `config/settings.py` | Django sozlamalari |
| `articles/workflow.py` | Maqola ish oqimi |
| `articles/models.py` | Ma'lumotlar modellari |
| `users/services.py` | Bildirishnoma xizmatlari |

---

## Testlarni ishga tushirish

```bash
python manage.py test articles.tests.test_workflow -v2
```

---

## Tarjimalarni kompilyatsiya qilish (ixtiyoriy)

Windows uchun gettext o'rnating, keyin:
```bash
python manage.py compilemessages
```

---

## Muammolar va yechimlar

| Muammo | Yechim |
|--------|--------|
| `No module named 'xxx'` | `pip install -r requirements.txt` |
| `Table not found` | `python manage.py migrate` |
| Port band | `python manage.py runserver 8080` |
| Migration xatosi | `python manage.py migrate --run-syncdb` |

---

## Texnologiyalar

- **Backend:** Django 4.x
- **Frontend:** Bootstrap 5
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Editor:** CKEditor

---

## Litsenziya

MIT License
