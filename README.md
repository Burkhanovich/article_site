# 📚 Multilingual Article Publishing Platform

A production-ready Django web application for publishing articles with full support for **Uzbek 🇺🇿**, **Russian 🇷🇺**, and **English 🇬🇧** languages.

## ✨ Features

### 🌍 Multi-Language Support
- **3 Languages**: Uzbek (default), Russian, English
- **Django i18n/l10n**: Full internationalization and localization
- **Language Switcher**: Visible in header, seamless language switching
- **URL Prefixes**: `/uz/`, `/ru/`, `/en/`
- **Multilingual Content**: Articles and rules in all 3 languages

### 👥 User Roles & Authentication
- **Two Roles**:
  - **Reader (O'quvchi)**: Browse and read articles
  - **Author (Avtor)**: Create, edit, delete own articles
- **Secure Registration**: Email + password with validation
- **Article Rules**: Authors must accept writing rules before publishing
- **Role-Based Access Control**: Proper permissions using Django CBVs

### 📝 Article Management
- **Rich Text Editor**: CKEditor with image upload support
- **Multilingual Articles**: Title and content in 3 languages
- **Draft/Published Status**: Control article visibility
- **SEO-Friendly Slugs**: Auto-generated from titles
- **View Counter**: Track article popularity
- **Cover Images**: Upload and display article covers
- **Search & Pagination**: Find articles easily

### 🔒 Security
- **CSRF Protection**: Enabled on all forms
- **XSS Prevention**: Secure content handling
- **Password Validation**: Strong password requirements (min 8 chars)
- **File Upload Security**: Validated image uploads (max 5MB)
- **Production-Ready**: SSL, secure cookies, HSTS headers

### 🎨 Frontend
- **Responsive Design**: Bootstrap 5
- **Modern UI**: Clean, professional interface
- **Custom Error Pages**: 403, 404, 500 with translations
- **Messages Framework**: User feedback for all actions

### ⚙️ Admin Panel
- **Multilingual Admin**: Tabbed interface for translated fields
- **User Management**: Bulk actions, role changes
- **Article Management**: Filters, search, inline editing
- **Rules Management**: Edit article writing rules per language

## 🛠️ Tech Stack

- **Backend**: Django 5.0+
- **Database**: PostgreSQL (SQLite for dev)
- **i18n**: django-modeltranslation
- **Editor**: CKEditor with image uploads
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Server**: Gunicorn (production)

## 📋 Requirements

- Python 3.10+
- PostgreSQL 14+ (or SQLite for development)
- pip (Python package manager)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd site
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update settings:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# For development with SQLite, use default settings
# For PostgreSQL, update:
DB_NAME=article_platform_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

**For SQLite Development**: Uncomment SQLite configuration in `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 5. Create Database (PostgreSQL only)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE article_platform_db;
CREATE USER article_user WITH PASSWORD 'your_password';
ALTER ROLE article_user SET client_encoding TO 'utf8';
ALTER ROLE article_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE article_user SET timezone TO 'Asia/Tashkent';
GRANT ALL PRIVILEGES ON DATABASE article_platform_db TO article_user;
\q
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

Enter username, email, and password.

### 8. Generate Translation Files

```bash
# Create message files for all languages
python manage.py makemessages -l uz -l ru -l en --ignore=venv

# Compile translations
python manage.py compilemessages --ignore=venv
```

### 9. Collect Static Files (for production)

```bash
python manage.py collectstatic --noinput
```

### 10. Create Article Rules

1. Start the development server:
```bash
python manage.py runserver
```

2. Go to admin panel: `http://127.0.0.1:8000/uz/admin/`
3. Login with superuser credentials
4. Navigate to **Article Rules**
5. Create a new rule set with content in all 3 languages
6. Mark it as **Active**

### 11. Run Development Server

```bash
python manage.py runserver
```

Access the application:
- **Homepage**: http://127.0.0.1:8000/uz/
- **Admin Panel**: http://127.0.0.1:8000/uz/admin/
- **Russian**: http://127.0.0.1:8000/ru/
- **English**: http://127.0.0.1:8000/en/

## 📖 Usage Guide

### For Authors

1. **Register** as an Author
2. **Accept Article Writing Rules** (required)
3. **Create Articles** with content in 3 languages
4. **Publish** or save as draft
5. **Edit/Delete** your own articles
6. **Track Views** on your articles

### For Readers

1. **Register** as a Reader
2. **Browse Articles** by language
3. **Search** for specific content
4. **View** article details

### For Administrators

1. **Manage Users**: Change roles, reset rule acceptance
2. **Manage Articles**: Publish, unpublish, edit any article
3. **Configure Rules**: Update article writing rules
4. **View Statistics**: Track platform usage

## 🌐 Multi-Language Content

### Creating Multilingual Articles

In the admin panel or article form, you'll see tabs for each language:
- **O'zbekcha** (Uzbek) - Required
- **Русский** (Russian) - Optional
- **English** - Optional

Fill in the title and content for each language. If a translation is missing, the default (Uzbek) will be displayed.

### Translating UI Elements

UI translations are stored in `locale/` directory:
```
locale/
├── uz/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
├── ru/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
└── en/
    └── LC_MESSAGES/
        ├── django.po
        └── django.mo
```

To update translations:
```bash
# Extract new strings
python manage.py makemessages -l uz -l ru -l en --ignore=venv

# Edit .po files in locale/ directories
# Then compile:
python manage.py compilemessages --ignore=venv
```

## 🚢 Production Deployment

### Environment Configuration

1. Generate a secure SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. Update `.env`:
```env
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

3. Configure PostgreSQL with strong credentials

### Using Gunicorn

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with 4 workers
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /path/to/site/staticfiles/;
    }

    location /media/ {
        alias /path/to/site/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service (Linux)

Create `/etc/systemd/system/article-platform.service`:

```ini
[Unit]
Description=Article Publishing Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/site
Environment="PATH=/path/to/site/venv/bin"
ExecStart=/path/to/site/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable article-platform
sudo systemctl start article-platform
sudo systemctl status article-platform
```

## 🔧 Maintenance

### Backup Database

```bash
# PostgreSQL
pg_dump -U postgres article_platform_db > backup.sql

# SQLite
cp db.sqlite3 db.sqlite3.backup
```

### Update Translations

```bash
python manage.py makemessages -l uz -l ru -l en --ignore=venv
# Edit .po files
python manage.py compilemessages --ignore=venv
```

### Clear Cache

```bash
python manage.py clearsessions
```

## 📁 Project Structure

```
site/
├── config/                 # Django project settings
│   ├── settings.py        # Main settings with i18n
│   ├── urls.py            # URL routing with i18n_patterns
│   ├── wsgi.py
│   └── asgi.py
├── users/                 # User authentication app
│   ├── models.py          # CustomUser, ArticleRules
│   ├── views.py           # Registration, login, rules
│   ├── forms.py           # User forms
│   ├── admin.py           # User admin
│   ├── translation.py     # Multilingual config
│   └── urls.py
├── articles/              # Article management app
│   ├── models.py          # Article model
│   ├── views.py           # CRUD views
│   ├── forms.py           # Article forms
│   ├── admin.py           # Article admin
│   ├── translation.py     # Multilingual config
│   └── urls.py
├── core/                  # Core app (homepage, errors)
│   ├── views.py           # Home, dashboard, error pages
│   └── urls.py
├── templates/             # HTML templates
│   ├── base.html          # Base with language switcher
│   ├── users/             # Auth templates
│   ├── articles/          # Article templates
│   ├── core/              # Home/dashboard
│   └── errors/            # 403, 404, 500
├── locale/                # Translation files
│   ├── uz/                # Uzbek translations
│   ├── ru/                # Russian translations
│   └── en/                # English translations
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploads (article covers)
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .env.example           # Example environment config
└── README.md              # This file
```

## 🐛 Troubleshooting

### "No module named 'decouple'"
```bash
pip install python-decouple
```

### "No module named 'modeltranslation'"
```bash
pip install django-modeltranslation
```

### Migration Errors
```bash
# Delete migrations (be careful!)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# Recreate
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Language Switcher Not Working
Make sure `LocaleMiddleware` is in `MIDDLEWARE` in settings.py

## 📄 License

This project is open-source and available for educational and commercial use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 👨‍💻 Author

Built with ❤️ using Django, Bootstrap, and django-modeltranslation.

---

## 🌟 Key Features Summary

✅ **Multi-language Support** (Uzbek, Russian, English)
✅ **Role-Based Access Control** (Reader, Author)
✅ **Article Rules System** with acceptance tracking
✅ **Rich Text Editor** (CKEditor)
✅ **Multilingual Content** (Articles, Rules)
✅ **Language Switcher** in header
✅ **SEO-Friendly** URLs and slugs
✅ **Responsive Design** (Bootstrap 5)
✅ **Security Best Practices** (CSRF, XSS, secure uploads)
✅ **Custom Error Pages** (403, 404, 500)
✅ **Admin Panel** with multilingual support
✅ **View Counter** for articles
✅ **Search & Pagination**
✅ **Production-Ready** (Gunicorn, PostgreSQL)

**Ready to deploy!** 🚀
