
import logging
import sys
from gravity_tse import get_price_history, Get_CWI_History, Get_EWI_History
import gravity_tse

# تنظیم logging برای نمایش همه لاگ‌ها در کنسول uvicorn
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def _get_sector_webid_map():
    if hasattr(gravity_tse, 'get_sector_webid_map'):
        return gravity_tse.get_sector_webid_map()
    elif hasattr(gravity_tse, 'SECTOR_WEBID_MAP'):
        return getattr(gravity_tse, 'SECTOR_WEBID_MAP')
    else:
        raise ImportError('Neither get_sector_webid_map nor SECTOR_WEBID_MAP found in finpy_tse')
from .db import SessionLocal, SymbolPrice, IndexPrice, Index
from datetime import datetime
import jdatetime
import pandas as pd
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def fetch_and_store_symbol_prices(symbols, adjust=False):
    session = SessionLocal()
    total_symbols = len(symbols)
    print(f"[SymbolPrice] Starting to fetch prices for {total_symbols} symbols...", flush=True)
    for i, (symbol_fa, symbol_en) in enumerate(symbols, 1):
        # Resume logic: skip symbol if it already has price data
        exists = session.query(SymbolPrice).filter_by(symbol=symbol_en).first()
        if exists:
            print(f"[SymbolPrice] Skipping {symbol_fa} ({symbol_en}) - already in DB.", flush=True)
            continue
        print(f"[SymbolPrice] Fetching data for symbol {i}/{total_symbols}: {symbol_fa} ({symbol_en})", flush=True)
        df = get_price_history(symbol_fa, adjust_price=adjust, ignore_date=True)
        if not (isinstance(df, pd.DataFrame) and not df.empty):
            print(f"[SymbolPrice] No data for symbol: {symbol_fa}", flush=True)
            continue
        count = 0
        for idx, row in df.iterrows():
            # idx is the Jalali date (J-Date) as index
            date_val = str(idx)
            if not date_val or pd.isnull(date_val):
                print(f"[SymbolPrice] Skipping row with missing J-Date for symbol '{symbol_fa}': {row}", flush=True)
                continue
            # Normalize keys for robust access
            row_lc = {str(k).lower().replace(' ', ''): v for k, v in row.items()}
            price = SymbolPrice(
                symbol=symbol_en,
                date=date_val,
                open=row_lc.get('open'),
                high=row_lc.get('high'),
                low=row_lc.get('low'),
                close=row_lc.get('close'),
                final=row_lc.get('final'),
                volume=row_lc.get('volume'),
                value=row_lc.get('value'),
                no=row_lc.get('no'),
                name=row_lc.get('name'),
                market=row_lc.get('market'),
                adj_open=row_lc.get('adjopen'),
                adj_high=row_lc.get('adjhigh'),
                adj_low=row_lc.get('adjlow'),
                adj_close=row_lc.get('adjclose'),
                adj_final=row_lc.get('adjfinal')
            )
            session.merge(price)
            count += 1
        print(f"[SymbolPrice] Stored {count} price records for {symbol_fa}", flush=True)
    session.commit()
    session.close()
    print("[SymbolPrice] All symbol prices stored.", flush=True)

def fetch_and_store_index_prices(indices, adjust=False):
    session = SessionLocal()
    total_indices = len(indices)
    print(f"[IndexPrice] Starting to fetch prices for {total_indices} indices...", flush=True)
    from .db import Index
    import gravity_tse
    # WebID mapping for main indices
    MAIN_INDEX_WEBIDS = {
        'شاخص کل': '32097828799138957',
        'شاخص هم وزن': '67130298613737946',
        'شاخص قیمت (وزنی-ارزشی)': '5798407779416661',
        'شاخص قیمت (هم وزن)': '8384385859414435',
        'شاخص شناور آزاد': '49579049405614711',
        'شاخص بازار اول': '62752761908615603',
        'شاخص بازار دوم': '71704845530629737',
        'شاخص صنعت': '43754960038275285',
        'شاخص 30 شرکت بزرگ': '10523825119011581',
        'شاخص 50 شرکت فعالتر': '46342955726788357',
    }
    for i, index_name in enumerate(indices, 1):
        print(f"[IndexPrice] Fetching data for index {i}/{total_indices}: {index_name}", flush=True)
        idx_obj = session.query(Index).filter_by(name=index_name).first()
        if not idx_obj:
            idx_obj = Index(name=index_name, type='market')
            session.add(idx_obj)
            session.commit()
        # اگر شاخص جزو شاخص‌های اصلی است، با WebID و get_index_price_by_webid واکشی شود
        try:
            if index_name in MAIN_INDEX_WEBIDS:
                webid = MAIN_INDEX_WEBIDS[index_name]
                df = gravity_tse.get_index_price_by_webid(webid, just_adj_close=False)
            else:
                df = gravity_tse.get_index_price_safely(index_name, ignore_date=True, adjust_price=adjust, just_adj_close=False)
        except Exception as e:
            print(f"[IndexPrice] Error fetching data for index '{index_name}': {e}", flush=True)
            continue
        if not (isinstance(df, pd.DataFrame) and not df.empty):
            print(f"[IndexPrice] No data for index: {index_name}", flush=True)
            continue
        count = 0
        for idx, row in df.iterrows():
            # پشتیبانی از نام ستون‌های مختلف (Adj Close یا adjclose یا value)
            row_lc = {str(k).lower().replace(' ', ''): v for k, v in row.items()}
            date_val = str(idx)
            if not date_val or pd.isnull(date_val):
                print(f"[IndexPrice] Skipping row with missing J-Date for index '{index_name}': {row_lc}", flush=True)
                continue
            # تعیین مقدار value با اولویت: adjclose > adj close > value > close
            value = row_lc.get('adjclose') or row_lc.get('adj close') or row_lc.get('value') or row_lc.get('close')
            # Use open/high/low/close if present, else fallback to adj open/high/low/close
            open_val = row_lc.get('open') or row_lc.get('adjopen') or row_lc.get('adj open')
            high_val = row_lc.get('high') or row_lc.get('adjhigh') or row_lc.get('adj high')
            low_val = row_lc.get('low') or row_lc.get('adjlow') or row_lc.get('adj low')
            close_val = row_lc.get('close') or row_lc.get('adjclose') or row_lc.get('adj close')
            price = IndexPrice(
                index_id=idx_obj.id,
                date=date_val,
                value=value,
                open=open_val,
                high=high_val,
                low=low_val,
                close=close_val
            )
            session.merge(price)
            count += 1
        print(f"[IndexPrice] Stored {count} price records for {index_name}", flush=True)
    session.commit()
    session.close()
    print("[IndexPrice] All index prices stored.", flush=True)

def fetch_and_store_industry_indices(industries, adjust=False):
    import pandas as pd
    session = SessionLocal()
    total_industries = len(industries)
    print(f"[IndustryIndex] Starting to fetch indices for {total_industries} industries...", flush=True)
    from .db import Index, IndexPrice
    from gravity_tse import fetch_index_history
    for i, industry in enumerate(industries, 1):
        print(f"[IndustryIndex] Fetching data for industry {i}/{total_industries}: {industry}", flush=True)
        idx_obj = session.query(Index).filter_by(name=industry, type='sector').first()
        if not idx_obj or not idx_obj.web_id:
            print(f"[IndustryIndex] No index row or web_id for industry: {industry}", flush=True)
            continue
        df = fetch_index_history(idx_obj.web_id, ignore_date=True, just_adj_close=False, sector_name=industry)
        if not isinstance(df, pd.DataFrame) or df.empty:
            print(f"[IndustryIndex] No data for industry: {industry}", flush=True)
            continue
        count = 0
        for idx, row in df.iterrows():
            date_val = str(idx)
            if not date_val or pd.isnull(date_val):
                print(f"[IndustryIndex] Skipping row with missing J-Date for industry '{industry}': {row}", flush=True)
                continue
            # Prevent duplicates: check if already exists
            exists = session.query(IndexPrice).filter_by(index_id=idx_obj.id, date=date_val).first()
            if exists:
                continue
            # Use Open/High/Low/Close if present, else fallback to Adj Open/High/Low/Close
            open_val = row.get('Open') or row.get('Adj Open')
            high_val = row.get('High') or row.get('Adj High')
            low_val = row.get('Low') or row.get('Adj Low')
            close_val = row.get('Close') or row.get('Adj Close')
            price = IndexPrice(
                index_id=idx_obj.id,
                date=date_val,
                value=row['Adj Close'] if adjust else row['Close'],
                open=open_val,
                high=high_val,
                low=low_val,
                close=close_val
            )
            session.add(price)
            count += 1
        session.commit()
        print(f"[IndustryIndex] Stored {count} index records for {industry}", flush=True)
    session.close()
    print("[IndustryIndex] All industry indices stored.", flush=True)
