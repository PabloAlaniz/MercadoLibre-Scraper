"""
MercadoLibre web scraper for products, cars, and real estate listings.

This module provides the main scraping functionality for MercadoLibre across
18 Latin American countries. It supports different product categories and
automatically detects and routes to specialized scrapers when needed.
"""

from config import socketio, SCRAPER_CONFIG, DATA_DIRECTORY, CSV_SEPARATOR
from scrapers.base_scraper import Scraper
from utils import format_filename, format_link_to_markdown
from log_config import get_logger
logger = get_logger(__name__)


def detect_category(soup):
    """
    Detect the category of a MercadoLibre product from its page content.

    Args:
        soup (BeautifulSoup): Parsed HTML content of the product page.

    Returns:
        str: Category identifier ('car', 'property', or 'others').
    """
    if soup.find('span', class_='ui-pdp-subtitle') and ' km ' in soup.text:
        return 'car'
    elif soup.find('span', string=lambda text: text and "m²" in text):
        return 'property'
    else:
        return 'others'


class MercadoLibreScraper(Scraper):
    """
    Main scraper for MercadoLibre product listings.

    This scraper handles general products and serves as the base for specialized
    scrapers (cars, real estate). It supports pagination, progress tracking, and
    multi-country operations.

    Attributes:
        data (list): Collected product data.
        base_url (str): Base URL template for MercadoLibre searches.
        data_directory (str): Directory for CSV output.
        csv_separator (str): CSV column separator.
        page_increment (int): Products per page (default: 50).
        max_pages (int): Maximum pages to scrape (default: 100).
    """

    def __init__(self):
        self.data = []
        self.base_url = SCRAPER_CONFIG['base_url']
        self.data_directory = DATA_DIRECTORY
        self.csv_separator = CSV_SEPARATOR
        self.page_increment = SCRAPER_CONFIG['page_increment']
        self.max_pages = SCRAPER_CONFIG['max_pages']

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
            dict: Dictionary with 'title', 'price', 'post_link', and 'image link'.
        """
        title_element = post.find('h2')
        price_value = self.format_price(post.find('span', class_='andes-money-amount__fraction'))
        post_link_element = post.find("a")
        img_element = post.find("img")

        data = {
            'title': title_element.text if title_element else None,
            'price': price_value if price_value else None,
            'post_link': post_link_element['href'] if post_link_element else None,
            'image link': img_element.get('data-src', img_element.get('src')) if img_element else None
        }
        return data

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

        if category == 'car':
            from scrapers.mercadolibre.car_scraper import CarScraper
            scraper = CarScraper()
        elif category == 'property':
            from scrapers.mercadolibre.property_scraper import PropertyScraper
            scraper = PropertyScraper()
        else:
            scraper = MercadoLibreScraper()

        base_data = {
            'title': self.extract_title(soup),
            'price': self.extract_price(soup),
            'publication_date': self.extract_publication_date(soup),
            'author': self.extract_author(soup),
            'link': self.extract_link(soup),
            'envio': self.extract_envio(soup),
        }

        specific_data = scraper.scrape_specific_details(soup)
        base_data.update(specific_data)

        return base_data

    def scrape_specific_details(self, soup):
        """
        Extract category-specific details from the product page.

        This method is overridden by specialized scrapers (CarScraper,
        PropertyScraper) to extract category-specific fields.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product detail page.

        Returns:
            dict: Empty dict for base scraper; category-specific data in subclasses.
        """
        return {}

    @staticmethod
    def extract_title(soup):
        """
        Extract product title from detail page.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product detail page.

        Returns:
            str or None: Product title, or None if not found.
        """
        title = soup.find('h1', class_='ui-pdp-title')
        return title.text if title else None

    @staticmethod
    def extract_price(soup):
        """
        Extract formatted price (currency symbol + amount) from detail page.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product detail page.

        Returns:
            str or None: Formatted price (e.g., "$ 150000"), or None if not found.
        """
        price_simbol = soup.find('span', class_='andes-money-amount__currency-symbol')
        price = soup.find('span', class_='andes-money-amount__fraction')
        return f"{price_simbol.text} {price.text}" if price_simbol and price else None

    @staticmethod
    def extract_author(soup):
        """
        Extract seller/author information from detail page.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product detail page.

        Returns:
            str or None: Seller name/info, or None if not found.
        """
        author = soup.find('div', class_='ui-pdp-seller-validated')
        return author.text if author else None

    @staticmethod
    def extract_link(soup):
        """
        Extract canonical product URL from detail page.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product detail page.

        Returns:
            str or None: Markdown-formatted link, or None if not found.
        """
        link = soup.find('link', rel='canonical')
        return format_link_to_markdown(link['href']) if link else None

    @staticmethod
    def extract_publication_date(soup):
        """
        Extract publication date from product detail page.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product detail page.

        Returns:
            str or None: Publication date text, or None if not found.
        """
        subtitle_element = soup.find('span', class_='ui-pdp-subtitle')
        if subtitle_element:
            parts = subtitle_element.text.split('·')
            publication_date = parts[1].strip() if len(parts) > 1 else None
            return publication_date
        return None

    @staticmethod
    def extract_envio(soup):
        """
        Extract shipping/delivery information from detail page.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product detail page.

        Returns:
            str or None: Shipping info (e.g., "Llega mañana"), or None if not found.
        """
        envio_element = soup.find('span', string=lambda text: text and "Llega" in text)
        return envio_element.text if envio_element else None

    def scrape_product_list(self, domain, product_name, user_scraping_limit):
        """
        Scrape multiple pages of product listings for a search query.

        This is the main entry point for scraping. It handles pagination,
        respects user-defined limits, and emits progress updates via WebSocket.

        Args:
            domain (str): Country domain code (e.g., 'ar', 'mx', 'br').
            product_name (str): Search query/product name to scrape.
            user_scraping_limit (int): Maximum number of products to collect.

        Returns:
            list: List of dictionaries, each containing product data from listings.

        Example:
            >>> scraper = MercadoLibreScraper()
            >>> products = scraper.scrape_product_list('ar', 'notebook gamer', 50)
            >>> len(products)
            50
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

            socketio.emit('scrape_status', {'progress': i, 'total': estimated_total_pages})

        return all_data
