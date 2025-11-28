

"""
FastAPI application for TSETMC data management.
Provides endpoints for fetching and updating stock market data.
"""

import logging
import sys
from typing import Dict, Any

from fastapi import FastAPI, Body

from .db import SessionLocal, SymbolList, Index
from .fetcher import (
    fetch_and_store_symbol_prices,
    fetch_and_store_index_prices,
    fetch_and_store_industry_indices
)
from .list_fetcher import (
    fetch_and_store_symbol_list,
    fetch_and_store_index_list,
    fetch_and_store_market_list,
    fetch_and_store_panel_list,
    fetch_and_store_sector_list
)
from .usd_fetcher import fetch_and_store_usd_irr_prices

# Configure encoding for Unicode support
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configure logging for uvicorn console output
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Create FastAPI application
app = FastAPI(
    title="TSETMC Data API",
    description="API for managing Tehran Stock Exchange data",
    version="1.0.0"
)


@app.post("/update-usd/")
async def update_usd() -> Dict[str, str]:
    """
    Update USD/IRR prices.

    Returns:
        Dict containing status of the operation.
    """
    try:
        print("[API] Updating USD/IRR prices...", flush=True)
        fetch_and_store_usd_irr_prices()
        print("[API] USD/IRR prices updated.", flush=True)
        return {"status": "usd updated"}
    except Exception as e:
        print(f"[ERROR] Exception in update_usd: {e}", flush=True)
        return {"status": "error", "message": str(e)}


@app.post("/update-db/")
async def update_db(payload: Dict[str, Any] = Body(...)) -> Dict[str, str]:
    """
    Update database with symbol and index prices.

    Args:
        payload: Dictionary containing symbols, indices, industries, and adjust flag.

    Returns:
        Dict containing status of the operation.
    """
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


@app.post("/fetch-all/")
async def fetch_all() -> Dict[str, str]:
    """
    Fetch and store all data: lists, prices, and USD rates.

    Returns:
        Dict containing status of the operation.
    """
    try:
        print("[INFO] Fetching and storing ALL data (lists, prices, USD)...", flush=True)

        print("[STEP 1] Fetching symbol list...", flush=True)
        fetch_and_store_symbol_list()

        print("[STEP 2] Fetching index list...", flush=True)
        fetch_and_store_index_list()

        # STEP 3: Industry index list removed (no longer needed)

        print("[STEP 4] Fetching market list...", flush=True)
        fetch_and_store_market_list()

        print("[STEP 5] Fetching panel list...", flush=True)
        fetch_and_store_panel_list()

        print("[STEP 6] Fetching sector list...", flush=True)
        fetch_and_store_sector_list()

        print("[STEP 7] Fetching USD/IRR prices...", flush=True)
        fetch_and_store_usd_irr_prices()

        print("[STEP 8] Fetching all symbols, indices, industries from DB...", flush=True)
        session = SessionLocal()
        symbols = [(row.symbol_fa, row.symbol_en) for row in session.query(SymbolList).all()]
        indices = [row.name for row in session.query(Index).filter_by(type='market').all()]
        industries = [row.name for row in session.query(Index).filter_by(type='sector').all()]
        session.close()

        print(f"[STEP 9] Fetching and storing prices for {len(symbols)} symbols...", flush=True)
        fetch_and_store_symbol_prices(symbols, adjust=True)

        print(f"[STEP 10] Fetching and storing prices for {len(indices)} indices...", flush=True)
        fetch_and_store_index_prices(indices, adjust=True)

        print(f"[STEP 11] Fetching and storing prices for {len(industries)} industries...", flush=True)
        fetch_and_store_industry_indices(industries, adjust=True)

        print("[DONE] All data fetched and stored.", flush=True)
        return {"status": "all data fetched"}
    except Exception as e:
        print(f"[ERROR] Exception in fetch_all: {e}", flush=True)
        return {"status": "error", "message": str(e)}
