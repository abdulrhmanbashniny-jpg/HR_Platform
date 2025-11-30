# 🚀 دليل النشر - Deployment Guide

دليل شامل لنشر منصة إدارة الموارد البشرية على منصات مختلفة.

---

## 📑 المحتويات

1. [Streamlit Cloud](#streamlit-cloud)
2. [Heroku](#heroku)
3. [AWS EC2](#aws-ec2)
4. [Docker](#docker)
5. [VPS](#vps)

---

## ☁️ Streamlit Cloud

الطريقة الأسهل والأسرع! مجانية تماماً.

### الخطوات:

#### 1. جهّز المشروع على GitHub

```bash
# تأكد من رفع كل الملفات
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. اذهب إلى Streamlit Cloud

1. افتح: https://streamlit.io/cloud
2. سجّل دخول بحساب GitHub
3. اضغط **"New app"**

#### 3. اربط المشروع

- Repository: `username/HR_Platform`
- Branch: `main`
- Main file: `app.py`

#### 4. أضف الأسرار (Secrets)

في **Advanced settings → Secrets**:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-key-here"
```

#### 5. انشر!

اضغط **Deploy** وانتظر 2-3 دقائق

✅ تطبيقك الآن متاح على: `https://yourapp.streamlit.app`

### ⚙️ الإعدادات

إنشاء ملف `.streamlit/secrets.toml`:

```toml
[supabase]
url = "https://xxxxx.supabase.co"
key = "your-key-here"
```

تحديث `config.py`:

```python
import streamlit as st

if "supabase" in st.secrets:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
```

---

## 🟣 Heroku

### المتطلبات:

```bash
pip install gunicorn
```

### الخطوات:

#### 1. إنشاء ملفات Heroku

**Procfile:**
```
web: sh setup.sh && streamlit run app.py
```

**setup.sh:**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

#### 2. النشر

```bash
# تسجيل دخول
heroku login

# إنشاء تطبيق
heroku create hr-platform-app

# إضافة المتغيرات
heroku config:set SUPABASE_URL="https://xxxxx.supabase.co"
heroku config:set SUPABASE_KEY="your-key-here"

# النشر
git push heroku main
```

✅ تطبيقك على: `https://hr-platform-app.herokuapp.com`

---

## 🟧 AWS EC2

### 1. إنشاء Instance

1. افتح AWS Console
2. EC2 → Launch Instance
3. اختر Ubuntu 22.04
4. نوع: t2.micro (مجاني)
5. Security Group: افتح منفذ 8501

### 2. الاتصال بالـ Server

```bash
ssh -i "your-key.pem" ubuntu@your-ec2-ip
```

### 3. التثبيت

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python
sudo apt install python3-pip python3-venv -y

# استنساخ المشروع
git clone https://github.com/username/HR_Platform.git
cd HR_Platform

# إنشاء البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المكتبات
pip install -r requirements.txt
```

### 4. تكوين الخدمة

إنشاء `/etc/systemd/system/hr-platform.service`:

```ini
[Unit]
Description=HR Platform
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/HR_Platform
Environment="PATH=/home/ubuntu/HR_Platform/venv/bin"
ExecStart=/home/ubuntu/HR_Platform/venv/bin/streamlit run app.py

[Install]
WantedBy=multi-user.target
```

### 5. تشغيل الخدمة

```bash
sudo systemctl daemon-reload
sudo systemctl start hr-platform
sudo systemctl enable hr-platform
sudo systemctl status hr-platform
```

### 6. Nginx كـ Reverse Proxy

```bash
sudo apt install nginx -y
```

إنشاء `/etc/nginx/sites-available/hr-platform`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/hr-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

✅ تطبيقك على: `http://your-ec2-ip` أو `http://your-domain.com`

---

## 🐳 Docker

### 1. إنشاء Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

### 2. إنشاء docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### 3. إنشاء .env

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-key-here
```

### 4. البناء والتشغيل

```bash
# بناء الصورة
docker-compose build

# تشغيل الحاوية
docker-compose up -d

# عرض السجلات
docker-compose logs -f

# إيقاف
docker-compose down
```

✅ تطبيقك على: `http://localhost:8501`

---

## 🖥️ VPS (DigitalOcean / Linode)

مشابه لـ AWS EC2:

### 1. إنشاء Droplet

- اختر Ubuntu 22.04
- حجم: 1GB RAM (5$ شهرياً)
- افتح منفذ 8501

### 2. اتبع نفس خطوات AWS EC2

---

## 🔐 الأمان

### 1. استخدم HTTPS

```bash
# تثبيت Certbot
sudo apt install certbot python3-certbot-nginx -y

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com
```

### 2. Firewall

```bash
# UFW
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw enable
```

### 3. البيئة

لا تحفظ المفاتيح في الكود! استخدم:

```python
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

---

## 📊 المراقبة

### 1. سجلات النظام

```bash
# Streamlit Cloud
# اذهب إلى: Manage app → Logs

# AWS/VPS
sudo journalctl -u hr-platform -f
```

### 2. مراقبة الأداء

```bash
# استخدام htop
sudo apt install htop
htop
```

### 3. التنبيهات

استخدم خدمات مثل:
- UptimeRobot (مجاني)
- StatusCake
- Pingdom

---

## 🔄 التحديثات

### Streamlit Cloud

```bash
git add .
git commit -m "Update"
git push origin main
# التحديث تلقائي!
```

### AWS/VPS

```bash
cd HR_Platform
git pull
sudo systemctl restart hr-platform
```

### Docker

```bash
docker-compose down
git pull
docker-compose build
docker-compose up -d
```

---

## 💾 النسخ الاحتياطية

### 1. قاعدة البيانات

```bash
# يدوي
python scripts/backup.py create

# تلقائي (cron)
crontab -e
```

أضف:
```
0 2 * * * cd /home/ubuntu/HR_Platform && /home/ubuntu/HR_Platform/venv/bin/python scripts/backup.py create
```

### 2. الملفات

```bash
# rsync
rsync -avz /home/ubuntu/HR_Platform/ /backup/
```

---

## 🧪 اختبار ما قبل النشر

```bash
# اختبار الاتصال
python scripts/test_connection.py

# اختبار التطبيق محلياً
streamlit run app.py

# التحقق من requirements.txt
pip install -r requirements.txt --dry-run
```

---

## ❓ استكشاف الأخطاء

### مشكلة: التطبيق لا يعمل

```bash
# تحقق من السجلات
docker-compose logs
sudo journalctl -u hr-platform -n 50
```

### مشكلة: Port مستخدم

```bash
# Linux/Mac
sudo lsof -i :8501
kill -9 PID

# أو غيّر المنفذ
streamlit run app.py --server.port 8502
```

### مشكلة: خطأ في قاعدة البيانات

```bash
# اختبار الاتصال
python scripts/test_connection.py

# تحقق من المتغيرات
echo $SUPABASE_URL
```

---

## 📚 موارد إضافية

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Heroku Docs](https://devcenter.heroku.com/)
- [AWS EC2 Guide](https://docs.aws.amazon.com/ec2/)
- [Docker Docs](https://docs.docker.com/)

---

## 🎉 نصائح للنجاح

1. ✅ ابدأ بـ Streamlit Cloud (أسهل طريقة)
2. ✅ استخدم HTTPS دائماً
3. ✅ احفظ المفاتيح بأمان
4. ✅ راقب الأداء باستمرار
5. ✅ اعمل نسخ احتياطية دورية

---

**بالتوفيق في النشر! 🚀**
