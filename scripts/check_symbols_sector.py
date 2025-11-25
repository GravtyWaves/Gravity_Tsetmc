# Script to check if all symbols have a sector assigned
from app.db import SessionLocal, SymbolList

session = SessionLocal()
no_sector = session.query(SymbolList).filter(SymbolList.sector_id == None).all()
if not no_sector:
    print('تمام نمادها sector دارند.')
else:
    print(f'{len(no_sector)} نماد بدون sector:')
    for s in no_sector:
        print(s.symbol_fa)
session.close()
