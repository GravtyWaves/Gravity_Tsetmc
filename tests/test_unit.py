"""
Unit tests for gravity_tse module
Tests individual functions and classes for correctness
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gravity_tse import (
    SymbolManager,
    PriceHistoryManager,
    USDManager,
    Get_RI_History,
    Get_ShareHoldersInfo,
    get_sector_webid_map,
    get_all_indices
)


class TestSectorWebidMap:
    """Tests for sector WebID mapping"""
    
    def test_get_sector_webid_map_returns_dict(self):
        """Test that sector WebID map is a dictionary"""
        sector_map = get_sector_webid_map()
        assert isinstance(sector_map, dict)
    
    def test_get_sector_webid_map_not_empty(self):
        """Test that sector WebID map is not empty"""
        sector_map = get_sector_webid_map()
        assert len(sector_map) > 0
    
    def test_get_sector_webid_map_has_common_sectors(self):
        """Test that common sectors exist in the map"""
        sector_map = get_sector_webid_map()
        expected_sectors = ['زراعت', 'بانک', 'فنی مهندسی']
        for sector in expected_sectors:
            assert sector in sector_map
    
    def test_get_sector_webid_map_values_are_numbers(self):
        """Test that all WebID values are numeric"""
        sector_map = get_sector_webid_map()
        for name, webid in sector_map.items():
            assert isinstance(webid, (int, float))


class TestIndices:
    """Tests for index information"""
    
    def test_get_all_indices_returns_list(self):
        """Test that all indices function returns a list"""
        indices = get_all_indices()
        assert isinstance(indices, list)
    
    def test_get_all_indices_has_required_keys(self):
        """Test that each index dict has required keys"""
        indices = get_all_indices()
        for idx in indices:
            assert 'name' in idx
            assert 'web_id' in idx
            assert 'type' in idx


class TestSymbolManager:
    """Tests for SymbolManager class"""
    
    @patch('gravity_tse.requests.get')
    def test_get_tse_webid_with_valid_symbol(self, mock_get):
        """Test get_tse_webid with a valid symbol"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<div>Symbol data</div>'
        mock_get.return_value = mock_response
        
        # Test - may return empty if MarketWatch parsing has issues
        result = SymbolManager.get_tse_webid('خودرو')
        assert isinstance(result, pd.DataFrame)
    
    @patch('gravity_tse.requests.get')
    def test_get_tse_webid_with_invalid_symbol(self, mock_get):
        """Test get_tse_webid with an invalid symbol"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = SymbolManager.get_tse_webid('INVALID_SYMBOL_XXXXXX')
        # Should return None or empty DataFrame on failure
        assert result is None or (isinstance(result, pd.DataFrame) and result.empty)


class TestUSDManager:
    """Tests for USD/IRR exchange rate manager"""
    
    @patch('gravity_tse.requests.get')
    def test_get_usd_irr_prices_valid_response(self, mock_get):
        """Test get_usd_irr_prices with valid API response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'created_at': {'timestamp': 1700000000},
                    'price': 42500
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = USDManager.get_usd_irr_prices()
        assert isinstance(result, pd.DataFrame)
    
    @patch('gravity_tse.requests.get')
    def test_get_usd_irr_prices_empty_response(self, mock_get):
        """Test get_usd_irr_prices with empty API response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        result = USDManager.get_usd_irr_prices()
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    @patch('gravity_tse.requests.get')
    def test_get_latest_usd_irr_valid_response(self, mock_get):
        """Test get_latest_usd_irr with valid API response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'created_at': {'timestamp': 1700000000},
                    'price': 42500
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = USDManager.get_latest_usd_irr()
        assert result is not None
        assert isinstance(result, dict)
        assert 'date' in result
        assert 'price' in result
    
    @patch('gravity_tse.requests.get')
    def test_get_latest_usd_irr_error_response(self, mock_get):
        """Test get_latest_usd_irr with error response"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = USDManager.get_latest_usd_irr()
        assert result is None


class TestRIHistory:
    """Tests for Real/Institutional history"""
    
    @patch('gravity_tse.SymbolManager.get_tse_webid')
    @patch('gravity_tse.requests.get')
    def test_get_ri_history_valid_symbol(self, mock_get, mock_symbol):
        """Test get_ri_history with valid symbol"""
        # Mock symbol lookup
        mock_df = pd.DataFrame({
            'WebID': [123456],
            'Ticker': ['KHRO'],
            'Name': ['خودرو']
        })
        mock_symbol.return_value = mock_df
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ridata': [
                {
                    'dEven': '1402-08-15',
                    'nBuyI': 100,
                    'nSellI': 50,
                    'vBuyI': 10000,
                    'vSellI': 5000,
                    'qBuyI': 500000,
                    'qSellI': 250000,
                    'nBuyL': 20,
                    'nSellL': 15,
                    'vBuyL': 50000,
                    'vSellL': 30000,
                    'qBuyL': 2000000,
                    'qSellL': 1200000
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = Get_RI_History.get_ri_history('خودرو')
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
    
    @patch('gravity_tse.SymbolManager.get_tse_webid')
    def test_get_ri_history_invalid_symbol(self, mock_symbol):
        """Test get_ri_history with invalid symbol"""
        mock_symbol.return_value = pd.DataFrame()
        
        result = Get_RI_History.get_ri_history('INVALID_SYMBOL')
        assert isinstance(result, pd.DataFrame)
        assert result.empty


class TestShareholdersInfo:
    """Tests for shareholders information"""
    
    @patch('gravity_tse.SymbolManager.get_tse_webid')
    @patch('gravity_tse.requests.get')
    def test_get_shareholders_info_valid_symbol(self, mock_get, mock_symbol):
        """Test get_shareholders_info with valid symbol"""
        # Mock symbol lookup
        mock_df = pd.DataFrame({
            'WebID': [123456],
            'Ticker': ['KHRO'],
            'Name': ['خودرو']
        })
        mock_symbol.return_value = mock_df
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'shareholder': [
                {
                    'dEven': '1402-08-15',
                    'lName': 'Company A',
                    'cEPS': 1000000,
                    'per': 25.5,
                    'sGoal': 'Institution',
                    'cIsin': '123456789',
                    'perChange': 1.5
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = Get_ShareHoldersInfo.get_shareholders_info('خودرو')
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
    
    @patch('gravity_tse.SymbolManager.get_tse_webid')
    def test_get_shareholders_info_invalid_symbol(self, mock_symbol):
        """Test get_shareholders_info with invalid symbol"""
        mock_symbol.return_value = pd.DataFrame()
        
        result = Get_ShareHoldersInfo.get_shareholders_info('INVALID_SYMBOL')
        assert isinstance(result, pd.DataFrame)
        assert result.empty


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
