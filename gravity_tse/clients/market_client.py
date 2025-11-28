"""Market client wrapper to expose market-related data functions in the package."""
from typing import Tuple, Optional
import pandas as pd
from gravity_tse.core.base_client import BaseSyncClient


class MarketClient(BaseSyncClient):
    """MarketClient provides high-level access to market-wide endpoints.

    Initially, it will wrap the existing `Get_MarketWatch` function from the
    `gravity_tse` module until we migrate the implementation into this class.
    """

    def get_market_watch(self, *args, **kwargs) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        # deferred import to avoid circular imports
        from gravity_tse import Get_MarketWatch

        return Get_MarketWatch(*args, **kwargs)
