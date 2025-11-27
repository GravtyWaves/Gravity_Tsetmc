<<<<<<< HEAD
"""
USD/IRR Price Fetcher for Gravity TSETMC
Fetches and stores USD/IRR exchange rate data from TSETMC API.
"""

import logging
import pandas as pd
from datetime import datetime
import jdatetime
import requests

from gravity_tse import USDManager
from .db import SessionLocal, UsdIrrPrice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s: %(message)s'
)


def fetch_and_store_usd_irr_prices():
    """
    Fetch and store USD/IRR prices from TSETMC API.

    This function fetches historical USD/IRR exchange rate data
    and stores it in the database.
    """
    session = SessionLocal()

    print("[UsdIrrPrice] Fetching USD/IRR prices...", flush=True)

    try:
        # Get USD/IRR data from TSETMC API
        df = USDManager.get_usd_irr_prices()

        if not (isinstance(df, pd.DataFrame) and not df.empty):
            print("  [✗] No USD/IRR data available", flush=True)
            return

        count = 0
        for idx, row in df.iterrows():
            date_val = str(idx)
            if not date_val or pd.isnull(date_val):
                continue

=======
from gravity_tse import USDManager
from .db import SessionLocal, UsdIrrPrice
import pandas as pd

def fetch_and_store_usd_irr_prices():
    """Fetch and store USD/IRR historical prices"""
    session = SessionLocal()
    print("[UsdIrrPrice] Fetching USD/IRR prices...", flush=True)
    
    try:
        df = USDManager.fetch_usd_irr_history(ignore_date=True)
        
        if not isinstance(df, pd.DataFrame) or df.empty:
            print("[UsdIrrPrice] No data fetched for USD/IRR (placeholder implementation)", flush=True)
            session.close()
            return
        
        # Remove duplicate dates, keep the first occurrence
        df = df[~df.index.duplicated(keep='first')]
        
        count = 0
        # If J-Date is not the index, try to set it
        if df.index.name != 'J-Date':
            if 'J-Date' in df.columns:
                df = df.set_index('J-Date')
        
        # Remove duplicate dates again after setting index
        df = df[~df.index.duplicated(keep='first')]
        
        for idx, row in df.iterrows():
            date = str(idx)
            
>>>>>>> 5489f53c21f43bc57a9de23edc6ccf15f223d306
            # Normalize row keys
            row_dict = {}
            for k, v in row.items():
                k_normalized = str(k).lower().strip().replace(' ', '')
                row_dict[k_normalized] = v
<<<<<<< HEAD

            # Convert Jalali date to Gregorian
            try:
                jalali_date = date_val
                year, month, day = map(int, jalali_date.split('-'))
                gregorian_date = jdatetime.date(year, month, day).togregorian().strftime('%Y-%m-%d')
            except Exception:
                gregorian_date = None

            usd_kwargs = dict(
                date=date_val,
                gregorian_date=gregorian_date,
                buy_price=row_dict.get('buyprice') or row_dict.get('buy_price'),
                sell_price=row_dict.get('sellprice') or row_dict.get('sell_price'),
                open=row_dict.get('open'),
                high=row_dict.get('high'),
                low=row_dict.get('low'),
                close=row_dict.get('close'),
                source='TSETMC API'
            )

            # Only pass valid keys
            usd_irr_price = UsdIrrPrice(**{k: v for k, v in usd_kwargs.items() if k in UsdIrrPrice.__table__.columns.keys()})
            session.merge(usd_irr_price)
            count += 1

        session.commit()

        if count > 0:
            print(f"  [✓] Stored {count} USD/IRR records", flush=True)
        else:
            print("  [✗] No valid USD/IRR records stored", flush=True)

    except Exception as e:
        print(f"  [✗] Error fetching USD/IRR prices: {e}", flush=True)
        session.rollback()

    session.close()
    print("[UsdIrrPrice] Complete", flush=True)
=======
            
            price = UsdIrrPrice(
                date=date,
                open=row_dict.get('open'),
                high=row_dict.get('high'),
                low=row_dict.get('low'),
                close=row_dict.get('close')
            )
            session.merge(price)
            count += 1
        
        session.commit()
        print(f"[UsdIrrPrice] Stored {count} USD/IRR price records", flush=True)
        
    except Exception as e:
        print(f"[UsdIrrPrice] Error: {e}", flush=True)
        session.rollback()
    finally:
        session.close()
>>>>>>> 5489f53c21f43bc57a9de23edc6ccf15f223d306
