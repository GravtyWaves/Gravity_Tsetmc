from app.db import reset_table, Index
from app.list_fetcher import fetch_and_store_index_list

if __name__ == "__main__":
    print("[RESET] Dropping and recreating ONLY indices table (other tables are NOT affected)...")
    reset_table(Index)
    print("[RESET] Table recreated. Reloading index list...")
    fetch_and_store_index_list()
    print("[RESET] Done. ONLY indices is now clean and reloaded.")