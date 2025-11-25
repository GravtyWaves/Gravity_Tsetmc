from app.db import reset_table, IndexPrice, SessionLocal, Index
from app.fetcher import fetch_and_store_index_prices

if __name__ == "__main__":
    print("[RESET] Dropping and recreating ONLY index_prices table (other tables are NOT affected)...")
    reset_table(IndexPrice)
    print("[RESET] Table recreated. Reloading index prices for all indices in DB...")
    session = SessionLocal()
    indices = [row.name for row in session.query(Index).all()]
    session.close()
    fetch_and_store_index_prices(indices, adjust=True)
    print("[RESET] Done. ONLY index_prices is now clean and reloaded.")