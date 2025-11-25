from app.db import SessionLocal, UsdIrrPrice
import requests
import pandas as pd

def fetch_usd_irr_history():
    # منبع داده: سایت می‌تواند تغییر کند. اینجا از سایت tgju.org استفاده می‌شود
    url = "https://api.tgju.org/v1/market/price-history/dollar_rl"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("[USD/IRR] Error fetching data from tgju.org")
        return
    data = resp.json().get('data', [])
    if not data:
        print("[USD/IRR] No data found in response.")
        return
    df = pd.DataFrame(data, columns=["date", "open", "high", "low", "close"])
    session = SessionLocal()
    count = 0
    for _, row in df.iterrows():
        price = UsdIrrPrice(
            date=row["date"],
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"])
        )
        session.merge(price)
        count += 1
    session.commit()
    session.close()
    print(f"[USD/IRR] Stored {count} USD/IRR price records.")

if __name__ == "__main__":
    fetch_usd_irr_history()
