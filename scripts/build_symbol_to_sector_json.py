# Script to find symbols with missing sector, guess their sector, and write a JSON mapping
import json
import re

COMPANIES_PATH = "BasicTseInformation/companies.json"
OUTPUT_PATH = "BasicTseInformation/symbol_to_sector.json"

# Load companies
def load_companies():
    with open(COMPANIES_PATH, encoding="utf-8") as f:
        return json.load(f)

def guess_sector(company):
    # Simple heuristics based on name or ticker (customize as needed)
    name = company.get("Name", "")
    ticker = company.get("Ticker", "")
    # Example rules (expand as needed):
    if "بیمه" in name or "بیمه" in ticker:
        return "بیمه و بازنشستگی"
    if "بانک" in name or "بانک" in ticker:
        return "بانک"
    if "سرمایه گذاری" in name:
        return "سرمایه گذاری"
    if "دارو" in name or "دارویی" in name:
        return "دارویی"
    if "فلز" in name or "فلزی" in name:
        return "فلزات اساسی"
    if "شیمیایی" in name:
        return "شیمیایی"
    if "خودرو" in name or "خودرو" in ticker:
        return "خودرو"
    if "سیمان" in name:
        return "سیمان"
    if "غذایی" in name:
        return "غذایی"
    # Add more rules as needed
    return None

def main():
    companies = load_companies()
    mapping = {}
    for c in companies:
        if c.get("SectorID") is None:
            sector = guess_sector(c)
            if sector:
                mapping[c["Ticker"]] = sector
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(mapping)} symbol->sector mappings to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
