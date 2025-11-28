import pytest
from gravity_tse.clients.market_client import MarketClient


def test_market_client_get_market_watch(monkeypatch):
    client = MarketClient()

    def fake_Get_MarketWatch(*args, **kwargs):
        import pandas as pd
        return pd.DataFrame({'A': [1]}), None

    monkeypatch.setattr('gravity_tse.Get_MarketWatch', fake_Get_MarketWatch)
    res, _ = client.get_market_watch()
    assert 'A' in res.columns
