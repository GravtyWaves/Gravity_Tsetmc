"""
Central script for database table creation, initial data loading, and updating all tables.

This module provides functions to initialize the database, load initial data,
and update all market data including symbols, indices, and USD/IRR rates.
"""

from typing import List, Tuple

from gravity_tse import Get_ShareHoldersInfo

from .db import Base, engine, SessionLocal, SymbolList, Sector
from .fetcher import (
    fetch_and_store_symbol_prices,
    fetch_and_store_index_prices,
    fetch_and_store_industry_indices
)
from .list_fetcher import (
    fetch_and_store_market_list,
    fetch_and_store_panel_list,
    fetch_and_store_sector_list,
    fetch_and_store_symbol_list,
    fetch_and_store_index_list
)
from .usd_fetcher import fetch_and_store_usd_irr_prices


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    Creates all database tables defined in the SQLAlchemy models.
    """
    print("[INIT] Creating all database tables...")
    Base.metadata.create_all(engine)
    print("[INIT] All tables created.")


def load_initial_data() -> None:
    """
    Load initial data for all market structures.

    Fetches and stores initial data for markets, panels, sectors,
    symbols, and indices from JSON files.
    """
    print("[INIT] Loading initial market data...")
    fetch_and_store_market_list()
    print("[INIT] Loading initial panel data...")
    fetch_and_store_panel_list()
    print("[INIT] Loading initial sector data...")
    fetch_and_store_sector_list()
    print("[INIT] Loading initial symbol data...")
    fetch_and_store_symbol_list()
    print("[INIT] Loading initial index data...")
    fetch_and_store_index_list()
    print("[INIT] Initial data loaded for all tables.")


def update_all() -> None:
    """
    Update all market data including prices and shareholder information.

    Updates symbol prices, index prices, industry indices, USD/IRR rates,
    and shareholder information for all symbols.
    """
    print("[UPDATE] Updating symbol prices...")

    # Get symbol list from database
    session = SessionLocal()
    symbols: List[Tuple[str, str]] = session.query(SymbolList.symbol_fa, SymbolList.symbol_en).all()
    session.close()

    fetch_and_store_symbol_prices(symbols, adjust=True)

    print("[UPDATE] Updating main index prices...")
    indices = [
        "شاخص کل", "شاخص هم وزن", "شاخص قیمت (وزنی-ارزشی)", "شاخص قیمت (هم وزن)",
        "شاخص شناور آزاد", "شاخص بازار اول", "شاخص بازار دوم", "شاخص صنعت",
        "شاخص 30 شرکت بزرگ", "شاخص 50 شرکت فعالتر"
    ]
    fetch_and_store_index_prices(indices, adjust=True)

    print("[UPDATE] Updating industry index prices...")
    # Get industry list from database
    session = SessionLocal()
    industries_result = session.query(Sector.sector_name).all()
    session.close()
    industries: List[str] = [i[0] for i in industries_result]

    fetch_and_store_industry_indices(industries, adjust=True)

    print("[UPDATE] Updating USD/IRR prices...")
    fetch_and_store_usd_irr_prices()

    print("[UPDATE] Updating shareholder information for all symbols...")
    # Get symbol list and update shareholders
    session = SessionLocal()
    symbols_fa = session.query(SymbolList.symbol_fa).all()
    session.close()

    for symbol_tuple in symbols_fa:
        try:
            Get_ShareHoldersInfo(symbol_tuple[0])
        except Exception as e:
            print(f"[ERROR] Shareholder info for {symbol_tuple[0]}: {e}")

    print("[UPDATE] All tables updated successfully.")


if __name__ == "__main__":
    init_db()
    load_initial_data()
    update_all()
