"""
Tests for MercadoLibre scraper functionality.
"""
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from infrastructure.adapters.null_notifier import NullProgressNotifier

TEST_CONFIG = {
    'base_url': 'https://listado.mercadolibre.com.{domain}/',
    'page_increment': 50,
    'max_pages': 10,
}


def _make_scraper():
    from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
    return MercadoLibreScraper(progress_notifier=NullProgressNotifier(), config=TEST_CONFIG)


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
        return _make_scraper()

    def test_format_price_removes_dots(self, scraper):
        """Should remove thousand separators from price."""
        price_element = Mock()
        price_element.text = '1.234.567'

        result = scraper.format_price(price_element)
        assert result == '1234567'

    def test_format_price_returns_none_for_empty(self, scraper):
        """Should return None for empty price element."""
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

    def test_get_total_results(self, scraper):
        """Should parse total results count."""
        html = '<span class="ui-search-search-result__quantity-results">1.234 resultados</span>'
        soup = BeautifulSoup(html, 'html.parser')

        total = scraper.get_total_results(soup)
        assert total == 1234

    def test_get_total_results_returns_zero_when_missing(self, scraper):
        """Should return 0 when results count is not found."""
        html = '<div>No results here</div>'
        soup = BeautifulSoup(html, 'html.parser')

        total = scraper.get_total_results(soup)
        assert total == 0

    def test_extract_post_data(self, scraper):
        """Should extract all post data from a listing item."""
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
        assert data['image_link'] == 'https://http2.mlstatic.com/test.jpg'


class TestScrapePageResults:
    """Tests for scrape_page_results method."""

    def test_scrape_page_results_success(self):
        """Should extract all products from search results page."""
        scraper = _make_scraper()

        html = '''
        <ul>
            <li class="ui-search-layout__item">
                <h2>Product 1</h2>
                <span class="andes-money-amount__fraction">100.000</span>
                <a href="https://articulo.mercadolibre.com.ar/prod1">Link1</a>
                <img src="https://http2.mlstatic.com/img1.jpg" />
            </li>
            <li class="ui-search-layout__item">
                <h2>Product 2</h2>
                <span class="andes-money-amount__fraction">200.000</span>
                <a href="https://articulo.mercadolibre.com.ar/prod2">Link2</a>
                <img src="https://http2.mlstatic.com/img2.jpg" />
            </li>
        </ul>
        '''

        with patch.object(scraper, 'get_page_content') as mock_get:
            mock_get.return_value = BeautifulSoup(html, 'html.parser')

            results = scraper.scrape_page_results('https://test.com')

            assert len(results) == 2
            assert results[0]['title'] == 'Product 1'
            assert results[1]['title'] == 'Product 2'

    def test_scrape_page_results_empty_page(self):
        """Should return empty list when no products found."""
        scraper = _make_scraper()

        html = '<div>No results</div>'

        with patch.object(scraper, 'get_page_content') as mock_get:
            mock_get.return_value = BeautifulSoup(html, 'html.parser')

            results = scraper.scrape_page_results('https://test.com')

            assert results == []

    def test_scrape_page_results_no_soup(self):
        """Should return empty list when page content cannot be fetched."""
        scraper = _make_scraper()

        with patch.object(scraper, 'get_page_content') as mock_get:
            mock_get.return_value = None

            results = scraper.scrape_page_results('https://test.com')

            assert results == []


class TestProductDetails:
    """Tests for product detail extraction methods."""

    def test_extract_author(self):
        """Should extract seller name from product page."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper

        html = '<div class="ui-pdp-seller-validated">Vendedor Oficial</div>'
        soup = BeautifulSoup(html, 'html.parser')

        author = MercadoLibreScraper.extract_author(soup)
        assert author == 'Vendedor Oficial'

    def test_extract_author_missing(self):
        """Should return None when seller info not found."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper

        html = '<div>No seller info</div>'
        soup = BeautifulSoup(html, 'html.parser')

        author = MercadoLibreScraper.extract_author(soup)
        assert author is None

    def test_extract_link(self):
        """Should extract and format canonical link."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper

        html = '<link rel="canonical" href="https://articulo.mercadolibre.com.ar/test" />'
        soup = BeautifulSoup(html, 'html.parser')

        with patch('scrapers.mercadolibre.mercadolibre_scraper.format_link_to_markdown') as mock_format:
            mock_format.return_value = '[Link](https://articulo.mercadolibre.com.ar/test)'

            link = MercadoLibreScraper.extract_link(soup)
            mock_format.assert_called_once_with('https://articulo.mercadolibre.com.ar/test')

    def test_extract_link_missing(self):
        """Should return None when canonical link not found."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper

        html = '<div>No link here</div>'
        soup = BeautifulSoup(html, 'html.parser')

        link = MercadoLibreScraper.extract_link(soup)
        assert link is None

    def test_extract_publication_date(self):
        """Should extract publication date from subtitle."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper

        html = '<span class="ui-pdp-subtitle">Nuevo · Hace 2 días · Vendedor Pro</span>'
        soup = BeautifulSoup(html, 'html.parser')

        date = MercadoLibreScraper.extract_publication_date(soup)
        assert date == 'Hace 2 días'

    def test_extract_publication_date_missing(self):
        """Should return None when publication date not found."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper

        html = '<div>No date</div>'
        soup = BeautifulSoup(html, 'html.parser')

        date = MercadoLibreScraper.extract_publication_date(soup)
        assert date is None

    def test_extract_shipping(self):
        """Should extract shipping information."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper

        html = '<span>Llega mañana</span>'
        soup = BeautifulSoup(html, 'html.parser')

        shipping = MercadoLibreScraper.extract_shipping(soup)
        assert shipping == 'Llega mañana'

    def test_extract_shipping_missing(self):
        """Should return None when shipping info not found."""
        from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper

        html = '<div>No shipping</div>'
        soup = BeautifulSoup(html, 'html.parser')

        shipping = MercadoLibreScraper.extract_shipping(soup)
        assert shipping is None


class TestScrapeProductDetails:
    """Tests for scrape_product_details orchestration."""

    def test_scrape_product_details_general(self):
        """Should extract details for general products."""
        scraper = _make_scraper()

        html = '''
        <div>
            <h1 class="ui-pdp-title">iPhone 15</h1>
            <span class="andes-money-amount__currency-symbol">$</span>
            <span class="andes-money-amount__fraction">500.000</span>
            <div class="ui-pdp-seller-validated">Apple Store</div>
            <link rel="canonical" href="https://test.com/iphone" />
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')

        with patch('scrapers.mercadolibre.mercadolibre_scraper.format_link_to_markdown') as mock_format:
            mock_format.return_value = '[Link](https://test.com/iphone)'

            details = scraper.scrape_product_details(soup)

            assert details['title'] == 'iPhone 15'
            assert details['price'] == '$ 500.000'
            assert details['author'] == 'Apple Store'

    def test_scrape_product_details_car_category(self):
        """Should delegate to car scraper for car products."""
        scraper = _make_scraper()

        html = '''
        <div>
            <h1 class="ui-pdp-title">Toyota Corolla 2020</h1>
            <span class="ui-pdp-subtitle">2020 | 50.000 km · Publicado hace 2 días</span>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')

        with patch('scrapers.mercadolibre.mercadolibre_scraper.detect_category') as mock_detect:
            mock_detect.return_value = 'car'

            with patch('scrapers.mercadolibre.car_scraper.scrape_car_details') as mock_car:
                mock_car.return_value = {'year': '2020', 'km': '50.000 km'}

                details = scraper.scrape_product_details(soup)

                assert 'title' in details
                assert details['year'] == '2020'
                assert details['km'] == '50.000 km'


class TestGetPageContent:
    """Tests for get_page_content (now in MercadoLibreScraper)."""

    def test_get_page_content_success(self):
        """Should return BeautifulSoup object on successful request."""
        scraper = _make_scraper()

        with patch('scrapers.mercadolibre.mercadolibre_scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = '<html><body>Test</body></html>'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = scraper.get_page_content('https://example.com')

            assert result is not None
            assert result.find('body').text == 'Test'

    def test_get_page_content_raises_on_error(self):
        """Should raise exception on request error."""
        import requests
        scraper = _make_scraper()

        with patch('scrapers.mercadolibre.mercadolibre_scraper.requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException('Connection error')

            with pytest.raises(Exception) as exc_info:
                scraper.get_page_content('https://example.com')

            assert 'Error al obtener la página' in str(exc_info.value)


class TestPriceParser:
    """Tests for ML-specific price parser."""

    def test_parse_usd_price(self):
        from scrapers.mercadolibre.price_parser import parse_mercadolibre_price
        from domain.enums import Currency

        m = parse_mercadolibre_price("U$S 15.000")
        assert m is not None
        assert m.amount == 15000.0
        assert m.currency == Currency.USD

    def test_parse_ars_price(self):
        from scrapers.mercadolibre.price_parser import parse_mercadolibre_price
        from domain.enums import Currency

        m = parse_mercadolibre_price("$ 150.000")
        assert m is not None
        assert m.amount == 150000.0
        assert m.currency == Currency.ARS

    def test_parse_none_returns_none(self):
        from scrapers.mercadolibre.price_parser import parse_mercadolibre_price

        assert parse_mercadolibre_price(None) is None

    def test_parse_empty_string_returns_none(self):
        from scrapers.mercadolibre.price_parser import parse_mercadolibre_price

        assert parse_mercadolibre_price("") is None

    def test_parse_invalid_string_returns_none(self):
        from scrapers.mercadolibre.price_parser import parse_mercadolibre_price

        assert parse_mercadolibre_price("no price here") is None

    def test_parse_price_with_no_dots(self):
        from scrapers.mercadolibre.price_parser import parse_mercadolibre_price

        m = parse_mercadolibre_price("$ 500")
        assert m is not None
        assert m.amount == 500.0


class TestMercadoLibreEnums:
    """Tests for ML-specific enums."""

    def test_product_category_car(self):
        from scrapers.mercadolibre.enums import ProductCategory
        assert ProductCategory.CAR == 'car'

    def test_product_category_property(self):
        from scrapers.mercadolibre.enums import ProductCategory
        assert ProductCategory.PROPERTY == 'property'

    def test_product_category_others(self):
        from scrapers.mercadolibre.enums import ProductCategory
        assert ProductCategory.OTHERS == 'others'

    def test_country_domain_ar(self):
        from scrapers.mercadolibre.enums import CountryDomain
        assert CountryDomain.AR == 'ar'

    def test_country_domain_mx(self):
        from scrapers.mercadolibre.enums import CountryDomain
        assert CountryDomain.MX == 'mx'

    def test_country_domain_all_18(self):
        from scrapers.mercadolibre.enums import CountryDomain
        assert len(CountryDomain) == 18
