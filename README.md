# Gravity_Tsetmc

نسخه 1.0.0

## معرفی

این پروژه یک ابزار جامع برای دریافت، ذخیره و مدیریت داده‌های بازار بورس ایران (TSETMC) است که شامل:
- دریافت لیست نمادها، شاخص‌ها، صنایع، بازارها و پنل‌ها
- دریافت و ذخیره قیمت‌های روزانه نمادها، شاخص‌ها و صنایع
- دریافت و ذخیره قیمت دلار/ریال
- ابزارهای مدیریت دیتابیس و تخصیص سکتور به نمادها
- CLI حرفه‌ای برای استفاده کامل از امکانات پروژه

## نصب و راه‌اندازی

1. کلون پروژه:
```sh
git clone https://github.com/GravtyWaves/Gravity_Tsetmc.git
cd Gravity_Tsetmc
```
2. ساخت محیط مجازی و نصب وابستگی‌ها:
```sh
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

## دستورات CLI

### دریافت و ذخیره کامل داده‌های اولیه
```sh
python cli.py init
```

### به‌روزرسانی داده‌های دیتابیس
```sh
python cli.py update --symbols فملی,خودرو --indices "شاخص کل" --industries "خودرو و ساخت قطعات"
```

### به‌روزرسانی قیمت دلار/ریال
```sh
python cli.py update-usd
```

### بازسازی و بارگذاری مجدد جداول
```sh
python cli.py reset-index-prices
python cli.py reset-symbol-prices
python cli.py reset-usd-irr-prices
python cli.py reset-indices
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