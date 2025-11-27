import sqlite3
import os

# مسیر دیتابیس را تعیین کنید
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, 'tsetmc_data.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# نام جدول و ستون‌هایی که باید حذف شوند
table = 'symbol_prices'
columns_to_remove = ['last', 'gregorian_date']

# گرفتن نام ستون‌های فعلی
cursor.execute(f"PRAGMA table_info({table})")
columns = [row[1] for row in cursor.fetchall()]

# ساخت جدول جدید بدون ستون‌های موردنظر
new_columns = [col for col in columns if col not in columns_to_remove]
columns_str = ', '.join(new_columns)

# ایجاد جدول موقت
cursor.execute(f"CREATE TABLE {table}_new AS SELECT {columns_str} FROM {table}")

# حذف جدول قدیمی و تغییر نام جدول جدید
cursor.execute(f"DROP TABLE {table}")
cursor.execute(f"ALTER TABLE {table}_new RENAME TO {table}")

conn.commit()
conn.close()
print('ستون‌های last و gregorian_date با موفقیت حذف شدند.')
