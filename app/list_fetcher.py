import json
import pandas as pd
from gravity_tse import get_sector_webid_map
from .db import SessionLocal, SymbolList, Index, Market, Panel, Sector


def fetch_and_store_market_list():
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
    session = SessionLocal()
    print("[Sector] Loading sectors from JSON and mapping to indices...", flush=True)
    try:
        with open("BasicTseInformation/sectors.json", "r", encoding="utf-8") as f:
            sectors = json.load(f)
    except FileNotFoundError:
        print("[Sector] Error: sectors.json not found.", flush=True)
        session.close()
        return
    from gravity_tse import get_sector_webid_map
    sector_webid_map = get_sector_webid_map()
    count = 0
    idx_count = 0
    for item in sectors:
        sector_id = item.get("SectorID")
        sector_name = item.get("SectorName")
        # درج یا به‌روزرسانی صنعت
        sector = session.query(Sector).filter_by(sector_id=sector_id).first()
        if not sector:
            sector = Sector(sector_id=sector_id, sector_name=sector_name)
            session.add(sector)
        else:
            sector.sector_name = sector_name
        count += 1
        # اگر این صنعت web_id دارد، به جدول شاخص‌ها هم اضافه یا آپدیت کن
        web_id = None
        for k, v in sector_webid_map.items():
            if k.strip() == sector_name.strip():
                web_id = v
                break
        if web_id:
            from .db import Index
            # اگر شاخصی با همین web_id وجود دارد، فقط آپدیت کن
            idx = session.query(Index).filter_by(web_id=str(web_id)).first()
            if not idx:
                idx = Index(name=sector_name, type='sector', web_id=str(web_id), description=sector_name, sector_id=sector_id)
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

import pandas as pd
import json

def fetch_and_store_symbol_list():
    session = SessionLocal()
    print("[SymbolList] Starting to load symbol list from local JSON...", flush=True)
    try:
        with open("BasicTseInformation/companies.json", "r", encoding="utf-8") as f:
            companies = json.load(f)
    except FileNotFoundError:
        print("[SymbolList] Error: companies.json not found.", flush=True)
        session.close()
        return
    
    print(f"[SymbolList] Loaded {len(companies)} companies from JSON.", flush=True)
    
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
            print(f"[SymbolList] Processed {count} symbols so far...", flush=True)
        
        # Use defaults for missing market_id and sector_id
        market_id = item.get("MarketID") or default_market_id
        sector_id = item.get("SectorID") or default_sector_id
        
        symbol = SymbolList(
            symbol_en=english_symbol,
            symbol_fa=persian_symbol,
            name=item.get("Name"),
            market_id=market_id,
            sector_id=sector_id,
            panel_id=item.get("PanelID")
        )
        session.merge(symbol)
    
    session.commit()
    session.close()
    print(f"[SymbolList] Processed {count} symbols total (skipped {skip_count})", flush=True)

def fetch_and_store_index_list():

    import json
    from gravity_tse import get_sector_webid_map
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
        from .db import Index
        # اگر شاخصی با همین web_id وجود دارد، فقط آپدیت کن
        idx = session.query(Index).filter_by(web_id=str(web_id)).first()
        if not idx:
            idx = Index(name=fa_name, type=typ, web_id=str(web_id), description=en_name)
            session.add(idx)
        else:
            idx.name = fa_name
            idx.type = typ
            idx.description = en_name
        session.commit()
    # Sector indices (from SECTOR_WEBID_MAP) فقط اگر قبلاً درج نشده باشند (درج صنایع در fetch_and_store_sector_list انجام می‌شود)
    session.close()
    print("[Index] All indices (main + sectors) stored in unified table.", flush=True)

