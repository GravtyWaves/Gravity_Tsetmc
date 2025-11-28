"""Index client wrapper for index-related endpoints."""
from typing import Optional
import pandas as pd
from gravity_tse.core.base_client import BaseSyncClient


class IndexClient(BaseSyncClient):
    def get_index_history(self, sector: str = 'خودرو', *args, **kwargs) -> Optional[pd.DataFrame]:
        # the underlying legacy function in the module
        from gravity_tse import Get_SectorIndex_History

        return Get_SectorIndex_History(sector, *args, **kwargs)
