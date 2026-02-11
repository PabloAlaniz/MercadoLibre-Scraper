"""Tests for utils.py helper functions"""
import pytest
import pandas as pd
import sys
import os
import importlib.util

# Load utils.py directly from file to bypass conftest mocks
utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils.py')
spec = importlib.util.spec_from_file_location("utils_real", utils_path)
utils_real = importlib.util.module_from_spec(spec)

# Mock the heavy dependencies that utils imports
from unittest.mock import MagicMock
sys.modules['config'] = MagicMock(socketio=MagicMock(), DATA_DIRECTORY='./data', CSV_SEPARATOR=',')
sys.modules['dash'] = MagicMock()

# Now load utils
spec.loader.exec_module(utils_real)

format_filename = utils_real.format_filename
format_price = utils_real.format_price
clean_km = utils_real.clean_km


class TestFormatFilename:
    """Tests for format_filename function"""

    def test_simple_name(self):
        """Test formatting a simple product name"""
        assert format_filename("Notebook Gamer") == "notebook-gamer"

    def test_multiple_spaces(self):
        """Test handling multiple spaces"""
        assert format_filename("Auto  Usado  2020") == "auto--usado--2020"

    def test_already_lowercase(self):
        """Test name that's already lowercase"""
        assert format_filename("laptop") == "laptop"

    def test_mixed_case(self):
        """Test mixed case conversion"""
        assert format_filename("iPhone PRO MAX") == "iphone-pro-max"

    def test_empty_string(self):
        """Test empty string input"""
        assert format_filename("") == ""


class TestFormatPrice:
    """Tests for format_price function"""

    def test_format_price_basic(self):
        """Test basic price formatting"""
        df = pd.DataFrame({"price": ["1.500", "2.000", "3.500"]})
        result = format_price(df)
        assert result["price"].tolist() == [1500.0, 2000.0, 3500.0]

    def test_format_price_with_decimals(self):
        """Test price formatting with decimal points"""
        df = pd.DataFrame({"price": ["1.500,50", "2.000,99"]})
        result = format_price(df)
        assert result["price"].tolist() == [1500.50, 2000.99]

    def test_format_price_missing_column(self):
        """Test that DataFrame without price column is returned unchanged"""
        df = pd.DataFrame({"name": ["Product A"]})
        result = format_price(df)
        assert "price" not in result.columns
        assert result.equals(df)

    def test_format_price_empty_dataframe(self):
        """Test with empty DataFrame"""
        df = pd.DataFrame({"price": []})
        result = format_price(df)
        assert len(result) == 0

    def test_format_price_large_numbers(self):
        """Test formatting large price values"""
        df = pd.DataFrame({"price": ["1.500.000", "250.000"]})
        result = format_price(df)
        assert result["price"].tolist() == [1500000.0, 250000.0]


class TestCleanKm:
    """Tests for clean_km function"""

    def test_clean_km_basic(self):
        """Test basic kilometer string parsing"""
        assert clean_km("50.000 km") == 50000

    @pytest.mark.xfail(reason="Bug: clean_km doesn't handle comma separators")
    def test_clean_km_with_comma(self):
        """Test kilometer string with comma separator"""
        assert clean_km("120,000 km") == 120000

    def test_clean_km_without_separator(self):
        """Test kilometer string without separator"""
        assert clean_km("15000 km") == 15000

    def test_clean_km_mixed_format(self):
        """Test various kilometer formats"""
        assert clean_km("100.500 km") == 100500
        assert clean_km("1.500 km") == 1500

    def test_clean_km_no_unit(self):
        """Test kilometer string without 'km' suffix"""
        assert clean_km("50000") == 50000

    def test_clean_km_zero(self):
        """Test zero kilometers"""
        assert clean_km("0 km") == 0

    def test_clean_km_with_spaces(self):
        """Test kilometer string with extra spaces"""
        assert clean_km("  50.000 km  ") == 50000
