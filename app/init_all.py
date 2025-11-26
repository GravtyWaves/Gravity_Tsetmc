"""
اسکریپت مرکزی برای ساخت جداول دیتابیس، بارگذاری داده‌های اولیه و بروزرسانی همه جداول
"""
from app.db import Base, engine
from app.list_fetcher import (
    fetch_and_store_market_list,
    fetch_and_store_panel_list,
    fetch_and_store_sector_list,
    fetch_and_store_symbol_list,
    fetch_and_store_index_list
)
from app.fetcher import (
    fetch_and_store_symbol_prices,
    fetch_and_store_index_prices,
    fetch_and_store_industry_indices
)
from app.usd_fetcher import fetch_and_store_usd_irr_prices
from gravity_tse import Get_ShareHoldersInfo
import pandas as pd

def init_db():
    print("[INIT] ساخت همه جداول دیتابیس...")
    Base.metadata.create_all(engine)
    print("[INIT] همه جداول ساخته شد.")

def load_initial_data():
    print("[INIT] بارگذاری داده‌های اولیه بازارها...")
    fetch_and_store_market_list()
    print("[INIT] بارگذاری داده‌های اولیه پنل‌ها...")
    fetch_and_store_panel_list()
    print("[INIT] بارگذاری داده‌های اولیه صنایع...")
    fetch_and_store_sector_list()
    print("[INIT] بارگذاری داده‌های اولیه نمادها...")
    fetch_and_store_symbol_list()
    print("[INIT] بارگذاری داده‌های اولیه شاخص‌ها...")
    fetch_and_store_index_list()
    print("[INIT] داده‌های اولیه همه جداول ذخیره شد.")

def update_all():
    print("[UPDATE] بروزرسانی قیمت نمادها...")
    # دریافت لیست نمادها از دیتابیس
    from app.db import SessionLocal, SymbolList
    session = SessionLocal()
    symbols = session.query(SymbolList.symbol_fa, SymbolList.symbol_en).all()
    session.close()
    fetch_and_store_symbol_prices(symbols, adjust=True)
    print("[UPDATE] بروزرسانی قیمت شاخص‌های اصلی...")
    indices = [
        "شاخص کل", "شاخص هم وزن", "شاخص قیمت (وزنی-ارزشی)", "شاخص قیمت (هم وزن)",
        "شاخص شناور آزاد", "شاخص بازار اول", "شاخص بازار دوم", "شاخص صنعت",
        "شاخص 30 شرکت بزرگ", "شاخص 50 شرکت فعالتر"
    ]
    fetch_and_store_index_prices(indices, adjust=True)
    print("[UPDATE] بروزرسانی قیمت شاخص‌های صنایع...")
    # دریافت لیست صنایع از دیتابیس
    from app.db import SessionLocal, Sector
    session = SessionLocal()
    industries = session.query(Sector.sector_name).all()
    session.close()
    industries = [i[0] for i in industries]
    fetch_and_store_industry_indices(industries, adjust=True)
    print("[UPDATE] بروزرسانی قیمت دلار/ریال...")
    fetch_and_store_usd_irr_prices()
    print("[UPDATE] بروزرسانی اطلاعات سهامداران همه نمادها...")
    # دریافت لیست نمادها و بروزرسانی سهامداران
    session = SessionLocal()
    symbols = session.query(SymbolList.symbol_fa).all()
    session.close()
    for s in symbols:
        try:
            Get_ShareHoldersInfo(s[0])
        except Exception as e:
            print(f"[ERROR] سهامداران نماد {s[0]}: {e}")
    print("[UPDATE] بروزرسانی همه جداول کامل شد.")

if __name__ == "__main__":
    init_db()
    load_initial_data()
    update_all()
