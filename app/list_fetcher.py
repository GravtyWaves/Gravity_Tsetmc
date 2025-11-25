from finpy_tse import Build_Market_StockList, __Get_TSE_Sector_WebID__
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
    print("[Sector] Loading sectors from JSON...", flush=True)
    try:
        with open("BasicTseInformation/sectors.json", "r", encoding="utf-8") as f:
            sectors = json.load(f)
    except FileNotFoundError:
        print("[Sector] Error: sectors.json not found.", flush=True)
        session.close()
        return
    count = 0
    for item in sectors:
        sector = Sector(
            sector_id=item.get("SectorID"),
            sector_name=item.get("SectorName")
        )
        session.merge(sector)
        count += 1
    session.commit()
    session.close()
    print(f"[Sector] Stored {count} sectors.", flush=True)

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
    count = 0
    for item in companies:
        english_symbol = item.get("Ticker4") or item.get("CompanyCode12")
        persian_symbol = item.get("Ticker")
        if not english_symbol or not persian_symbol:
            continue  # skip if missing key fields
        count += 1
        if count % 100 == 0:
            print(f"[SymbolList] Processed {count} symbols so far...", flush=True)
        symbol = SymbolList(
            symbol_en=english_symbol,
            symbol_fa=persian_symbol,
            name=item.get("Name"),
            market_id=item.get("MarketID"),
            sector_id=item.get("SectorID"),
            panel_id=item.get("PanelID")
        )
        session.merge(symbol)
    session.commit()
    session.close()
    print(f"[SymbolList] Processed {count} symbols total", flush=True)

def fetch_and_store_index_list():

    import json
    from finpy_tse import get_sector_webid_map
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
        idx = session.query(Index).filter_by(name=fa_name, type=typ).first()
        if not idx:
            idx = Index(name=fa_name, type=typ, web_id=web_id, description=en_name)
            session.add(idx)
        else:
            idx.web_id = web_id
            idx.description = en_name
        session.commit()

    # Sector indices (from SECTOR_WEBID_MAP)
    sector_webid_map = get_sector_webid_map()
    for fa_sector, web_id in sector_webid_map.items():
        en_sector = farsi_to_english(fa_sector)
        idx = session.query(Index).filter_by(name=fa_sector, type='sector').first()
        if not idx:
            idx = Index(name=fa_sector, type='sector', web_id=str(web_id), description=en_sector)
            session.add(idx)
        else:
            idx.web_id = str(web_id)
            idx.description = en_sector
        session.commit()

    session.close()
    print("[Index] All indices (main + sectors) stored in unified table.", flush=True)

