import sqlite3

DB_PATH = 'app/tsetmc_data.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# استخراج لیست جداول
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables:')
for t in tables:
    print(t[0])

# استخراج ستون‌های هر جدول
for t in tables:
    print(f'Columns in table {t[0]}:')
    cursor.execute(f'PRAGMA table_info({t[0]});')
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]} ({col[2]})')

conn.close()
