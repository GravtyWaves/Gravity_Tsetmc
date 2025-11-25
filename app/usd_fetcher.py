from finpy_tse import Get_USD_RIAL
from .db import SessionLocal, UsdIrrPrice
import pandas as pd

def fetch_and_store_usd_irr_prices():
    session = SessionLocal()
    print("[UsdIrrPrice] Fetching USD/IRR prices...", flush=True)
    df = Get_USD_RIAL(ignore_date=True)
    if isinstance(df, pd.DataFrame):
        # Remove duplicate dates, keep the first occurrence
        df = df[~df.index.duplicated(keep='first')]
        count = 0
        # If J-Date is not the index, try to set it
        if df.index.name != 'J-Date':
            if 'J-Date' in df.columns:
                df = df.set_index('J-Date')
        # Remove duplicate dates again after setting index, just in case
        df = df[~df.index.duplicated(keep='first')]
        for idx, row in df.iterrows():
            date = idx  # Use J-Date as the date
            price = UsdIrrPrice(
                date=date,
                open=row.get('Open') or row.get('بازگشایی') or row.get('open'),
                high=row.get('High') or row.get('بیشترین') or row.get('high'),
                low=row.get('Low') or row.get('کمترین') or row.get('low'),
                close=row.get('Close') or row.get('پایانی') or row.get('close')
            )
            session.merge(price)
            count += 1
        print(f"[UsdIrrPrice] Stored {count} USD/IRR price records", flush=True)
    else:
        print("[UsdIrrPrice] No data fetched for USD/IRR", flush=True)
    session.commit()
    session.close()
    print("[UsdIrrPrice] USD/IRR prices stored.", flush=True)
