import sqlite3
import jdatetime

def jalali_to_gregorian(jalali_date_str):
    """
    Converts Jalali date string (e.g. '1400-01-01') to Gregorian date string ('2021-03-21').
    """
    try:
        year, month, day = map(int, jalali_date_str.split('-'))
        g_date = jdatetime.date(year, month, day).togregorian()
        return g_date.strftime('%Y-%m-%d')
    except Exception:
        return None

# Path to your SQLite DB
DB_PATH = 'app/tsetmc_data.db'
TABLE = 'symbol_prices'
JALALI_COL = 'jdate'  # Change if your column name is different
GREGORIAN_COL = 'gregorian_date'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Add column if not exists
try:
    cursor.execute(f"ALTER TABLE {TABLE} ADD COLUMN {GREGORIAN_COL} TEXT;")
except sqlite3.OperationalError:
    pass  # Column already exists

# 2. Read all rows with Jalali date
cursor.execute(f"SELECT rowid, {JALALI_COL} FROM {TABLE}")
rows = cursor.fetchall()

# 3. Update each row with Gregorian date
for rowid, jalali_date in rows:
    if jalali_date:
        gregorian_date = jalali_to_gregorian(jalali_date)
        if gregorian_date:
            cursor.execute(f"UPDATE {TABLE} SET {GREGORIAN_COL} = ? WHERE rowid = ?", (gregorian_date, rowid))

conn.commit()
conn.close()
print('gregorian_date column added and populated.')
