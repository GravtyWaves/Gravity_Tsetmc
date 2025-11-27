import logging
import sys
import pandas as pd
from datetime import datetime
import jdatetime

from gravity_tse import PriceHistoryManager, Get_RI_History, Get_ShareHoldersInfo, USDManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

from .db import SessionLocal, SymbolPrice, IndexPrice, Index, SymbolList, RIData, ShareholdersInfo, UsdIrrPrice




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
        # Handle different input types: tuples, objects, or strings
        if isinstance(symbol_pair, tuple):
            symbol_fa, symbol_en = symbol_pair
        elif isinstance(symbol_pair, str):
            # If it's a string, look up the symbol in the database
            symbol_record = session.query(SymbolList).filter_by(symbol_en=symbol_pair).first()
            if not symbol_record:
                print(f"  [✗] Symbol '{symbol_pair}' not found in database", flush=True)
                error_count += 1
                continue
            symbol_fa = symbol_record.symbol_fa
            symbol_en = symbol_record.symbol_en
        else:
            # Assume it's an object with symbol_fa and symbol_en attributes
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
                # تبدیل تاریخ جلالی به میلادی برای gregorian_date
                try:
                    jalali_date = date_val
                    year, month, day = map(int, jalali_date.split('-'))
                    gregorian_date = jdatetime.date(year, month, day).togregorian().strftime('%Y-%m-%d')
                except Exception:
                    gregorian_date = None
                price_kwargs = dict(
                    symbol=symbol_en,
                    date=date_val,
                    gregorian_date=gregorian_date,
                    open=row_dict.get('open'),
                    high=row_dict.get('high'),
                    low=row_dict.get('low'),
                    close=row_dict.get('close'),
                    final=row_dict.get('final'),
                    volume=row_dict.get('volume'),
                    value=row_dict.get('value'),
                    count=row_dict.get('no'),
                    adj_open=row_dict.get('adjopen') or row_dict.get('adj open'),
                    adj_high=row_dict.get('adjhigh') or row_dict.get('adj high'),
                    adj_low=row_dict.get('adjlow') or row_dict.get('adj low'),
                    adj_close=row_dict.get('adjclose') or row_dict.get('adj close'),
                    adj_final=row_dict.get('adjfinal') or row_dict.get('adj final'),
                    adj_volume=row_dict.get('adjvolume') or row_dict.get('adj volume') or row_dict.get('volume'),  # Adjusted volume if available, else regular volume
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

    """Fetch and store index prices. If indices is empty, fetch all from gravity_tse.get_all_indices."""
    session = SessionLocal()
    from gravity_tse import get_all_indices
    if indices is None or not indices:
        indices = get_all_indices()
    print(f"[IndexPrice] Fetching prices for {len(indices)} indices (main + sector)...", flush=True)

    success_count = 0
    error_count = 0

    for i, idx in enumerate(indices, 1):
        index_name = idx["name"]
        webid = idx["web_id"]
        idx_type = idx.get("type", "sector")
        try:
            print(f"[{i}/{len(indices)}] Processing index: {index_name} (type: {idx_type})", flush=True)
            # ثبت یا دریافت رکورد شاخص
            idx_obj = session.query(Index).filter_by(name=index_name).first()
            if not idx_obj:
                idx_obj = Index(name=index_name, type=idx_type, description=index_name, web_id=str(webid))
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
                r = requests.get(url, timeout=10)
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
            for idx_row, row in df.iterrows():
                date_val = str(idx_row)
                if not date_val or pd.isnull(date_val):
                    continue
                open_val = row['Open']
                if pd.isnull(open_val) or open_val == 0:
                    prev_idx = df.index.get_loc(idx_row) - 1
                    if prev_idx >= 0:
                        prev_close = df.iloc[prev_idx]['Close']
                        open_val = prev_close
                price_kwargs = dict(
                    index_id=idx_obj.id,
                    date=date_val,
                    gregorian_date=row['Date'].strftime('%Y-%m-%d') if not pd.isnull(row['Date']) else None,
                    open=open_val,
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


def fetch_and_store_ri_data(symbols=None):
    """Fetch and store RI data for symbols. If symbols is empty, fetch all."""
    session = SessionLocal()

    # اگر symbols خالی است، همه نمادها را از دیتابیس بگیر
    if not symbols:
        symbol_records = session.query(SymbolList).all()
        symbols = [(s.symbol_fa, s.symbol_en) for s in symbol_records]

    total_symbols = len(symbols) if isinstance(symbols, list) else len(list(symbols))
    print(f"[RIData] Fetching RI data for {total_symbols} symbols...", flush=True)

    success_count = 0
    skip_count = 0
    error_count = 0

    for i, symbol_pair in enumerate(symbols, 1):
        # Handle different input types: tuples, objects, or strings
        if isinstance(symbol_pair, tuple):
            symbol_fa, symbol_en = symbol_pair
        elif isinstance(symbol_pair, str):
            # If it's a string, look up the symbol in the database
            symbol_record = session.query(SymbolList).filter_by(symbol_en=symbol_pair).first()
            if not symbol_record:
                print(f"  [✗] Symbol '{symbol_pair}' not found in database", flush=True)
                error_count += 1
                continue
            symbol_fa = symbol_record.symbol_fa
            symbol_en = symbol_record.symbol_en
        else:
            # Assume it's an object with symbol_fa and symbol_en attributes
            symbol_fa = symbol_pair.symbol_fa
            symbol_en = symbol_pair.symbol_en

        # Check if already exists
        exists = session.query(RIData).filter_by(symbol=symbol_en).first()
        if exists:
            skip_count += 1
            continue

        try:
            print(f"[{i}/{total_symbols}] Fetching RI data for {symbol_fa}...", flush=True)
            df = Get_RI_History.get_ri_history(symbol_fa)
            if not (isinstance(df, pd.DataFrame) and not df.empty):
                print(f"  [✗] No RI data for {symbol_fa}", flush=True)
                error_count += 1
                continue
            count = 0
            for idx, row in df.iterrows():
                date_val = str(idx)
                if not date_val or pd.isnull(date_val):
                    continue
                # Normalize row keys
                row_dict = {}
                for k, v in row.items():
                    k_normalized = str(k).lower().strip().replace(' ', '')
                    row_dict[k_normalized] = v
                # تبدیل تاریخ جلالی به میلادی برای gregorian_date
                try:
                    jalali_date = date_val
                    year, month, day = map(int, jalali_date.split('-'))
                    gregorian_date = jdatetime.date(year, month, day).togregorian().strftime('%Y-%m-%d')
                except Exception:
                    gregorian_date = None
                ri_kwargs = dict(
                    symbol=symbol_en,
                    date=date_val,
                    gregorian_date=gregorian_date,
                    # Real (individual) data
                    no_buy_real=row_dict.get('nobuyreal') or row_dict.get('no buy real'),
                    no_sell_real=row_dict.get('nosellreal') or row_dict.get('no sell real'),
                    vol_buy_real=row_dict.get('volbuyreal') or row_dict.get('vol buy real'),
                    vol_sell_real=row_dict.get('volsellreal') or row_dict.get('vol sell real'),
                    val_buy_real=row_dict.get('valbuyreal') or row_dict.get('val buy real'),
                    val_sell_real=row_dict.get('valsellreal') or row_dict.get('val sell real'),
                    # Institutional data
                    no_buy_inst=row_dict.get('nobuyinst') or row_dict.get('no buy inst'),
                    no_sell_inst=row_dict.get('nosellinst') or row_dict.get('no sell inst'),
                    vol_buy_inst=row_dict.get('volbuyinst') or row_dict.get('vol buy inst'),
                    vol_sell_inst=row_dict.get('volsellinst') or row_dict.get('vol sell inst'),
                    val_buy_inst=row_dict.get('valbuyinst') or row_dict.get('val buy inst'),
                    val_sell_inst=row_dict.get('valsellinst') or row_dict.get('val sell inst'),
                )
                # Only pass valid keys
                ri_data = RIData(**{k: v for k, v in ri_kwargs.items() if k in RIData.__table__.columns.keys()})
                session.merge(ri_data)
                count += 1
            session.commit()
            if count > 0:
                print(f"  [✓] Stored {count} RI records for {symbol_fa}", flush=True)
                success_count += 1
            else:
                print(f"  [✗] No valid RI records stored for {symbol_fa}", flush=True)
        except Exception as e:
            print(f"  [✗] Error fetching RI data for {symbol_fa}: {e}", flush=True)
            error_count += 1
            session.rollback()

    session.close()
    print(f"[RIData] Complete: {success_count} success, {skip_count} skipped, {error_count} errors", flush=True)


def fetch_and_store_shareholders_info(symbols=None):
    """Fetch and store shareholders info for symbols. If symbols is empty, fetch all."""
    session = SessionLocal()

    # اگر symbols خالی است، همه نمادها را از دیتابیس بگیر
    if not symbols:
        symbol_records = session.query(SymbolList).all()
        symbols = [(s.symbol_fa, s.symbol_en) for s in symbol_records]

    total_symbols = len(symbols) if isinstance(symbols, list) else len(list(symbols))
    print(f"[ShareholdersInfo] Fetching shareholders info for {total_symbols} symbols...", flush=True)

    success_count = 0
    skip_count = 0
    error_count = 0

    for i, symbol_pair in enumerate(symbols, 1):
        # Handle different input types: tuples, objects, or strings
        if isinstance(symbol_pair, tuple):
            symbol_fa, symbol_en = symbol_pair
        elif isinstance(symbol_pair, str):
            # If it's a string, look up the symbol in the database
            symbol_record = session.query(SymbolList).filter_by(symbol_en=symbol_pair).first()
            if not symbol_record:
                print(f"  [✗] Symbol '{symbol_pair}' not found in database", flush=True)
                error_count += 1
                continue
            symbol_fa = symbol_record.symbol_fa
            symbol_en = symbol_record.symbol_en
        else:
            # Assume it's an object with symbol_fa and symbol_en attributes
            symbol_fa = symbol_pair.symbol_fa
            symbol_en = symbol_pair.symbol_en

        # Check if already exists
        exists = session.query(ShareholdersInfo).filter_by(symbol=symbol_en).first()
        if exists:
            skip_count += 1
            continue

        try:
            print(f"[{i}/{total_symbols}] Fetching shareholders info for {symbol_fa}...", flush=True)
            df = Get_ShareHoldersInfo.get_shareholders_info(symbol_fa)
            if not (isinstance(df, pd.DataFrame) and not df.empty):
                print(f"  [✗] No shareholders info for {symbol_fa}", flush=True)
                error_count += 1
                continue
            count = 0
            for idx, row in df.iterrows():
                date_val = str(idx)
                if not date_val or pd.isnull(date_val):
                    continue
                # Normalize row keys
                row_dict = {}
                for k, v in row.items():
                    k_normalized = str(k).lower().strip().replace(' ', '')
                    row_dict[k_normalized] = v
                # تبدیل تاریخ جلالی به میلادی برای gregorian_date
                try:
                    jalali_date = date_val
                    year, month, day = map(int, jalali_date.split('-'))
                    gregorian_date = jdatetime.date(year, month, day).togregorian().strftime('%Y-%m-%d')
                except Exception:
                    gregorian_date = None
                shareholders_kwargs = dict(
                    symbol=symbol_en,
                    date=date_val,
                    gregorian_date=gregorian_date,
                    holder_name=row_dict.get('holdername') or row_dict.get('shareholdername'),
                    shares=row_dict.get('shares') or row_dict.get('sharescount'),
                    shares_percent=row_dict.get('sharespercent') or row_dict.get('percentage'),
                    holder_type=row_dict.get('holdertype'),
                    national_id=row_dict.get('nationalid'),
                    change_percent=row_dict.get('changepercent'),
                )
                # Only pass valid keys
                shareholder_info = ShareholdersInfo(**{k: v for k, v in shareholders_kwargs.items() if k in ShareholdersInfo.__table__.columns.keys()})
                session.merge(shareholder_info)
                count += 1
            session.commit()
            if count > 0:
                print(f"  [✓] Stored {count} shareholders records for {symbol_fa}", flush=True)
                success_count += 1
            else:
                print(f"  [✗] No valid shareholders records stored for {symbol_fa}", flush=True)
        except Exception as e:
            print(f"  [✗] Error fetching shareholders info for {symbol_fa}: {e}", flush=True)
            error_count += 1
            session.rollback()

    session.close()
    print(f"[ShareholdersInfo] Complete: {success_count} success, {skip_count} skipped, {error_count} errors", flush=True)


def fetch_and_store_usd_irr_prices():
    """Fetch and store USD IRR prices."""
    session = SessionLocal()

    print("[UsdIrrPrice] Fetching USD IRR prices...", flush=True)

    try:
        df = USDManager.get_usd_irr_prices()
        if not (isinstance(df, pd.DataFrame) and not df.empty):
            print("  [✗] No USD IRR data", flush=True)
            return

        count = 0
        for idx, row in df.iterrows():
            date_val = str(idx)
            if not date_val or pd.isnull(date_val):
                continue
            # Normalize row keys
            row_dict = {}
            for k, v in row.items():
                k_normalized = str(k).lower().strip().replace(' ', '')
                row_dict[k_normalized] = v
            # تبدیل تاریخ جلالی به میلادی برای gregorian_date
            try:
                jalali_date = date_val
                year, month, day = map(int, jalali_date.split('-'))
                gregorian_date = jdatetime.date(year, month, day).togregorian().strftime('%Y-%m-%d')
            except Exception:
                gregorian_date = None
            usd_kwargs = dict(
                date=date_val,
                gregorian_date=gregorian_date,
                usd_price=row_dict.get('usdprice'),
                irr_price=row_dict.get('irrprice'),
                # Add other fields as per UsdIrrPrice model
            )
            # Only pass valid keys
            usd_irr_price = UsdIrrPrice(**{k: v for k, v in usd_kwargs.items() if k in UsdIrrPrice.__table__.columns.keys()})
            session.merge(usd_irr_price)
            count += 1
        session.commit()
        if count > 0:
            print(f"  [✓] Stored {count} USD IRR records", flush=True)
        else:
            print("  [✗] No valid USD IRR records stored", flush=True)
    except Exception as e:
        print(f"  [✗] Error fetching USD IRR prices: {e}", flush=True)
        session.rollback()

    session.close()
    print("[UsdIrrPrice] Complete", flush=True)
