import sqlite3

# نام دیتابیس خود را در اینجا وارد کنید
DB_PATH = 'tsetmc_data.db'

# نام جدول مورد نظر برای حذف
TABLE_NAME = 'subsectors'

def drop_table(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.commit()
        print(f"جدول {table_name} با موفقیت حذف شد.")
    except Exception as e:
        print(f"خطا در حذف جدول: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    drop_table(DB_PATH, TABLE_NAME)
