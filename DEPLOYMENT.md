# 🚀 Deployment Guide

Complete guide for deploying the Multilingual Article Publishing Platform to production.

## 📋 Pre-Deployment Checklist

- [ ] PostgreSQL database created and accessible
- [ ] Domain name configured (DNS pointing to your server)
- [ ] SSL certificate ready (Let's Encrypt recommended)
- [ ] Server with Python 3.10+ installed
- [ ] Backup strategy in place

## 🔧 Production Server Setup

### 1. Server Requirements

**Minimum**:
- 1 CPU core
- 1GB RAM
- 10GB storage
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+

**Recommended**:
- 2 CPU cores
- 2GB RAM
- 20GB SSD storage

### 2. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and PostgreSQL
sudo apt install python3.10 python3.10-venv python3-pip postgresql postgresql-contrib nginx -y

# Install additional dependencies
sudo apt install build-essential libpq-dev python3-dev gettext -y
```

### 3. Create Application User

```bash
sudo adduser --system --group --home /opt/article-platform articleapp
sudo su - articleapp
```

### 4. Setup Application

```bash
# Clone or upload your application
cd /opt/article-platform
# (Upload your code here via git, scp, or other method)

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## 🗄️ Database Setup

### PostgreSQL Configuration

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE article_platform_db;
CREATE USER article_user WITH PASSWORD 'STRONG_PASSWORD_HERE';

ALTER ROLE article_user SET client_encoding TO 'utf8';
ALTER ROLE article_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE article_user SET timezone TO 'Asia/Tashkent';

GRANT ALL PRIVILEGES ON DATABASE article_platform_db TO article_user;

# Exit
\q
```

### Configure PostgreSQL Remote Access (if needed)

Edit `/etc/postgresql/14/main/postgresql.conf`:
```conf
listen_addresses = 'localhost'
```

Edit `/etc/postgresql/14/main/pg_hba.conf`:
```conf
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## ⚙️ Application Configuration

### 1. Environment Variables

Create `/opt/article-platform/.env`:

```bash
# Generate secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Edit `.env`:
```env
# Django Settings
SECRET_KEY=your-generated-secret-key-here-min-50-characters
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=article_platform_db
DB_USER=article_user
DB_PASSWORD=STRONG_PASSWORD_HERE
DB_HOST=localhost
DB_PORT=5432
```

### 2. Set Proper Permissions

```bash
# As root/sudo user
sudo chown -R articleapp:articleapp /opt/article-platform
sudo chmod 640 /opt/article-platform/.env
```

### 3. Run Migrations

```bash
# As articleapp user
cd /opt/article-platform
source venv/bin/activate

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py compilemessages --ignore=venv
```

## 🦄 Gunicorn Configuration

### 1. Create Gunicorn Config

Create `/opt/article-platform/gunicorn_config.py`:

```python
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/opt/article-platform/logs/gunicorn_access.log"
errorlog = "/opt/article-platform/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "article_platform"

# Server mechanics
daemon = False
pidfile = "/opt/article-platform/gunicorn.pid"
user = "articleapp"
group = "articleapp"
```

### 2. Create Log Directory

```bash
sudo mkdir -p /opt/article-platform/logs
sudo chown articleapp:articleapp /opt/article-platform/logs
```

### 3. Test Gunicorn

```bash
cd /opt/article-platform
source venv/bin/activate
gunicorn config.wsgi:application -c gunicorn_config.py
```

## 🔄 Systemd Service

### Create Service File

Create `/etc/systemd/system/article-platform.service`:

```ini
[Unit]
Description=Article Publishing Platform Gunicorn Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=articleapp
Group=articleapp
RuntimeDirectory=gunicorn
WorkingDirectory=/opt/article-platform
Environment="PATH=/opt/article-platform/venv/bin"
EnvironmentFile=/opt/article-platform/.env

ExecStart=/opt/article-platform/venv/bin/gunicorn \
    --config /opt/article-platform/gunicorn_config.py \
    config.wsgi:application

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable article-platform

# Start service
sudo systemctl start article-platform

# Check status
sudo systemctl status article-platform

# View logs
sudo journalctl -u article-platform -f
```

## 🌐 Nginx Configuration

### 1. Create Nginx Config

Create `/etc/nginx/sites-available/article-platform`:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=article_limit:10m rate=10r/s;

# Upstream
upstream article_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration (adjust paths for your SSL cert)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logging
    access_log /var/log/nginx/article_platform_access.log;
    error_log /var/log/nginx/article_platform_error.log;

    # Max upload size
    client_max_body_size 5M;

    # Static files
    location /static/ {
        alias /opt/article-platform/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/article-platform/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Favicon
    location = /favicon.ico {
        alias /opt/article-platform/staticfiles/favicon.ico;
        access_log off;
        log_not_found off;
    }

    # Robots.txt
    location = /robots.txt {
        alias /opt/article-platform/staticfiles/robots.txt;
        access_log off;
        log_not_found off;
    }

    # Application
    location / {
        limit_req zone=article_limit burst=20 nodelay;

        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        proxy_pass http://article_app;
    }
}
```

### 2. Enable Site

```bash
# Test configuration
sudo nginx -t

# Create symlink
sudo ln -s /etc/nginx/sites-available/article-platform /etc/nginx/sites-enabled/

# Reload Nginx
sudo systemctl reload nginx

# Enable Nginx on boot
sudo systemctl enable nginx
```

## 🔒 SSL Certificate (Let's Encrypt)

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Obtain Certificate

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Auto-Renewal

Certbot automatically creates a renewal timer. Check it:

```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

## 🔥 Firewall Configuration

```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## 📊 Monitoring and Logs

### View Application Logs

```bash
# Gunicorn logs
sudo tail -f /opt/article-platform/logs/gunicorn_error.log

# Systemd logs
sudo journalctl -u article-platform -f

# Nginx logs
sudo tail -f /var/log/nginx/article_platform_error.log
```

### Log Rotation

Create `/etc/logrotate.d/article-platform`:

```
/opt/article-platform/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        systemctl reload article-platform > /dev/null 2>&1 || true
    endscript
}
```

## 🔄 Backup Strategy

### Database Backup Script

Create `/opt/article-platform/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/article-platform/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="article_platform_db"
DB_USER="article_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
PGPASSWORD="your_db_password" pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/article-platform/media/

# Remove backups older than 30 days
find $BACKUP_DIR -type f -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Make executable and add to crontab:

```bash
chmod +x /opt/article-platform/backup.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /opt/article-platform/backup.sh >> /var/log/article-backup.log 2>&1
```

## 🔄 Deployment Updates

### Update Application

```bash
# Pull latest code
cd /opt/article-platform
git pull origin main

# Activate venv
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Compile translations
python manage.py compilemessages --ignore=venv

# Restart service
sudo systemctl restart article-platform

# Check status
sudo systemctl status article-platform
```

## 🧪 Testing Production Setup

```bash
# Test database connection
python manage.py dbshell

# Check for errors
python manage.py check --deploy

# Test static files
curl https://your-domain.com/static/
```

## 🚨 Troubleshooting

### Service Won't Start

```bash
sudo journalctl -u article-platform -n 50 --no-pager
```

### 502 Bad Gateway

Check if Gunicorn is running:
```bash
sudo systemctl status article-platform
sudo netstat -tulpn | grep 8000
```

### Static Files Not Loading

```bash
python manage.py collectstatic --clear --noinput
sudo systemctl restart article-platform
```

### Database Connection Error

Check PostgreSQL:
```bash
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT 1"
```

## 📈 Performance Optimization

### Enable Caching

Add to settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_article_status ON articles_article(status);
CREATE INDEX idx_article_author ON articles_article(author_id);
CREATE INDEX idx_article_created ON articles_article(created_at DESC);
```

## ✅ Post-Deployment Checklist

- [ ] Application accessible via HTTPS
- [ ] Language switcher working
- [ ] User registration working
- [ ] Article creation/editing working
- [ ] Admin panel accessible
- [ ] Static files loading correctly
- [ ] Media uploads working
- [ ] Error pages displaying correctly
- [ ] Backups configured and tested
- [ ] Monitoring in place
- [ ] SSL certificate auto-renewal configured
- [ ] Firewall rules active

## 🎉 Deployment Complete!

Your multilingual article publishing platform is now live!

Access your site at: **https://your-domain.com**

---

**Need help?** Check logs, review configuration, or refer to the main README.md.
