import pytest
from gravity_tse.clients.index_client import IndexClient


def test_index_client_get_index_history(monkeypatch):
    client = IndexClient()

    def fake_GetIndexHistory(webid, *args, **kwargs):
        import pandas as pd
        return pd.DataFrame({'A': [42]})
    monkeypatch.setattr('gravity_tse.Get_SectorIndex_History', fake_GetIndexHistory)
    df = client.get_index_history('خودرو')
    assert df.loc[0, 'A'] == 42
