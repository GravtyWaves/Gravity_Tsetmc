import json

# Load the JSON file
with open('BasicTseInformation/companies.json', 'r', encoding='utf-8') as f:
    companies = json.load(f)

# Remove duplicates based on CompanyCode
seen = set()
unique_companies = []
for company in companies:
    code = company.get('CompanyCode')
    if code not in seen:
        seen.add(code)
        unique_companies.append(company)

# Save the deduplicated list back to the file
with open('BasicTseInformation/companies.json', 'w', encoding='utf-8') as f:
    json.dump(unique_companies, f, ensure_ascii=False, indent=4)

print(f"Removed {len(companies) - len(unique_companies)} duplicates. Total unique companies: {len(unique_companies)}")
