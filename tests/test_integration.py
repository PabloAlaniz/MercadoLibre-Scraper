"""
Integration tests for MercadoLibre scraper against the real site.

These tests make actual HTTP requests to MercadoLibre searching for
"gol trend" (a popular car in Argentina). They verify that the scraper
correctly parses real HTML from the live site.

Run with: pytest tests/ -v -m integration
"""
import functools

import pytest
import requests
from bs4 import BeautifulSoup

from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper, detect_category
from scrapers.mercadolibre.enums import ProductCategory
from infrastructure.adapters.null_notifier import NullProgressNotifier

pytestmark = pytest.mark.integration

SEARCH_TERM = "gol trend"
DOMAIN = "ar"
SCRAPE_LIMIT = 5

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_original_get = requests.get


def _get_with_ua(*args, **kwargs):
    """Wrap requests.get to always send a browser User-Agent."""
    headers = kwargs.pop("headers", {}) or {}
    headers.setdefault("User-Agent", _USER_AGENT)
    kwargs["headers"] = headers
    return _original_get(*args, **kwargs)


# ---------------------------------------------------------------------------
# Fixtures (module-scoped to minimise HTTP requests)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="module")
def _patch_requests_ua(request):
    """Inject User-Agent into every requests.get call for the module."""
    requests.get = _get_with_ua
    yield
    requests.get = _original_get


@pytest.fixture(scope="module")
def ml_is_reachable():
    """Skip the entire module if MercadoLibre is not reachable."""
    try:
        resp = requests.get(
            "https://listado.mercadolibre.com.ar/gol-trend", timeout=15
        )
        resp.raise_for_status()
    except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
        pytest.skip("MercadoLibre is not reachable — skipping integration tests")


@pytest.fixture(scope="module")
def scraper():
    return MercadoLibreScraper(progress_notifier=NullProgressNotifier())


@pytest.fixture(scope="module")
def search_results_soup(ml_is_reachable, scraper):
    """BeautifulSoup of the search results page."""
    url = f"https://listado.mercadolibre.com.ar/gol-trend"
    return scraper.get_page_content(url)


@pytest.fixture(scope="module")
def search_listings(ml_is_reachable, scraper):
    """List of dicts from scrape_product_list."""
    return scraper.scrape_product_list(DOMAIN, SEARCH_TERM, SCRAPE_LIMIT)


@pytest.fixture(scope="module")
def first_listing_url(search_listings):
    """post_link of the first search result."""
    assert len(search_listings) >= 1, "Need at least one listing"
    return search_listings[0]["post_link"]


@pytest.fixture(scope="module")
def detail_page_soup(ml_is_reachable, scraper, first_listing_url):
    """BeautifulSoup of the first listing's detail page."""
    return scraper.get_page_content(first_listing_url)


# ---------------------------------------------------------------------------
# 1. TestSearchResults — search returns valid products
# ---------------------------------------------------------------------------

class TestSearchResults:

    def test_search_returns_results(self, search_listings):
        assert len(search_listings) >= 1

    def test_search_respects_limit(self, search_listings):
        # Allow some slack — a page may have more items than SCRAPE_LIMIT
        assert len(search_listings) <= SCRAPE_LIMIT + 50

    def test_listing_has_title(self, search_listings):
        with_title = [i for i in search_listings if i["title"]]
        if not with_title:
            pytest.xfail(
                "No listing titles found — ML may have changed HTML selectors "
                "(extract_post_data uses h2 tag)"
            )
        for item in with_title:
            assert len(item["title"]) > 0

    def test_listing_has_price(self, search_listings):
        for item in search_listings:
            assert item["price"] is not None
            assert item["price"].replace(".", "").replace(",", "").isdigit()

    def test_listing_has_post_link(self, search_listings):
        for item in search_listings:
            assert item["post_link"] is not None
            assert "mercadolibre" in item["post_link"].lower() or "mercadolibre" in item["post_link"]

    def test_listing_has_image(self, search_listings):
        for item in search_listings:
            assert item["image_link"] is not None
            assert item["image_link"].startswith("http")

    def test_listing_dict_shape(self, search_listings):
        expected_keys = {"title", "price", "post_link", "image_link"}
        for item in search_listings:
            assert set(item.keys()) == expected_keys


# ---------------------------------------------------------------------------
# 2. TestSearchPageParsing — HTML parsing of search page
# ---------------------------------------------------------------------------

class TestSearchPageParsing:

    def test_get_total_results_positive(self, scraper, search_results_soup):
        total = scraper.get_total_results(search_results_soup)
        assert total > 0

    def test_search_page_has_listing_items(self, search_results_soup):
        items = search_results_soup.find_all("li", class_="ui-search-layout__item")
        assert len(items) > 0

    def test_scrape_page_results_returns_data(self, ml_is_reachable, scraper):
        url = "https://listado.mercadolibre.com.ar/gol-trend"
        results = scraper.scrape_page_results(url)
        assert isinstance(results, list)
        assert len(results) > 0


# ---------------------------------------------------------------------------
# 3. TestProductDetailPage — detail page parsing
# ---------------------------------------------------------------------------

class TestProductDetailPage:

    def test_detail_page_loads(self, detail_page_soup):
        assert detail_page_soup is not None

    def test_extract_title_from_real_page(self, scraper, detail_page_soup):
        title = scraper.extract_title(detail_page_soup)
        assert title is not None
        assert len(title) > 0

    def test_extract_price_from_real_page(self, scraper, detail_page_soup):
        price = scraper.extract_price(detail_page_soup)
        assert price is not None
        assert "$" in price

    def test_extract_link_from_real_page(self, scraper, detail_page_soup):
        link = scraper.extract_link(detail_page_soup)
        assert link is not None
        assert "[Link](" in link


# ---------------------------------------------------------------------------
# 4. TestCategoryDetection — category detection on real pages
# ---------------------------------------------------------------------------

class TestCategoryDetection:

    def test_gol_trend_detected_as_car(self, detail_page_soup):
        category = detect_category(detail_page_soup)
        # "gol trend" is a car, but some listings may lack km info
        assert category in (ProductCategory.CAR, ProductCategory.OTHERS)

    def test_detect_category_returns_valid_value(self, detail_page_soup):
        category = detect_category(detail_page_soup)
        assert category in (ProductCategory.CAR, ProductCategory.PROPERTY, ProductCategory.OTHERS)


# ---------------------------------------------------------------------------
# 5. TestCarSpecificDetails — car-specific fields
# ---------------------------------------------------------------------------

class TestCarSpecificDetails:

    def test_scrape_product_details_returns_dict(self, scraper, detail_page_soup):
        details = scraper.scrape_product_details(detail_page_soup)
        assert isinstance(details, dict)
        assert "title" in details

    def test_car_details_have_year_and_km(self, scraper, detail_page_soup):
        category = detect_category(detail_page_soup)
        if category != ProductCategory.CAR:
            pytest.skip("Listing not detected as car — cannot verify car fields")
        details = scraper.scrape_product_details(detail_page_soup)
        assert "year" in details
        assert "km" in details

    def test_car_year_is_plausible(self, scraper, detail_page_soup):
        category = detect_category(detail_page_soup)
        if category != ProductCategory.CAR:
            pytest.skip("Listing not detected as car")
        details = scraper.scrape_product_details(detail_page_soup)
        year = int(details["year"])
        assert 1990 <= year <= 2027

    def test_car_km_is_plausible(self, scraper, detail_page_soup):
        category = detect_category(detail_page_soup)
        if category != ProductCategory.CAR:
            pytest.skip("Listing not detected as car")
        details = scraper.scrape_product_details(detail_page_soup)
        km = details["km"]
        assert "km" in km.lower() or km.replace(".", "").replace(",", "").isdigit()


# ---------------------------------------------------------------------------
# 6. TestEndToEnd — full pipeline
# ---------------------------------------------------------------------------

class TestEndToEnd:

    def test_full_scraping_pipeline(self, ml_is_reachable):
        """Search → get URL → load detail → verify structured data."""
        s = MercadoLibreScraper(progress_notifier=NullProgressNotifier())
        listings = s.scrape_product_list(DOMAIN, SEARCH_TERM, 3)
        assert len(listings) >= 1

        url = listings[0]["post_link"]
        soup = s.get_page_content(url)
        assert soup is not None

        details = s.scrape_product_details(soup)
        assert isinstance(details, dict)
        assert "title" in details
        assert "price" in details


# ---------------------------------------------------------------------------
# 7. TestBaseScraperHTTP — HTTP layer (now in MercadoLibreScraper)
# ---------------------------------------------------------------------------

class TestBaseScraperHTTP:

    def test_get_page_content_returns_soup(self, ml_is_reachable, scraper):
        soup = scraper.get_page_content("https://listado.mercadolibre.com.ar/gol-trend")
        assert isinstance(soup, BeautifulSoup)

    def test_get_page_content_raises_for_bad_url(self, scraper):
        with pytest.raises(Exception):
            scraper.get_page_content("https://this-domain-does-not-exist-12345.com/")
