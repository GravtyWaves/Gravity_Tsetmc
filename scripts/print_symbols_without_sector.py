# Script to print names and tickers of all symbols without sector for manual/AI review
from app.db import SessionLocal, SymbolList

session = SessionLocal()
symbols = session.query(SymbolList).filter(SymbolList.sector_id == None).all()
for s in symbols:
    print(f"{s.symbol_fa}\t{s.name}")
session.close()
