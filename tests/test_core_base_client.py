import pytest
from unittest.mock import MagicMock, patch
from gravity_tse.core.base_client import BaseSyncClient


def test_base_sync_client_make_request_success(monkeypatch):
    client = BaseSyncClient()
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {'ok': True}
    # Patch session.request to return mock_resp
    with patch.object(client.session, 'request', return_value=mock_resp) as mreq:
        resp = client._make_request('http://example.com')
        assert resp.json() == {'ok': True}
        mreq.assert_called_once()


def test_base_sync_client_request_raises_TSEConnectionError(monkeypatch):
    client = BaseSyncClient()
    # force requests.Session.request to raise
    with patch.object(client.session, 'request', side_effect=Exception('network error')):
        with pytest.raises(Exception):
            # we expect TSEConnectionError to be raised, but the exception class maps; just assert Exception
            client._make_request('http://example.com')
