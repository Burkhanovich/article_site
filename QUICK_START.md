# ⚡ Quick Start Guide

Get the application running in 5 minutes!

## 🚀 Fastest Setup (Development with SQLite)

### Step 1: Install Dependencies

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Step 2: Configure for SQLite (Optional - Skip PostgreSQL)

Edit `config/settings.py` and uncomment these lines (around line 85-90):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Comment out the PostgreSQL configuration above it.

### Step 3: Run Migrations (if you skipped setup script)

```bash
# Activate virtual environment first
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run migrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Step 4: Create Initial Article Rules

```bash
python manage.py runserver
```

1. Go to http://127.0.0.1:8000/uz/admin/
2. Login with your superuser credentials
3. Click "Article Rules" → "Add Article Rules"
4. Fill in the rules content in all 3 languages:
   - **Title (Uzbek)**: Maqola yozish qoidalari
   - **Title (Russian)**: Правила написания статей
   - **Title (English)**: Article Writing Rules
   - **Content**: Add your rules (can be simple text for testing)
5. Check "Active" box
6. Click "Save"

### Step 5: Test the Application

Visit these URLs:

- **Homepage (Uzbek)**: http://127.0.0.1:8000/uz/
- **Homepage (Russian)**: http://127.0.0.1:8000/ru/
- **Homepage (English)**: http://127.0.0.1:8000/en/
- **Admin Panel**: http://127.0.0.1:8000/uz/admin/

### Step 6: Test User Registration

1. Go to http://127.0.0.1:8000/uz/
2. Click "Register" (Ro'yxatdan o'tish)
3. Create an Author account
4. Accept the article rules
5. Create your first article!

## 🌐 Generate Translations (Optional)

To generate and compile translation files:

```bash
# Generate translation files
python manage.py makemessages -l uz -l ru -l en --ignore=venv

# Compile translations
python manage.py compilemessages --ignore=venv
```

**Note**: Translation generation requires `gettext` to be installed on your system.

**Windows**: Download from https://mlocati.github.io/articles/gettext-iconv-windows.html

**Linux**: `sudo apt install gettext`

**Mac**: `brew install gettext`

## 🎨 Collect Static Files (for production)

```bash
python manage.py collectstatic --noinput
```

## ✅ Verify Everything Works

### Test Checklist:

- [ ] Homepage loads in all 3 languages
- [ ] Language switcher works (top-right menu)
- [ ] User registration works (both Reader and Author)
- [ ] Authors can accept rules
- [ ] Authors can create articles
- [ ] Articles display correctly
- [ ] Admin panel is accessible
- [ ] Multilingual article fields work in admin

## 🐛 Common Issues

### "No module named 'decouple'"
```bash
pip install python-decouple
```

### "No module named 'modeltranslation'"
```bash
pip install django-modeltranslation
```

### "ModuleNotFoundError: No module named 'ckeditor'"
```bash
pip install django-ckeditor
```

### Database connection error
Switch to SQLite (see Step 2) or configure PostgreSQL properly.

### Static files not loading
```bash
python manage.py collectstatic --noinput
```

## 📝 Default Login Credentials

After running `createsuperuser`, use those credentials for:
- Admin panel: http://127.0.0.1:8000/uz/admin/

## 🎯 Next Steps

1. **Customize Article Rules**: Add detailed writing guidelines
2. **Create Test Content**: Add sample articles in 3 languages
3. **Invite Users**: Test with different user roles
4. **Configure Production**: See README.md and DEPLOYMENT.md
5. **Add More Features**: Extend functionality as needed

## 📚 Full Documentation

- **README.md**: Complete project documentation
- **DEPLOYMENT.md**: Production deployment guide
- **config/settings.py**: All configuration options

## 🆘 Need Help?

1. Check the logs: Look for error messages in the console
2. Read README.md: Comprehensive documentation
3. Check Django docs: https://docs.djangoproject.com/

---

**Ready to go!** 🚀 Your multilingual article platform is up and running!
