# Gravity TSETMC - پروژه حرفه‌ای مدیریت داده‌های بورس

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📌 معرفی

**Gravity TSETMC** یک پروژه حرفه‌ای و دقیق برای دریافت، ذخیره‌سازی و مدیریت داده‌های بازار بورس تهران (TSETMC) است که با بالاترین معیارهای صنعتی طراحی شده است.

### ✨ ویژگی‌های اصلی

- ✅ **دیتابیس حرفه‌ای** - SQLAlchemy ORM با طراحی optimized
- ✅ **داده‌های جامع** - نمادها، شاخص‌ها، صنایع، بازارها، پنل‌ها
- ✅ **قیمت‌های روزانه** - نمادها، شاخص‌ها، و ارزش دلار/ریال
- ✅ **داده‌های RI** - اطلاعات خریدار/فروشنده حقیقی و حقوقی
- ✅ **اطلاعات سهامداران** - سهامداران عمده و تغییرات
- ✅ **API و CLI** - رابط command-line جامع و API programmatic
- ✅ **به‌روزرسانی خودکار** - سیستم scheduler برای به‌روزرسانی داده‌ها

## 🗄️ ساختار دیتابیس

### جداول اصلی:

| جدول | توضیح |
|------|-------|
| `markets` | بازارهای مختلف (بورس، فرابورس، پایه‌های مختلف) |
| `sectors` | صنایع و بخش‌های اقتصادی |
| `panels` | پنل‌های مختلف |
| `symbol_list` | لیست نمادها با اطلاعات |
| `symbol_prices` | قیمت‌های روزانه نمادها |
| `indices` | شاخص‌های مختلف |
| `index_prices` | قیمت‌های روزانه شاخص‌ها |
| `ri_data` | داده‌های سهامداران حقیقی/حقوقی |
| `usd_irr_prices` | قیمت دلار/ریال |
| `shareholders_info` | اطلاعات سهامداران عمده |

## 🚀 نصب و راه‌اندازی

### الزامات سیستم
- Python 3.8+
- pip (مدیر بسته Python)

### مراحل نصب

1. **کلون کردن پروژه:**
```bash
git clone https://github.com/GravtyWaves/Gravity_Tsetmc.git
cd Gravity_Tsetmc
```

2. **ایجاد محیط مجازی:**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **نصب وابستگی‌ها:**
```bash
pip install -r requirements.txt
```

4. **تهیه دیتابیس:**
```bash
python cli.py init-all
```

## 📋 دستورات CLI

### ۱. دریافت و ذخیره داده‌های اولیه

```bash
# دریافت تمام داده‌های اولیه (نمادها، شاخص‌ها، صنایع)
python cli.py init-all

# دریافت فقط نمادها
python cli.py init --symbols

# دریافت فقط شاخص‌ها
python cli.py init --indices
```

### ۲. به‌روزرسانی داده‌ها

```bash
# به‌روزرسانی قیمت نمادهای خاص
python cli.py update --symbols فملی خودرو

# به‌روزرسانی قیمت شاخص‌های خاص
python cli.py update --indices "شاخص کل" "شاخص صنایع پایه"

# به‌روزرسانی قیمت دلار/ریال
python cli.py update --usd

# به‌روزرسانی داده‌های RI
python cli.py update --ri

# به‌روزرسانی همه چیز
python cli.py update --all
```

### ۳. مدیریت دیتابیس

```bash
# ری‌ست کردن جدول قیمت نمادها
python cli.py reset --symbol-prices

# ری‌ست کردن جدول قیمت شاخص‌ها
python cli.py reset --index-prices

# ری‌ست کردن همه جداول
python cli.py reset --all
```

### ۴. لیست و جستجو

```bash
# نمایش تمام نمادها
python cli.py list --symbols

# جستجوی نماد خاص
python cli.py search --symbol خودرو

# نمایش تمام شاخص‌ها
python cli.py list --indices

# نمایش تمام صنایع
python cli.py list --sectors
```

## 🔧 استفاده از API

### مثال برای دریافت قیمت نماد:

```python
from app.db import get_session, SymbolPrice
from datetime import datetime, timedelta

session = get_session()

# دریافت قیمت نماد در ۳۰ روز اخیر
symbol = 'خودرو'
thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

prices = session.query(SymbolPrice).filter(
    SymbolPrice.symbol == symbol,
    SymbolPrice.gregorian_date >= thirty_days_ago
).all()

for price in prices:
    print(f"{price.date}: Close={price.close}, Volume={price.volume}")

session.close()
```

### مثال برای دریافت معلومات نماد:

```python
from app.db import get_session, SymbolList

session = get_session()

# دریافت اطلاعات نماد
symbol = session.query(SymbolList).filter(
    SymbolList.symbol_en == 'KHRO'
).first()

if symbol:
    print(f"نام: {symbol.name}")
    print(f"بازار: {symbol.market.market_name}")
    print(f"صنعت: {symbol.sector.sector_name}")
    print(f"وضعیت: {'فعال' if symbol.is_active else 'غیرفعال'}")

session.close()
```

## 📊 ساختار پروژه

```
Gravity_Tsetmc/
├── app/
│   ├── db.py                    # مدل‌های دیتابیس
│   ├── fetcher.py               # دریافت‌کننده داده
│   ├── main.py                  # لجستیک اصلی
│   └── ...
├── gravity_tse/
│   ├── __init__.py             # توابع کمکی TSETMC
│   └── ...
├── scripts/
│   └── ...                      # اسکریپت‌های کمکی
├── cli.py                       # رابط command-line
├── test.py                      # تست‌ها
├── requirements.txt             # وابستگی‌ها
└── README.md                    # این فایل
```

## 🔐 نکات امنیتی

- ✅ استفاده از environment variables برای configuration
- ✅ حفاظت از داده‌های حساس
- ✅ SQL Injection protection via ORM
- ✅ Rate limiting برای درخواست‌های API

## 🛠️ توسعه و مشارکت

برای کمک به پروژه:

1. Fork کنید
2. branch جدید بسازید (`git checkout -b feature/ازخصوصیت‌تان`)
3. تغییرات را commit کنید (`git commit -m 'Add feature'`)
4. Push کنید (`git push origin feature/ازخصوصیت‌تان`)
5. Pull Request بسازید

## 📞 تماس و پشتیبانی

- **GitHub Issues**: برای گزارش مشکلات و پیشنهادات
- **Email**: [تماس‌گیری از طریق GitHub]

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای جزئیات بیشتر `LICENSE` را ببینید.

---

**ساخته شده با ❤️ برای جامعه بورس و سرمایه‌گذاری ایران**
python cli.py reset-tables-and-reload
```

### ابزارهای بررسی و گزارش
```sh
python cli.py list-indices
python cli.py list-sectors
python cli.py check-symbols-sector
python cli.py print-symbols-without-sector
```

### ابزارهای تخصیص و اصلاح سکتور نمادها
```sh
python cli.py update-symbol-sectors
python cli.py infer-and-assign-sector
python cli.py filter-symbol-to-sector
```

## تست
برای تست سریع:
```sh
python cli.py fetch-index-prices
python cli.py fix-index-prices
```

## لایسنس
MIT

---
برای اطلاعات بیشتر به مستندات هر ماژول مراجعه کنید.