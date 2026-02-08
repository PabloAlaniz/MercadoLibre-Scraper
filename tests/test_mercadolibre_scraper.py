"""
Tests for MercadoLibre scraper functionality.
"""
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup


class TestDetectCategory:
    """Tests for category detection from product pages."""
    
    def test_detect_car_category(self):
        """Should detect car category when km is present."""
        from scrapers.mercadolibre.mercadolibre_scraper import detect_category
        
        html = '''
        <div>
            <span class="ui-pdp-subtitle">Usado · 50000 km · 2020</span>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        assert detect_category(soup) == 'car'
    
    def test_detect_property_category(self):
        """Should detect property category when m² is present."""
        from scrapers.mercadolibre.mercadolibre_scraper import detect_category
        
        html = '''
        <div>
            <span>150 m² totales</span>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        assert detect_category(soup) == 'property'
    
    def test_detect_others_category(self):
        """Should default to others category."""
        from scrapers.mercadolibre.mercadolibre_scraper import detect_category
        
        html = '<div><span>iPhone 15</span></div>'
        soup = BeautifulSoup(html, 'html.parser')
        assert detect_category(soup) == 'others'


class TestMercadoLibreScraper:
    """Tests for MercadoLibreScraper class."""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        # Mock the config imports
        with patch.dict('sys.modules', {
            'config': Mock(
                socketio=Mock(),
                SCRAPER_CONFIG={'base_url': 'https://listado.mercadolibre.com.{domain}/', 'page_increment': 50, 'max_pages': 10},
                DATA_DIRECTORY='./data',
                CSV_SEPARATOR=','
            )
        }):
            from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
            return MercadoLibreScraper()
    
    def test_format_price_removes_dots(self):
        """Should remove thousand separators from price."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
        
        with patch.dict('sys.modules', {
            'config': Mock(
                socketio=Mock(),
                SCRAPER_CONFIG={'base_url': '', 'page_increment': 50, 'max_pages': 10},
                DATA_DIRECTORY='./data',
                CSV_SEPARATOR=','
            )
        }):
            scraper = MercadoLibreScraper()
            
            price_element = Mock()
            price_element.text = '1.234.567'
            
            result = scraper.format_price(price_element)
            assert result == '1234567'
    
    def test_format_price_returns_none_for_empty(self):
        """Should return None for empty price element."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
        
        with patch.dict('sys.modules', {
            'config': Mock(
                socketio=Mock(),
                SCRAPER_CONFIG={'base_url': '', 'page_increment': 50, 'max_pages': 10},
                DATA_DIRECTORY='./data',
                CSV_SEPARATOR=','
            )
        }):
            scraper = MercadoLibreScraper()
            assert scraper.format_price(None) is None
    
    def test_extract_title(self):
        """Should extract title from product page."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
        
        html = '<h1 class="ui-pdp-title">iPhone 15 Pro Max 256GB</h1>'
        soup = BeautifulSoup(html, 'html.parser')
        
        title = MercadoLibreScraper.extract_title(soup)
        assert title == 'iPhone 15 Pro Max 256GB'
    
    def test_extract_title_returns_none_when_missing(self):
        """Should return None when title is not found."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
        
        html = '<div>No title here</div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        title = MercadoLibreScraper.extract_title(soup)
        assert title is None
    
    def test_extract_price(self):
        """Should extract and format price from product page."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
        
        html = '''
        <div>
            <span class="andes-money-amount__currency-symbol">$</span>
            <span class="andes-money-amount__fraction">1.500.000</span>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        price = MercadoLibreScraper.extract_price(soup)
        assert price == '$ 1.500.000'
    
    def test_get_total_results(self):
        """Should parse total results count."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
        
        with patch.dict('sys.modules', {
            'config': Mock(
                socketio=Mock(),
                SCRAPER_CONFIG={'base_url': '', 'page_increment': 50, 'max_pages': 10},
                DATA_DIRECTORY='./data',
                CSV_SEPARATOR=','
            )
        }):
            scraper = MercadoLibreScraper()
            
            html = '<span class="ui-search-search-result__quantity-results">1.234 resultados</span>'
            soup = BeautifulSoup(html, 'html.parser')
            
            total = scraper.get_total_results(soup)
            assert total == 1234
    
    def test_get_total_results_returns_zero_when_missing(self):
        """Should return 0 when results count is not found."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
        
        with patch.dict('sys.modules', {
            'config': Mock(
                socketio=Mock(),
                SCRAPER_CONFIG={'base_url': '', 'page_increment': 50, 'max_pages': 10},
                DATA_DIRECTORY='./data',
                CSV_SEPARATOR=','
            )
        }):
            scraper = MercadoLibreScraper()
            
            html = '<div>No results here</div>'
            soup = BeautifulSoup(html, 'html.parser')
            
            total = scraper.get_total_results(soup)
            assert total == 0
    
    def test_extract_post_data(self):
        """Should extract all post data from a listing item."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
        
        with patch.dict('sys.modules', {
            'config': Mock(
                socketio=Mock(),
                SCRAPER_CONFIG={'base_url': '', 'page_increment': 50, 'max_pages': 10},
                DATA_DIRECTORY='./data',
                CSV_SEPARATOR=','
            )
        }):
            scraper = MercadoLibreScraper()
            
            html = '''
            <li class="ui-search-layout__item">
                <h2>Test Product</h2>
                <span class="andes-money-amount__fraction">100.000</span>
                <a href="https://articulo.mercadolibre.com.ar/test">Link</a>
                <img src="https://http2.mlstatic.com/test.jpg" />
            </li>
            '''
            soup = BeautifulSoup(html, 'html.parser')
            post = soup.find('li')
            
            data = scraper.extract_post_data(post)
            
            assert data['title'] == 'Test Product'
            assert data['price'] == '100000'
            assert data['post_link'] == 'https://articulo.mercadolibre.com.ar/test'
            assert data['image link'] == 'https://http2.mlstatic.com/test.jpg'


class TestBaseScraper:
    """Tests for base Scraper class."""
    
    def test_get_page_content_success(self):
        """Should return BeautifulSoup object on successful request."""
        from scrapers.base_scraper import Scraper
        
        scraper = Scraper()
        
        with patch('scrapers.base_scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = '<html><body>Test</body></html>'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = scraper.get_page_content('https://example.com')
            
            assert result is not None
            assert result.find('body').text == 'Test'
    
    def test_get_page_content_raises_on_error(self):
        """Should raise exception on request error."""
        from scrapers.base_scraper import Scraper
        import requests
        
        scraper = Scraper()
        
        with patch('scrapers.base_scraper.requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException('Connection error')
            
            with pytest.raises(Exception) as exc_info:
                scraper.get_page_content('https://example.com')
            
            assert 'Error al obtener la página' in str(exc_info.value)
