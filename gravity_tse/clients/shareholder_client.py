"""Shareholder client wrapper to expose shareholder information retrieval."""
from typing import Optional
import pandas as pd
from gravity_tse.core.base_client import BaseSyncClient


class ShareholderClient(BaseSyncClient):
    def get_shareholders_info(self, ticker: str) -> Optional[pd.DataFrame]:
        from gravity_tse import Get_ShareHoldersInfo
        return Get_ShareHoldersInfo(ticker)
