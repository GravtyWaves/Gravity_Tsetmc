from db import reset_only_usd_and_index_tables, SessionLocal, Index
from usd_fetcher import fetch_and_store_usd_irr_prices
from fetcher import fetch_and_store_index_prices

if __name__ == "__main__":
    print("[RESET] Dropping and recreating ONLY usd_irr_prices and index_prices tables (other tables are NOT affected)...")
    reset_only_usd_and_index_tables()
    print("[RESET] Tables recreated. Reloading USD/IRR prices...")
    fetch_and_store_usd_irr_prices()
    print("[RESET] Reloading index prices for all indices in DB...")
    session = SessionLocal()
    indices = [row.name for row in session.query(Index).all()]
    session.close()
    fetch_and_store_index_prices(indices, adjust=True)
    print("[RESET] Done. ONLY usd_irr_prices and index_prices are now clean and reloaded.")