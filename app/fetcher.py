import logging
import sys
import pandas as pd
from datetime import datetime
import jdatetime

from gravity_tse import PriceHistoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

from .db import SessionLocal, SymbolPrice, IndexPrice, Index, SymbolList




def fetch_and_store_symbol_prices(symbols=None, adjust=False):
    """Fetch and store symbol prices. If symbols is empty, fetch all."""
    session = SessionLocal()
    
    # اگر symbols خالی است، همه نمادها را از دیتابیس بگیر
    if not symbols:
        symbol_records = session.query(SymbolList).all()
        symbols = [(s.symbol_fa, s.symbol_en) for s in symbol_records]
    
    total_symbols = len(symbols) if isinstance(symbols, list) else len(list(symbols))
    print(f"[SymbolPrice] Fetching prices for {total_symbols} symbols...", flush=True)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, symbol_pair in enumerate(symbols, 1):
        # Handle both tuple pairs and symbol objects
        if isinstance(symbol_pair, tuple):
            symbol_fa, symbol_en = symbol_pair
        else:
            symbol_fa = symbol_pair.symbol_fa
            symbol_en = symbol_pair.symbol_en
        
        # Check if already exists
        exists = session.query(SymbolPrice).filter_by(symbol=symbol_en).first()
        if exists:
            skip_count += 1
            continue
        
        try:
            print(f"[{i}/{total_symbols}] Fetching {symbol_fa}...", flush=True)
            df = PriceHistoryManager.get_price_history(symbol_fa, adjust_price=adjust, ignore_date=True)
            if not (isinstance(df, pd.DataFrame) and not df.empty):
                print(f"  [✗] No data for {symbol_fa}", flush=True)
                error_count += 1
                continue
            count = 0
            for idx, row in df.iterrows():
                date_val = str(idx)
                if not date_val or pd.isnull(date_val):
                    continue
                # Normalize row keys (handle Persian/English column names)
                row_dict = {}
                for k, v in row.items():
                    k_normalized = str(k).lower().strip().replace(' ', '')
                    row_dict[k_normalized] = v
                # Map to SymbolPrice fields
                price_kwargs = dict(
                    symbol=symbol_en,
                    date=date_val,
                    open=row_dict.get('open'),
                    high=row_dict.get('high'),
                    low=row_dict.get('low'),
                    close=row_dict.get('close'),
                    final=row_dict.get('final'),
                    last=row_dict.get('last'),
                    volume=row_dict.get('volume'),
                    value=row_dict.get('value'),
                    count=row_dict.get('no'),
                    adjusted_close=row_dict.get('adjclose'),
                    gregorian_date=row_dict.get('date'),
                )
                # Only pass valid keys
                price = SymbolPrice(**{k: v for k, v in price_kwargs.items() if k in SymbolPrice.__table__.columns.keys()})
                session.merge(price)
                count += 1
            session.commit()
            if count > 0:
                print(f"  [✓] Stored {count} records for {symbol_fa}", flush=True)
                success_count += 1
            else:
                print(f"  [✗] No valid records stored for {symbol_fa}", flush=True)
        except Exception as e:
            print(f"  [✗] Error fetching {symbol_fa}: {e}", flush=True)
            error_count += 1
            session.rollback()
    
    session.close()
    print(f"[SymbolPrice] Complete: {success_count} success, {skip_count} skipped, {error_count} errors", flush=True)



def fetch_and_store_index_prices(indices=None, adjust=False):
    """Fetch and store index prices. If indices is empty, fetch main indices."""
    session = SessionLocal()
    

    # شاخص‌های اصلی بازار
    main_indices = [
        ("شاخص کل", 32097828799138957),
        ("شاخص هم وزن", 67130298613737946),
        ("شاخص 30 شرکت بزرگ", 10523825119011581)
    ]

    # دریافت لیست صنایع و WebIDها
    from gravity_tse import get_sector_webid_map
    sector_map = get_sector_webid_map()
    sector_indices = [(sector, webid) for sector, webid in sector_map.items()]

    # ترکیب شاخص‌های اصلی و صنایع
    all_indices = main_indices + sector_indices
    print(f"[IndexPrice] Fetching prices for {len(all_indices)} indices (main + sectors)...", flush=True)

    success_count = 0
    error_count = 0

    for i, (index_name, webid) in enumerate(all_indices, 1):
        try:
            print(f"[{i}/{len(all_indices)}] Processing index: {index_name}", flush=True)
            # ثبت یا دریافت رکورد شاخص
            idx_obj = session.query(Index).filter_by(name=index_name).first()
            if not idx_obj:
                idx_obj = Index(name=index_name, type='sector', description=index_name, web_id=str(webid))
                session.add(idx_obj)
                session.commit()
                print(f"  [✓] Created index record for {index_name}", flush=True)
            else:
                print(f"  [✓] Index record already exists for {index_name}", flush=True)

            # دریافت داده‌های تاریخی شاخص
            r = None
            try:
                url = f'https://old.tsetmc.com/tsev2/chart/data/IndexFinancial.aspx?i={webid}&t=ph'
                import requests
                r = requests.get(url)
            except Exception as e:
                print(f"  [✗] Error fetching data for {index_name}: {e}", flush=True)
                error_count += 1
                continue
            if not r or not r.text:
                print(f"  [✗] No data for {index_name}", flush=True)
                error_count += 1
                continue
            import pandas as pd
            df = pd.DataFrame(r.text.split(';'))
            columns = ['Date','High','Low','Open','Close','Volume','D']
            try:
                df[columns] = df[0].str.split(",",expand=True)
            except Exception as e:
                print(f"  [✗] Error parsing data for {index_name}: {e}", flush=True)
                error_count += 1
                continue
            df.drop(columns=[0,'D'],inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df['J-Date'] = df['Date'].apply(lambda x: str(jdatetime.date.fromgregorian(date=x.date())))
            df = df.set_index('J-Date')
            df = df[['Date','Open','High','Low','Close','Volume']]
            df[['Open','High','Low','Close','Volume']] = df[['Open','High','Low','Close','Volume']].apply(pd.to_numeric, axis=1)

            # ذخیره در دیتابیس
            count = 0
            for idx, row in df.iterrows():
                date_val = str(idx)
                if not date_val or pd.isnull(date_val):
                    continue
                price_kwargs = dict(
                    index_id=idx_obj.id,
                    date=date_val,
                    gregorian_date=row['Date'].strftime('%Y-%m-%d') if not pd.isnull(row['Date']) else None,
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    final=row['Close'],
                    volume=row['Volume'],
                    value=None
                )
                price = IndexPrice(**{k: v for k, v in price_kwargs.items() if k in IndexPrice.__table__.columns.keys()})
                session.merge(price)
                count += 1
            session.commit()
            if count > 0:
                print(f"  [✓] Stored {count} records for {index_name}", flush=True)
                success_count += 1
            else:
                print(f"  [✗] No valid records stored for {index_name}", flush=True)
        except Exception as e:
            print(f"  [✗] Error processing {index_name}: {e}", flush=True)
            error_count += 1
            session.rollback()

    session.close()
    print(f"[IndexPrice] Complete: {success_count} success, {error_count} errors", flush=True)

