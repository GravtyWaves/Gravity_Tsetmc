# Script to filter symbol_to_sector.json to only use sectors present in DB
import json
from app.db import SessionLocal, Sector

MAPPING_PATH = "BasicTseInformation/symbol_to_sector.json"
OUTPUT_PATH = "BasicTseInformation/symbol_to_sector_filtered.json"

def get_valid_sectors():
    session = SessionLocal()
    valid = set(s.sector_name for s in session.query(Sector).all())
    session.close()
    return valid

def main():
    with open(MAPPING_PATH, encoding="utf-8") as f:
        mapping = json.load(f)
    valid_sectors = get_valid_sectors()
    filtered = {k: v for k, v in mapping.items() if v in valid_sectors}
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"Filtered mapping: {len(filtered)} symbols (from {len(mapping)}) written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
