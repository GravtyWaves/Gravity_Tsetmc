from app.db import SessionLocal, Index, IndexPrice

def check_indices_and_prices():
    session = SessionLocal()
    indices = session.query(Index).all()
    print(f"{'ID':<4} | {'Name':<30} | {'Type':<10} | {'WebID':<20} | {'Has Prices?':<12} | {'Price Count':<12}")
    print('-'*100)
    for idx in indices:
        price_count = session.query(IndexPrice).filter_by(index_id=idx.id).count()
        has_prices = 'Yes' if price_count > 0 else 'No'
        print(f"{idx.id:<4} | {idx.name:<30} | {idx.type or '-':<10} | {idx.web_id or '-':<20} | {has_prices:<12} | {price_count:<12}")
    session.close()

if __name__ == "__main__":
    check_indices_and_prices()
