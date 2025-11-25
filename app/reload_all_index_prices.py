from app.db import SessionLocal, Index
from app.fetcher import fetch_and_store_index_prices

def reload_all_index_prices():
    session = SessionLocal()
    indices = session.query(Index).all()
    names = [idx.name for idx in indices]
    session.close()
    fetch_and_store_index_prices(names, adjust=False)

if __name__ == "__main__":
    reload_all_index_prices()
