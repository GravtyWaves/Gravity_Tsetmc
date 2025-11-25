from app.db import SessionLocal, Sector
session = SessionLocal()
sectors = session.query(Sector.sector_name).all()
for s in sectors:
    print(repr(s[0]))
session.close()