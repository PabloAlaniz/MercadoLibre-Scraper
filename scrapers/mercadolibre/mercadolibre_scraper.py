"""
MercadoLibre web scraper for products, cars, and real estate listings.

This module provides the main scraping functionality for MercadoLibre across
18 Latin American countries. It supports different product categories and
automatically detects and routes to specialized scrapers when needed.
"""

import requests
from bs4 import BeautifulSoup

from utils import format_filename, format_link_to_markdown
from scrapers.mercadolibre.enums import ProductCategory
from domain.entities import ProductListing, ProductDetail, CarProductDetail, PropertyProductDetail
from log_config import get_logger
logger = get_logger(__name__)


DEFAULT_CONFIG = {
    'base_url': 'https://listado.mercadolibre.com.{domain}/',
    'page_increment': 50,
    'max_pages': 100,
}


def detect_category(soup):
    """
    Detect the category of a MercadoLibre product from its page content.

    Args:
        soup (BeautifulSoup): Parsed HTML content of the product page.

    Returns:
        str: Category identifier ('car', 'property', or 'others').
    """
    if soup.find('span', class_='ui-pdp-subtitle') and ' km ' in soup.text:
        return ProductCategory.CAR
    elif soup.find('span', string=lambda text: text and "m²" in text):
        return ProductCategory.PROPERTY
    else:
        return ProductCategory.OTHERS


class MercadoLibreScraper:
    """
    Main scraper for MercadoLibre product listings.

    Implements ScraperPort protocol without inheriting from a base class.

    Args:
        progress_notifier: Optional ProgressNotifierPort implementation.
        config: Optional dict with 'base_url', 'page_increment', 'max_pages'.
    """

    def __init__(self, progress_notifier=None, config=None):
        self.data = []
        self.progress_notifier = progress_notifier
        _cfg = config or DEFAULT_CONFIG
        self.base_url = _cfg['base_url']
        self.page_increment = _cfg['page_increment']
        self.max_pages = _cfg['max_pages']

    def get_page_content(self, url):
        """Fetch and parse a web page.

        Args:
            url (str): URL to fetch.

        Returns:
            BeautifulSoup: Parsed HTML content.

        Raises:
            Exception: If the HTTP request fails.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error al obtener la página {url}: {e}")
            raise Exception(f"Error al obtener la página {url}: {e}")

    def format_price(self, price_element):
        """
        Format price by removing thousand separators (dots).

        Args:
            price_element: BeautifulSoup element containing the price.

        Returns:
            str or None: Formatted price string without dots, or None if invalid.
        """
        if price_element and isinstance(price_element.text, str):
            return price_element.text.replace('.', '')
        return None

    def extract_post_data(self, post):
        """
        Extract key data fields from a product listing element.

        Args:
            post: BeautifulSoup element representing a product listing.

        Returns:
            dict: Dictionary with 'title', 'price', 'post_link', and 'image_link'.
        """
        title_element = post.find('h2')
        price_value = self.format_price(post.find('span', class_='andes-money-amount__fraction'))
        post_link_element = post.find("a")
        img_element = post.find("img")

        listing = ProductListing(
            title=title_element.text if title_element else None,
            price=price_value if price_value else None,
            post_link=post_link_element['href'] if post_link_element else None,
            image_link=img_element.get('data-src', img_element.get('src')) if img_element else None,
        )
        return listing.to_dict()

    def get_total_results(self, soup):
        """
        Extract the total number of search results from the search page.

        Args:
            soup (BeautifulSoup): Parsed HTML of the search results page.

        Returns:
            int: Total number of results, or 0 if not found.
        """
        results_element = soup.find('span', class_='ui-search-search-result__quantity-results')
        if results_element:
            return int(results_element.text.split()[0].replace('.', '').replace(',', ''))
        return 0

    def scrape_page_results(self, url):
        """
        Scrape all product listings from a single search results page.

        Args:
            url (str): URL of the search results page.

        Returns:
            list: List of dictionaries, each containing product data.
        """
        logger.debug(f"Comenzando scrape_page_results para URL: {url}")
        soup = self.get_page_content(url)

        if not soup:
            logger.warning("No se pudo obtener el contenido de la página.")
            return []

        content = soup.find_all('li', class_='ui-search-layout__item')
        logger.debug(f"Encontrados {len(content)} elementos en la página.")

        page_data = []
        for post in content:
            post_data = self.extract_post_data(post)
            page_data.append(post_data)
            logger.debug(f"Datos del post agregados: {post_data}")

        logger.debug("Scrape de la página completado exitosamente.")
        return page_data

    def scrape_product_details(self, soup):
        """
        Scrape detailed information from a product detail page.

        Automatically detects product category (car, property, general) and
        delegates to the appropriate specialized scraper.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product detail page.

        Returns:
            dict: Dictionary with all extracted product details.
        """
        category = detect_category(soup)

        base_kwargs = dict(
            title=self.extract_title(soup),
            price=self.extract_price(soup),
            publication_date=self.extract_publication_date(soup),
            author=self.extract_author(soup),
            link=self.extract_link(soup),
            shipping=self.extract_shipping(soup),
            category=category,
        )

        if category == ProductCategory.CAR:
            from scrapers.mercadolibre.car_scraper import scrape_car_details
            specific_data = scrape_car_details(soup)
            detail = CarProductDetail(
                **base_kwargs,
                year=specific_data.get('year'),
                km=specific_data.get('km'),
            )
        elif category == ProductCategory.PROPERTY:
            from scrapers.mercadolibre.property_scraper import scrape_property_details
            specific_data = scrape_property_details(soup)
            detail = PropertyProductDetail(
                **base_kwargs,
                m2=specific_data.get('m2'),
            )
        else:
            detail = ProductDetail(**base_kwargs)

        return detail.to_dict()

    @staticmethod
    def extract_title(soup):
        """Extract product title from detail page."""
        title = soup.find('h1', class_='ui-pdp-title')
        return title.text if title else None

    @staticmethod
    def extract_price(soup):
        """Extract formatted price (currency symbol + amount) from detail page."""
        price_simbol = soup.find('span', class_='andes-money-amount__currency-symbol')
        price = soup.find('span', class_='andes-money-amount__fraction')
        return f"{price_simbol.text} {price.text}" if price_simbol and price else None

    @staticmethod
    def extract_author(soup):
        """Extract seller/author information from detail page."""
        author = soup.find('div', class_='ui-pdp-seller-validated')
        return author.text if author else None

    @staticmethod
    def extract_link(soup):
        """Extract canonical product URL from detail page."""
        link = soup.find('link', rel='canonical')
        return format_link_to_markdown(link['href']) if link else None

    @staticmethod
    def extract_publication_date(soup):
        """Extract publication date from product detail page."""
        subtitle_element = soup.find('span', class_='ui-pdp-subtitle')
        if subtitle_element:
            parts = subtitle_element.text.split('·')
            publication_date = parts[1].strip() if len(parts) > 1 else None
            return publication_date
        return None

    @staticmethod
    def extract_shipping(soup):
        """Extract shipping/delivery information from detail page."""
        shipping_element = soup.find('span', string=lambda text: text and "Llega" in text)
        return shipping_element.text if shipping_element else None

    def scrape_product_list(self, domain, product_name, user_scraping_limit):
        """
        Scrape multiple pages of product listings for a search query.

        Args:
            domain (str): Country domain code (e.g., 'ar', 'mx', 'br').
            product_name (str): Search query/product name to scrape.
            user_scraping_limit (int): Maximum number of products to collect.

        Returns:
            list: List of dictionaries, each containing product data from listings.
        """
        cleaned_name = format_filename(product_name)
        base_url = self.base_url.format(domain=domain)

        soup = self.get_page_content(base_url + cleaned_name)
        total_results = self.get_total_results(soup)

        products_per_page = len(soup.find_all('li', class_='ui-search-layout__item'))
        estimated_total_pages = total_results // products_per_page + (total_results % products_per_page > 0)

        scraping_limit = min(total_results, user_scraping_limit)
        logger.info(f"Se obtuvieron {total_results} resultados. Se limitará el scraping a {scraping_limit} resultados.")

        all_data = []

        for i in range(0, min(estimated_total_pages, self.max_pages)):
            if len(all_data) >= scraping_limit:
                logger.info(f"Se alcanzó el límite de {scraping_limit} productos. Terminando.")
                break

            url = f"{base_url}{cleaned_name}_Desde_{(i * self.page_increment) + 1}_NoIndex_True"
            scraped_page_data = self.scrape_page_results(url)
            if not scraped_page_data:
                logger.warning(f"La página {i + 1} no devolvió datos. Terminando.")
                break

            all_data.extend(scraped_page_data)
            logger.info(f"Scraping de página {i + 1} de {estimated_total_pages} completado")

            if self.progress_notifier:
                self.progress_notifier.notify_progress(i, estimated_total_pages)

        return all_data
