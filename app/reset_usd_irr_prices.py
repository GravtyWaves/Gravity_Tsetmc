from app.db import reset_table, UsdIrrPrice
from app.usd_fetcher import fetch_and_store_usd_irr_prices

if __name__ == "__main__":
    print("[RESET] Dropping and recreating ONLY usd_irr_prices table (other tables are NOT affected)...")
    reset_table(UsdIrrPrice)
    print("[RESET] Table recreated. Reloading USD/IRR prices...")
    fetch_and_store_usd_irr_prices()
    print("[RESET] Done. ONLY usd_irr_prices is now clean and reloaded.")