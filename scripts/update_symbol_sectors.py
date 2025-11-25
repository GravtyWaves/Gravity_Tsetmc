# Script to update sector_id for symbols in DB using symbol_to_sector.json
import json
from app.db import SessionLocal, SymbolList, Sector

MAPPING_PATH = "BasicTseInformation/symbol_to_sector.json"

# Map sector name to sector_id from DB
def get_sector_name_to_id():
    session = SessionLocal()
    mapping = {}
    for sector in session.query(Sector).all():
        mapping[sector.sector_name] = sector.sector_id
    session.close()
    return mapping

def main():
    with open(MAPPING_PATH, encoding="utf-8") as f:
        symbol_to_sector = json.load(f)
    sector_name_to_id = get_sector_name_to_id()
    session = SessionLocal()
    updated = 0
    for symbol, sector_name in symbol_to_sector.items():
        sector_id = sector_name_to_id.get(sector_name)
        if not sector_id:
            print(f"[WARN] No sector_id for sector '{sector_name}' (symbol: {symbol})")
            continue
        q = session.query(SymbolList).filter(SymbolList.symbol_fa == symbol)
        for sym in q:
            if sym.sector_id != sector_id:
                sym.sector_id = sector_id
                updated += 1
    session.commit()
    session.close()
    print(f"Updated {updated} symbols with sector_id.")

if __name__ == "__main__":
    main()
