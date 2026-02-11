"""
Tests for utility functions.
"""
import pytest


class TestFormatFilename:
    """Tests for format_filename function."""
    
    def test_simple_name(self):
        """Should replace spaces with hyphens and lowercase."""
        from utils import format_filename
        
        result = format_filename("Notebook Gamer")
        assert result == "notebook-gamer"
    
    def test_multiple_spaces(self):
        """Should handle multiple consecutive spaces."""
        from utils import format_filename
        
        result = format_filename("iPhone  15  Pro")
        assert result == "iphone--15--pro"
    
    def test_already_lowercase(self):
        """Should work with already lowercase names."""
        from utils import format_filename
        
        result = format_filename("notebook gamer")
        assert result == "notebook-gamer"
    
    def test_mixed_case(self):
        """Should convert mixed case to lowercase."""
        from utils import format_filename
        
        result = format_filename("Samsung Galaxy S24")
        assert result == "samsung-galaxy-s24"
    
    def test_empty_string(self):
        """Should handle empty string."""
        from utils import format_filename
        
        result = format_filename("")
        assert result == ""


class TestCleanKm:
    """Tests for clean_km function."""
    
    def test_clean_km_basic(self):
        """Should clean standard km format."""
        from utils import clean_km
        
        result = clean_km("50.000 km")
        assert result == 50000
    
    def test_clean_km_without_separator(self):
        """Should clean km without thousand separator."""
        from utils import clean_km
        
        result = clean_km("50000 km")
        assert result == 50000
    
    def test_clean_km_mixed_format(self):
        """Should clean km with multiple dots."""
        from utils import clean_km
        
        result = clean_km("123.456 km")
        assert result == 123456
    
    def test_clean_km_zero(self):
        """Should handle zero km."""
        from utils import clean_km
        
        result = clean_km("0 km")
        assert result == 0


class TestFormatPriceForDisplay:
    """Tests for format_price_for_display function."""
    
    def test_format_price_for_display_basic(self):
        """Should format price for Argentine display."""
        from utils import format_price_for_display
        
        result = format_price_for_display(150000)
        assert result == "$150.000,00"
    
    def test_format_price_for_display_large_number(self):
        """Should format large prices correctly."""
        from utils import format_price_for_display
        
        result = format_price_for_display(1500000)
        assert result == "$1.500.000,00"
    
    def test_format_price_for_display_from_string(self):
        """Should handle string input."""
        from utils import format_price_for_display
        
        result = format_price_for_display("250000")
        assert result == "$250.000,00"
    
    def test_format_price_for_display_invalid_value(self):
        """Should return input unchanged for invalid values."""
        from utils import format_price_for_display
        
        result = format_price_for_display("invalid")
        assert result == "invalid"
    
    def test_format_price_for_display_zero(self):
        """Should format zero correctly."""
        from utils import format_price_for_display
        
        result = format_price_for_display(0)
        assert result == "$0,00"


class TestLinkFormatting:
    """Tests for link formatting functions."""
    
    def test_format_link_to_markdown(self):
        """Should convert URL to markdown link."""
        from utils import format_link_to_markdown
        
        result = format_link_to_markdown("https://example.com/product")
        assert result == "[Link](https://example.com/product)"
    
    def test_extract_url_from_markdown_basic(self):
        """Should extract URL from markdown link."""
        from utils import extract_url_from_markdown
        
        result = extract_url_from_markdown("[Link](https://example.com/product)")
        assert result == "https://example.com/product"
    
    def test_extract_url_from_markdown_different_text(self):
        """Should extract URL regardless of link text."""
        from utils import extract_url_from_markdown
        
        result = extract_url_from_markdown("[View Product](https://test.com)")
        assert result == "https://test.com"
    
    def test_extract_url_from_markdown_invalid_format(self):
        """Should return None for invalid markdown."""
        from utils import extract_url_from_markdown
        
        result = extract_url_from_markdown("https://test.com")
        assert result is None
    
    def test_extract_url_from_markdown_empty_url(self):
        """Should handle empty URL in brackets."""
        from utils import extract_url_from_markdown
        
        result = extract_url_from_markdown("[Text]()")
        assert result == ""


class TestGetLatestCsv:
    """Tests for get_latest_csv function."""
    
    def test_get_latest_csv_returns_filename(self, tmp_path):
        """Should return latest CSV filename without suffix."""
        from utils import get_latest_csv
        import time
        
        # Create test CSV files
        csv1 = tmp_path / "product1_scraped_data_detailed.csv"
        csv1.touch()
        time.sleep(0.01)  # Ensure different timestamps
        
        csv2 = tmp_path / "product2_scraped_data_detailed.csv"
        csv2.touch()
        
        result = get_latest_csv(str(tmp_path))
        assert result == "product2"
    
    def test_get_latest_csv_empty_directory(self, tmp_path):
        """Should return None when no CSV files exist."""
        from utils import get_latest_csv
        
        result = get_latest_csv(str(tmp_path))
        assert result is None
    
    def test_get_latest_csv_single_file(self, tmp_path):
        """Should return single CSV filename."""
        from utils import get_latest_csv
        
        csv = tmp_path / "notebook-gamer_scraped_data_detailed.csv"
        csv.touch()
        
        result = get_latest_csv(str(tmp_path))
        assert result == "notebook-gamer"
