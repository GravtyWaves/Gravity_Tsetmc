"""Stock client wrapper for TSE functions (initially wraps existing functions)."""
from typing import Optional
import pandas as pd
from gravity_tse import get_tse_webid, get_price_history
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
            df = get_tse_webid(symbol)
            return df
        except TSEConnectionError:
            return None

    def get_price_history(self, symbol: str, *args, **kwargs) -> pd.DataFrame:
        """Return historical price data for a symbol using existing helper."""
        return get_price_history(symbol, *args, **kwargs)
