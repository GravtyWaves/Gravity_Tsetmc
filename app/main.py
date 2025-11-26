

from fastapi import FastAPI, Request, Body


app = FastAPI()

@app.post("/update-usd/")
def update_usd():
    try:
        print("[API] Updating USD/IRR prices...", flush=True)
        fetch_and_store_usd_irr_prices()
        print("[API] USD/IRR prices updated.", flush=True)
        return {"status": "usd updated"}
    except Exception as e:
        print(f"[ERROR] Exception in update_usd: {e}", flush=True)
        return {"status": "error", "message": str(e)}

@app.post("/update-db/")
def update_db(payload: dict = Body(...)):
    try:
        print("[API] Updating DB with payload:", payload, flush=True)
        symbols = payload.get("symbols", [])
        indices = payload.get("indices", [])
        industries = payload.get("industries", [])
        adjust = payload.get("adjust", True)
        if symbols:
            print(f"[API] Updating symbol prices for {len(symbols)} symbols...", flush=True)
            fetch_and_store_symbol_prices(symbols, adjust=adjust)
        if indices:
            print(f"[API] Updating index prices for {len(indices)} indices...", flush=True)
            fetch_and_store_index_prices(indices, adjust=adjust)
        if industries:
            print(f"[API] Updating industry indices for {len(industries)} industries...", flush=True)
            fetch_and_store_industry_indices(industries, adjust=adjust)
        print("[API] DB update complete.", flush=True)
        return {"status": "db updated"}
    except Exception as e:
        print(f"[ERROR] Exception in update_db: {e}", flush=True)
        return {"status": "error", "message": str(e)}

import logging
import sys
from .usd_fetcher import fetch_and_store_usd_irr_prices
from .fetcher import fetch_and_store_symbol_prices, fetch_and_store_index_prices, fetch_and_store_industry_indices
from .list_fetcher import fetch_and_store_symbol_list, fetch_and_store_index_list

# تنظیم encoding برای پشتیبانی از کاراکترهای یونیکد
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# تنظیم logging برای نمایش همه لاگ‌ها در کنسول uvicorn
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = FastAPI()

@app.post("/fetch-all/")
def fetch_all():
    try:
        print("[INFO] Fetching and storing ALL data (lists, prices, USD)...", flush=True)
        print("[STEP 1] Fetching symbol list...", flush=True)
        fetch_and_store_symbol_list()
        print("[STEP 2] Fetching index list...", flush=True)
        fetch_and_store_index_list()
        # [STEP 3] Fetching industry index list removed (no longer needed)
        print("[STEP 4] Fetching market list...", flush=True)
        from .list_fetcher import fetch_and_store_market_list, fetch_and_store_panel_list, fetch_and_store_sector_list
        fetch_and_store_market_list()
        print("[STEP 5] Fetching panel list...", flush=True)
        fetch_and_store_panel_list()
        print("[STEP 6] Fetching sector list...", flush=True)
        fetch_and_store_sector_list()
        print("[STEP 8] Fetching USD/IRR prices...", flush=True)
        fetch_and_store_usd_irr_prices()
        print("[STEP 9] Fetching all symbols, indices, industries from DB...", flush=True)
        from .db import SessionLocal, SymbolList, Index
        session = SessionLocal()
        symbols = [(row.symbol_fa, row.symbol_en) for row in session.query(SymbolList).all()]
        indices = [row.name for row in session.query(Index).filter_by(type='market').all()]
        industries = [row.name for row in session.query(Index).filter_by(type='sector').all()]
        session.close()
        print(f"[STEP 10] Fetching and storing prices for {len(symbols)} symbols...", flush=True)
        fetch_and_store_symbol_prices(symbols, adjust=True)
        print(f"[STEP 11] Fetching and storing prices for {len(indices)} indices...", flush=True)
        fetch_and_store_index_prices(indices, adjust=True)
        print(f"[STEP 12] Fetching and storing prices for {len(industries)} industries...", flush=True)
        fetch_and_store_industry_indices(industries, adjust=True)
        print("[DONE] All data fetched and stored.", flush=True)
        return {"status": "all data fetched"}
    except Exception as e:
        print(f"[ERROR] Exception in fetch_all: {e}", flush=True)
        return {"status": "error", "message": str(e)}
