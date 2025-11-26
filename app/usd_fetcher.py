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
            
            # Normalize row keys
            row_dict = {}
            for k, v in row.items():
                k_normalized = str(k).lower().strip().replace(' ', '')
                row_dict[k_normalized] = v
            
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
