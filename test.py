import sqlite3
conn = sqlite3.connect('tsetmc_data.db')  # نام دیتابیس را درست وارد کن
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
conn.close()