import pytest
from gravity_tse.clients.shareholder_client import ShareholderClient


def test_shareholder_client_get_shareholders_info(monkeypatch):
    client = ShareholderClient()

    def fake_Get_ShareHoldersInfo(ticker):
        import pandas as pd
        return pd.DataFrame({'holderName': ['John'], 'shareholderShares':[100]})

    monkeypatch.setattr('gravity_tse.Get_ShareHoldersInfo', fake_Get_ShareHoldersInfo)
    df = client.get_shareholders_info('خودرو')
    assert len(df) == 1
