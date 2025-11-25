from app.db import SessionLocal, Index

def list_all_indices():
    session = SessionLocal()
    indices = session.query(Index).all()
    print(f"{'ID':<4} | {'Farsi Name':<30} | {'English Name':<30} | {'WebID':<20} | {'Type':<10}")
    print('-'*110)
    for idx in indices:
        print(f"{idx.id:<4} | {idx.name:<30} | {idx.description or '-':<30} | {idx.web_id or '-':<20} | {idx.type or '-':<10}")
    session.close()

if __name__ == "__main__":
    list_all_indices()
