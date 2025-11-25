from app.db import reset_table, SymbolPrice, SessionLocal, SymbolList
from app.fetcher import fetch_and_store_symbol_prices

if __name__ == "__main__":
    print("[RESET] Dropping and recreating ONLY symbol_prices table (other tables are NOT affected)...")
    reset_table(SymbolPrice)
    print("[RESET] Table recreated. Reloading symbol prices for all symbols in DB...")
    session = SessionLocal()
    symbols = [(row.symbol_fa, row.symbol_en) for row in session.query(SymbolList).all()]
    session.close()
    fetch_and_store_symbol_prices(symbols, adjust=True)
    print("[RESET] Done. ONLY symbol_prices is now clean and reloaded.")