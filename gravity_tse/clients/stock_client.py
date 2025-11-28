"""Stock client wrapper for TSE functions (initially wraps existing functions)."""
from typing import Optional
import pandas as pd
from gravity_tse.core.base_client import BaseSyncClient
from gravity_tse.core.exceptions import TSEConnectionError


class StockClient(BaseSyncClient):
    """StockClient provides high-level methods to access stock data.

    At first, StockClient will wrap existing module-level helper
    functions (`get_tse_webid`, `get_price_history`) to minimize
    changes. Later we can migrate internal logic into class methods.
    """

    def get_stock_info(self, symbol: str) -> Optional[pd.DataFrame]:
        """Return search results for symbol using existing get_tse_webid wrapper."""
        try:
            # deferred import to avoid circular dependency at module import time
            from gravity_tse import get_tse_webid

            df = get_tse_webid(symbol)
            return df
        except TSEConnectionError:
            return None

    def get_price_history(self, symbol: str, *args, **kwargs) -> pd.DataFrame:
        """Return historical price data for a symbol using existing helper."""
        # The orchestrating method will delegate to the module-level
        # helper for backwards compatibility unless the internal
        # methods are migrated. If called, use the internal
        # implementation if available.
        if hasattr(self, '_get_price_history_impl'):
            return self._get_price_history_impl(symbol, *args, **kwargs)
        from gravity_tse import get_price_history
        return get_price_history(symbol, *args, **kwargs)

    def _get_price_data(self, ticker_no: int, ticker: str, name: str, market: str) -> pd.DataFrame:
        """Fetch a single-symbol price history and return a DataFrame."""
        url = f'https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{ticker_no}/0'
        try:
            resp = self._make_request(url)
            data = resp.json().get('closingPriceDaily', [])
        except Exception:
            return pd.DataFrame(columns=['Date','High','Low','Final','Close','Open','Y-Final','Value','Volume','No','Ticker','Name','Market'])

        if not data:
            return pd.DataFrame(columns=['Date','High','Low','Final','Close','Open','Y-Final','Value','Volume','No','Ticker','Name','Market'])

        df_history = pd.DataFrame(data)
        df_history = df_history[['dEven','priceMax','priceMin','pClosing','pDrCotVal','priceFirst','priceYesterday','qTotCap','qTotTran5J','zTotTran']]
        df_history.columns = ['Date','High','Low','Final','Close','Open','Y-Final','Value','Volume','No']
        df_history['Date'] = df_history['Date'].astype(str).apply(lambda x: f'{x[:4]}-{x[4:6]}-{x[-2:]}')
        df_history['Date'] = pd.to_datetime(df_history['Date'])
        df_history = df_history[df_history['No'] != 0]
        df_history['Ticker'] = ticker
        df_history['Name'] = name
        df_history['Market'] = market
        df_history = df_history.set_index('Date')
        return df_history

    def _get_price_history_impl(self, stock: str, start_date: str = '1400-01-01', end_date: str = '1401-01-01', ignore_date: bool = False,
                                 adjust_price: bool = False, show_weekday: bool = False, double_date: bool = False) -> pd.DataFrame:
        """Implementation for get_price_history directly in the client."""
        # Validate dates if needed
        if not ignore_date:
            # Minimal validation; reuse top-level helper for now
            start_date = start_date
            end_date = end_date

        # get WebIDs
        from gravity_tse import get_tse_webid
        webid_df = get_tse_webid(stock)
        if type(webid_df) == bool:
            return pd.DataFrame()

        # loop to get data
        df_history = pd.DataFrame(columns=['Date','High','Low','Final','Close','Open','Y-Final','Value','Volume','No','Ticker','Name','Market']).set_index('Date')
        for index, row in (webid_df.reset_index()).iterrows():
            try:
                df_temp = self._get_price_data(ticker_no=row['WebID'], ticker=row['Ticker'], name=row['Name'], market=row['Market'])
                df_history = pd.concat([df_history, df_temp])
            except Exception:
                pass

        # Post-process as in legacy function
        if df_history.empty:
            return df_history
        df_history = df_history.sort_index(ascending=True)
        df_history = df_history.reset_index()
        df_history['Weekday'] = df_history['Date'].dt.weekday
        df_history['Weekday'] = df_history['Weekday'].apply(lambda x: '')
        df_history['J-Date'] = df_history['Date'].apply(lambda x: str(pd.Timestamp(x).date()))
        df_history = df_history.set_index('J-Date')
        if not show_weekday:
            df_history.drop(columns=['Weekday'], inplace=True)
        if not double_date:
            df_history.drop(columns=['Date'], inplace=True)
        if not ignore_date:
            df_history = df_history[start_date:end_date]
        return df_history
