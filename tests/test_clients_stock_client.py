import pandas as pd
import pytest
from gravity_tse.clients.stock_client import StockClient


def make_sample_df():
    df = pd.DataFrame([['خودرو', 1234, 'auto name']], columns=['Name','WebID','NameSplit'])
    df.index = pd.MultiIndex.from_tuples([('خودرو', 1)])
    df.columns = ['Name','WebID','NameSplit']
    return df


def test_get_stock_info(monkeypatch):
    client = StockClient()
    sample = make_sample_df()

    monkeypatch.setattr('gravity_tse.get_tse_webid', lambda s: sample)
    result = client.get_stock_info('خودرو')
    assert result is not None


def test_get_price_history_calls_function(monkeypatch):
    client = StockClient()
    # monkeypatch the top-level helper to ensure it is used
    monkeypatch.setattr('gravity_tse.get_price_history', lambda *args, **kwargs: pd.DataFrame({'A':[1,2,3]}))
    df = client.get_price_history('خودرو')
    assert isinstance(df, pd.DataFrame)
