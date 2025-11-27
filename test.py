import json
import os

# مسیر کامل فایل
file_path = 'E:/Shakour/GravityProjects/Gravity_Tsetmc/BasicTseInformation/companies.json'

# یا اگر فایل در پوشه فعلی است:
# file_path = './companies.json'

# خواندن فایل JSON
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# حذف فیلدهای SectorID و SubSectorID از هر آیتم
for item in data:
    item.pop('SectorID', None)
    item.pop('SubSectorID', None)

# ذخیره فایل با داده‌های به‌روز شده
output_path = 'E:/Shakour/GravityProjects/Gravity_Tsetmc/BasicTseInformation/companies.json'
with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("فیلدهای SectorID و SubSectorID با موفقیت حذف شدند.")
print(f"فایل به‌روز شده در: {output_path} ذخیره شد.")