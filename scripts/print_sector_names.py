# Script to print all valid sector names from DB only
from app.db import SessionLocal, Sector

print("--- Sectors in DB ---")
session = SessionLocal()
for s in session.query(Sector).all():
    print(s.sector_name)
session.close()
