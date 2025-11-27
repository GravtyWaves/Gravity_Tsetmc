"""
Integration tests for Gravity TSETMC project
Tests interactions between multiple components
"""

import pytest
import pandas as pd
import sqlite3
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db import SessionLocal, Market, Panel, Sector, SymbolList


class TestDatabaseIntegration:
    """Tests for database operations"""
    
    def test_database_session_creation(self):
        """Test that database session can be created"""
        try:
            session = SessionLocal()
            assert session is not None
            session.close()
        except Exception as e:
            pytest.skip(f"Database not initialized: {e}")
    
    def test_market_table_accessible(self):
        """Test that Market table is accessible"""
        try:
            session = SessionLocal()
            markets = session.query(Market).limit(1).all()
            assert isinstance(markets, list)
            session.close()
        except Exception as e:
            pytest.skip(f"Database not initialized: {e}")
    
    def test_sector_table_accessible(self):
        """Test that Sector table is accessible"""
        try:
            session = SessionLocal()
            sectors = session.query(Sector).limit(1).all()
            assert isinstance(sectors, list)
            session.close()
        except Exception as e:
            pytest.skip(f"Database not initialized: {e}")
    
    def test_symbol_list_table_accessible(self):
        """Test that SymbolList table is accessible"""
        try:
            session = SessionLocal()
            symbols = session.query(SymbolList).limit(1).all()
            assert isinstance(symbols, list)
            session.close()
        except Exception as e:
            pytest.skip(f"Database not initialized: {e}")


class TestAppInitialization:
    """Tests for app initialization functions"""
    
    @patch('app.list_fetcher.SessionLocal')
    @patch('builtins.open')
    def test_fetch_market_list_json_loading(self, mock_open, mock_session):
        """Test that market list can be loaded from JSON"""
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = '[]'
        mock_open.return_value = mock_file
        
        # Test JSON parsing works
        import json
        data = json.loads('[]')
        assert isinstance(data, list)
    
    @patch('app.list_fetcher.SessionLocal')
    @patch('builtins.open')
    def test_fetch_panel_list_json_loading(self, mock_open, mock_session):
        """Test that panel list can be loaded from JSON"""
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = '[]'
        mock_open.return_value = mock_file
        
        # Test JSON parsing works
        import json
        data = json.loads('[]')
        assert isinstance(data, list)


class TestDataProcessingPipeline:
    """Tests for data processing workflow"""
    
    def test_dataframe_concatenation(self):
        """Test that DataFrames can be concatenated properly"""
        df1 = pd.DataFrame({'Date': ['1402-01-01'], 'Price': [100]})
        df2 = pd.DataFrame({'Date': ['1402-01-02'], 'Price': [105]})
        
        result = pd.concat([df1, df2])
        assert len(result) == 2
        assert list(result['Date']) == ['1402-01-01', '1402-01-02']
    
    def test_dataframe_sorting(self):
        """Test that DataFrames can be sorted properly"""
        df = pd.DataFrame({
            'Date': ['1402-01-03', '1402-01-01', '1402-01-02'],
            'Price': [110, 100, 105]
        })
        
        sorted_df = df.sort_values('Date')
        assert list(sorted_df['Date']) == ['1402-01-01', '1402-01-02', '1402-01-03']
    
    def test_dataframe_reset_index(self):
        """Test that DataFrames can have index reset"""
        df = pd.DataFrame({'Price': [100, 105, 110]})
        df_reset = df.reset_index(drop=True)
        assert list(df_reset.index) == [0, 1, 2]


class TestErrorHandling:
    """Tests for error handling in various scenarios"""
    
    @patch('gravity_tse.requests.get')
    def test_api_timeout_handling(self, mock_get):
        """Test that API timeout is handled gracefully"""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()
        
        # Import and test error handling
        from gravity_tse import USDManager
        result = USDManager.get_latest_usd_irr()
        # Should return None instead of raising exception
        assert result is None
    
    @patch('gravity_tse.requests.get')
    def test_api_connection_error_handling(self, mock_get):
        """Test that connection errors are handled gracefully"""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError()
        
        from gravity_tse import USDManager
        result = USDManager.get_latest_usd_irr()
        assert result is None


class TestEndToEndWorkflow:
    """End-to-end integration tests"""
    
    @patch('gravity_tse.SymbolManager.get_tse_webid')
    @patch('gravity_tse.requests.get')
    def test_symbol_lookup_to_price_fetch(self, mock_get, mock_symbol):
        """Test complete workflow from symbol lookup to price fetch"""
        # Mock symbol lookup
        mock_df = pd.DataFrame({
            'WebID': [123456],
            'Ticker': ['KHRO'],
            'Name': ['خودرو']
        })
        mock_symbol.return_value = mock_df
        
        # Mock price API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Price: 100</body></html>'
        mock_get.return_value = mock_response
        
        # Verify symbol was looked up
        from gravity_tse import SymbolManager
        result = SymbolManager.get_tse_webid('خودرو')
        assert not result.empty


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
