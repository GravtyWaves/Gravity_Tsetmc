import json
import os

# پیدا کردن فایل در پوشه فعلی
current_dir = os.getcwd()
file_name = r'BasicTseInformation\companies.json'
file_path = os.path.join(current_dir, file_name)

# بررسی وجود فایل
if not os.path.exists(file_path):
    print(f"فایل {file_name} در مسیر {current_dir} یافت نشد.")
    print("فایل‌های موجود در پوشه:")
    for f in os.listdir(current_dir):
        print(f"  - {f}")
else:
    # خواندن فایل JSON
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # حذف فیلدهای SectorID و SubSectorID از هر آیتم
    for item in data:
        item.pop('SectorID', None)
        item.pop('SubSectorID', None)

    # ذخیره فایل با داده‌های به‌روز شده
    output_path = os.path.join(current_dir, 'companies_updated.json')
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("فیلدهای SectorID و SubSectorID با موفقیت حذف شدند.")
    print(f"فایل به‌روز شده در: {output_path} ذخیره شد.")