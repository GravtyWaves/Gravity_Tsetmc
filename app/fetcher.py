"""
Data fetching and storage module for TSETMC data.
Combines list_fetcher.py and fetcher.py functionality.
"""

import json
import logging
import sys
import pandas as pd
from datetime import datetime
import jdatetime
import requests

from gravity_tse import (
    PriceHistoryManager, 
    Get_RI_History, 
    Get_ShareHoldersInfo, 
    USDManager,
    get_sector_webid_map,
    get_all_indices
)

from .db import (
    SessionLocal, 
    SymbolPrice, 
    IndexPrice, 
    Index, 
    Symbol, 
    RIData, 
    ShareholdersInfo, 
    UsdIrrPrice,
    Market,
    Panel,
    Sector
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

# ==================== LIST FETCHING FUNCTIONS ====================

def fetch_and_store_market_list():
    """Fetch and store market list from JSON"""
    session = SessionLocal()
    print("[Market] Loading markets from JSON...", flush=True)
    try:
        with open("BasicTseInformation/markets.json", "r", encoding="utf-8") as f:
            markets = json.load(f)
    except FileNotFoundError:
        print("[Market] Error: markets.json not found.", flush=True)
        session.close()
        return
    
    count = 0
    for item in markets:
        market = Market(
            market_id=item.get("MarketID"),
            market_name=item.get("MarketName")
        )
        session.merge(market)
        count += 1
    
    session.commit()
    session.close()
    print(f"[Market] Stored {count} markets.", flush=True)

def fetch_and_store_panel_list():
    """Fetch and store panel list from JSON"""
    session = SessionLocal()
    print("[Panel] Loading panels from JSON...", flush=True)
    try:
        with open("BasicTseInformation/panels.json", "r", encoding="utf-8") as f:
            panels = json.load(f)
    except FileNotFoundError:
        print("[Panel] Error: panels.json not found.", flush=True)
        session.close()
        return
    
    count = 0
    for item in panels:
        panel = Panel(
            panel_id=item.get("PanelID"),
            panel_name=item.get("PanelName")
        )
        session.merge(panel)
        count += 1
    
    session.commit()
    session.close()
    print(f"[Panel] Stored {count} panels.", flush=True)

def fetch_and_store_sector_list():
    """Fetch and store sector list from JSON and map to indices"""
    session = SessionLocal()
    print("[Sector] Loading sectors from JSON and mapping to indices...", flush=True)
    try:
        with open("BasicTseInformation/sectors.json", "r", encoding="utf-8") as f:
            sectors = json.load(f)
    except FileNotFoundError:
        print("[Sector] Error: sectors.json not found.", flush=True)
        session.close()
        return
    
    sector_webid_map = get_sector_webid_map()
    count = 0
    idx_count = 0
    
    for item in sectors:
        sector_id = item.get("SectorID")
        sector_name = item.get("SectorName")
        
        # Insert or update sector
        sector = session.query(Sector).filter_by(sector_id=sector_id).first()
        if not sector:
            sector = Sector(
                sector_id=sector_id, 
                sector_name=sector_name,
                english_name=item.get("EnglishName"),
                us_equivalent=item.get("USEquivalent")
            )
            session.add(sector)
        else:
            sector.sector_name = sector_name
            sector.english_name = item.get("EnglishName")
            sector.us_equivalent = item.get("USEquivalent")
        
        count += 1
        
        # If this sector has web_id, add to indices table
        web_id = None
        for k, v in sector_webid_map.items():
            if k.strip() == sector_name.strip():
                web_id = v
                break
        
        if web_id:
            # If index with same web_id exists, update it
            idx = session.query(Index).filter_by(web_id=str(web_id)).first()
            if not idx:
                idx = Index(
                    name=sector_name, 
                    type='sector', 
                    web_id=str(web_id), 
                    description=sector_name, 
                    sector_id=sector_id
                )
                session.add(idx)
            else:
                idx.name = sector_name
                idx.type = 'sector'
                idx.description = sector_name
                idx.sector_id = sector_id
            idx_count += 1
    
    session.commit()
    session.close()
    print(f"[Sector] Stored {count} sectors and {idx_count} sector indices.", flush=True)

def fetch_and_store_symbol_list():
    """Fetch and store symbol list from JSON"""
    session = SessionLocal()
    print("[Symbol] Starting to load symbol list from local JSON...", flush=True)
    try:
        with open("BasicTseInformation/companies.json", "r", encoding="utf-8") as f:
            companies = json.load(f)
    except FileNotFoundError:
        print("[Symbol] Error: companies.json not found.", flush=True)
        session.close()
        return
    
    print(f"[Symbol] Loaded {len(companies)} companies from JSON.", flush=True)
    
    # Get default values for missing fields
    markets = session.query(Market).all()
    sectors = session.query(Sector).all()
    
    default_market_id = markets[0].market_id if markets else 1.0
    default_sector_id = sectors[0].sector_id if sectors else 1.0
    
    count = 0
    skip_count = 0
    
    for item in companies:
        english_symbol = item.get("Ticker4") or item.get("CompanyCode12")
        persian_symbol = item.get("Ticker")
        if not english_symbol or not persian_symbol:
            skip_count += 1
            continue  # skip if missing key fields
        
        count += 1
        if count % 100 == 0:
            print(f"[Symbol] Processed {count} symbols so far...", flush=True)
        
        # Use defaults for missing market_id and sector_id
        market_id = item.get("MarketID") or default_market_id
        sector_id = item.get("SectorID") or default_sector_id
        
        symbol = Symbol(
            symbol_en=english_symbol,
            symbol_fa=persian_symbol,
            name=item.get("Name"),
            name_en=item.get("NameEn"),
            web_id=item.get("WebID"),
            industry=item.get("Industry"),
            market_id=market_id,
            sector_id=sector_id,
            panel_id=item.get("PanelID")
        )
        session.merge(symbol)
    
    session.commit()
    session.close()
    print(f"[Symbol] Processed {count} symbols total (skipped {skip_count})", flush=True)

def fetch_and_store_index_list():
    """Fetch and store main indices list"""
    session = SessionLocal()
    print("[Index] Storing all indices (main + sectors) in unified table...", flush=True)

    # Helper: generate English name from Farsi
    def farsi_to_english(fa_name):
        import re
        # Replace Persian numbers, remove special chars, replace spaces with _
        en = fa_name
        en = en.replace('شاخص', 'Index')
        en = en.replace('کل', 'Total')
        en = en.replace('هم وزن', 'EqualWeight')
        en = en.replace('قیمت', 'Price')
        en = en.replace('وزنی-ارزشی', 'CapWeighted')
        en = en.replace('شناور آزاد', 'FreeFloat')
        en = en.replace('بازار اول', 'FirstMarket')
        en = en.replace('بازار دوم', 'SecondMarket')
        en = en.replace('صنعت', 'Industry')
        en = en.replace('شرکت بزرگ', 'LargeCap')
        en = en.replace('شرکت فعالتر', 'Active50')
        en = en.replace('شرکت', 'Company')
        en = en.replace('فعالتر', 'Active')
        en = en.replace(' ', '_')
        en = re.sub(r'[^A-Za-z0-9_]', '', en)
        return en

    # Main indices (Farsi name, English name, web_id, type)
    main_indices = [
        ("شاخص کل", "Index_Total", "32097828799138957", "market"),
        ("شاخص هم وزن", "Index_EqualWeight", "67130298613737946", "market"),
        ("شاخص قیمت (وزنی-ارزشی)", "Index_Price_CapWeighted", "5798407779416661", "market"),
        ("شاخص قیمت (هم وزن)", "Index_Price_EqualWeight", "8384385859414435", "market"),
        ("شاخص شناور آزاد", "Index_FreeFloat", "49579049405614711", "market"),
        ("شاخص بازار اول", "Index_FirstMarket", "62752761908615603", "market"),
        ("شاخص بازار دوم", "Index_SecondMarket", "71704845530629737", "market"),
        ("شاخص صنعت", "Index_Industry", "43754960038275285", "market"),
        ("شاخص 30 شرکت بزرگ", "Index_30_LargeCap", "10523825119011581", "market"),
        ("شاخص 50 شرکت فعالتر", "Index_50_Active", "46342955726788357", "market")
    ]
    
    for fa_name, en_name, web_id, typ in main_indices:
        # If index with same web_id exists, update it
        idx = session.query(Index).filter_by(web_id=str(web_id)).first()
        if not idx:
            idx = Index(
                name=fa_name, 
                name_en=en_name,
                type=typ, 
                web_id=str(web_id), 
                description=en_name
            )
            session.add(idx)
        else:
            idx.name = fa_name
            idx.name_en = en_name
            idx.type = typ
            idx.description = en_name
        session.commit()
    
    session.close()
    print("[Index] All indices (main + sectors) stored in unified table.", flush=True)

def initialize_all_lists():
    """Initialize all basic lists (markets, panels, sectors, symbols, indices)"""
    print("[Initialization] Starting to initialize all basic lists...", flush=True)
    fetch_and_store_market_list()
    fetch_and_store_panel_list()
    fetch_and_store_sector_list()
    fetch_and_store_symbol_list()
    fetch_and_store_index_list()
    print("[Initialization] All basic lists initialized successfully.", flush=True)

# ==================== DATA FETCHING FUNCTIONS ====================

def _get_symbol_pair(session, symbol_input):
    """Helper function to get symbol_fa and symbol_en from various input types"""
    if isinstance(symbol_input, tuple):
        return symbol_input[0], symbol_input[1]  # (symbol_fa, symbol_en)
    elif isinstance(symbol_input, str):
        # If it's a string, look up the symbol in the database
        symbol_record = session.query(Symbol).filter_by(symbol_en=symbol_input).first()
        if not symbol_record:
            return None, None
        return symbol_record.symbol_fa, symbol_record.symbol_en
    else:
        # Assume it's an object with symbol_fa and symbol_en attributes
        return symbol_input.symbol_fa, symbol_input.symbol_en

def _convert_jalali_to_gregorian(jalali_date):
    """Convert Jalali date to Gregorian date"""
    try:
        year, month, day = map(int, jalali_date.split('-'))
        gregorian_date = jdatetime.date(year, month, day).togregorian().strftime('%Y-%m-%d')
        return gregorian_date
    except Exception:
        return None

def _normalize_row_keys(row):
    """Normalize row keys to handle Persian/English column names"""
    row_dict = {}
    for k, v in row.items():
        k_normalized = str(k).lower().strip().replace(' ', '')
        row_dict[k_normalized] = v
    return row_dict

def fetch_and_store_symbol_prices(symbols=None, adjust=False):
    """Fetch and store symbol prices. If symbols is empty, fetch all."""
    session = SessionLocal()

    # If symbols is empty, get all symbols from database
    if not symbols:
        symbol_records = session.query(Symbol).all()
        symbols = [(s.symbol_fa, s.symbol_en) for s in symbol_records]

    total_symbols = len(symbols) if isinstance(symbols, list) else len(list(symbols))
    print(f"[SymbolPrice] Fetching prices for {total_symbols} symbols...", flush=True)

    success_count = 0
    skip_count = 0
    error_count = 0

    for i, symbol_input in enumerate(symbols, 1):
        symbol_fa, symbol_en = _get_symbol_pair(session, symbol_input)
        if not symbol_fa or not symbol_en:
            print(f"  [✗] Symbol '{symbol_input}' not found in database", flush=True)
            error_count += 1
            continue

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
                
                row_dict = _normalize_row_keys(row)
                gregorian_date = _convert_jalali_to_gregorian(date_val)
                
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
                    adj_volume=row_dict.get('adjvolume') or row_dict.get('adj volume') or row_dict.get('volume'),
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
            
            # Register or get index record
            idx_obj = session.query(Index).filter_by(name=index_name).first()
            if not idx_obj:
                idx_obj = Index(
                    name=index_name, 
                    type=idx_type, 
                    description=index_name, 
                    web_id=str(webid)
                )
                session.add(idx_obj)
                session.commit()
                print(f"  [✓] Created index record for {index_name}", flush=True)
            else:
                print(f"  [✓] Index record already exists for {index_name}", flush=True)

            # Fetch historical index data
            try:
                url = f'https://old.tsetmc.com/tsev2/chart/data/IndexFinancial.aspx?i={webid}&t=ph'
                r = requests.get(url, timeout=10)
            except Exception as e:
                print(f"  [✗] Error fetching data for {index_name}: {e}", flush=True)
                error_count += 1
                continue
                
            if not r or not r.text:
                print(f"  [✗] No data for {index_name}", flush=True)
                error_count += 1
                continue
            
            # Parse the data
            df = pd.DataFrame(r.text.split(';'))
            columns = ['Date','High','Low','Open','Close','Volume','D']
            
            try:
                df[columns] = df[0].str.split(",", expand=True)
            except Exception as e:
                print(f"  [✗] Error parsing data for {index_name}: {e}", flush=True)
                error_count += 1
                continue
                
            df.drop(columns=[0,'D'], inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df['J-Date'] = df['Date'].apply(lambda x: str(jdatetime.date.fromgregorian(date=x.date())))
            df = df.set_index('J-Date')
            df = df[['Date','Open','High','Low','Close','Volume']]
            df[['Open','High','Low','Close','Volume']] = df[['Open','High','Low','Close','Volume']].apply(pd.to_numeric, axis=1)

            # Store in database
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

    # If symbols is empty, get all symbols from database
    if not symbols:
        symbol_records = session.query(Symbol).all()
        symbols = [(s.symbol_fa, s.symbol_en) for s in symbol_records]

    total_symbols = len(symbols) if isinstance(symbols, list) else len(list(symbols))
    print(f"[RIData] Fetching RI data for {total_symbols} symbols...", flush=True)

    success_count = 0
    skip_count = 0
    error_count = 0

    for i, symbol_input in enumerate(symbols, 1):
        symbol_fa, symbol_en = _get_symbol_pair(session, symbol_input)
        if not symbol_fa or not symbol_en:
            print(f"  [✗] Symbol '{symbol_input}' not found in database", flush=True)
            error_count += 1
            continue

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
                
                row_dict = _normalize_row_keys(row)
                gregorian_date = _convert_jalali_to_gregorian(date_val)
                
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

    # If symbols is empty, get all symbols from database
    if not symbols:
        symbol_records = session.query(Symbol).all()
        symbols = [(s.symbol_fa, s.symbol_en) for s in symbol_records]

    total_symbols = len(symbols) if isinstance(symbols, list) else len(list(symbols))
    print(f"[ShareholdersInfo] Fetching shareholders info for {total_symbols} symbols...", flush=True)

    success_count = 0
    skip_count = 0
    error_count = 0

    for i, symbol_input in enumerate(symbols, 1):
        symbol_fa, symbol_en = _get_symbol_pair(session, symbol_input)
        if not symbol_fa or not symbol_en:
            print(f"  [✗] Symbol '{symbol_input}' not found in database", flush=True)
            error_count += 1
            continue

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
                
                row_dict = _normalize_row_keys(row)
                gregorian_date = _convert_jalali_to_gregorian(date_val)
                
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
            
            row_dict = _normalize_row_keys(row)
            gregorian_date = _convert_jalali_to_gregorian(date_val)
            
            usd_kwargs = dict(
                date=date_val,
                gregorian_date=gregorian_date,
                buy_price=row_dict.get('buyprice') or row_dict.get('buy_price'),
                sell_price=row_dict.get('sellprice') or row_dict.get('sell_price'),
                open=row_dict.get('open'),
                high=row_dict.get('high'),
                low=row_dict.get('low'),
                close=row_dict.get('close'),
                source=row_dict.get('source')
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

def fetch_all_data():
    """Fetch and store all types of data"""
    print("[AllData] Starting to fetch all data...", flush=True)
    fetch_and_store_symbol_prices()
    fetch_and_store_index_prices()
    fetch_and_store_ri_data()
    fetch_and_store_shareholders_info()
    fetch_and_store_usd_irr_prices()
    print("[AllData] All data fetched successfully.", flush=True)

# For backward compatibility
SymbolList = Symbol