from gravity_tse import stock_client, StockClient


def test_stock_client_exported():
    assert isinstance(stock_client, StockClient)
