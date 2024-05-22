import requests
from bs4 import BeautifulSoup
from log_config import get_logger
logger = get_logger(__name__)


class Scraper:
    def get_page_content(self, url):
        try:
            #logger.debug(f"Iniciando la solicitud de la página: {url}")
            response = requests.get(url)
            response.raise_for_status()
            #logger.info(f"Solicitud completada exitosamente para la página: {url}")
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error al obtener la página {url}: {e}")
            raise Exception(f"Error al obtener la página {url}: {e}")

    def scrape_product_list(self, domain, product_name, user_scraping_limit):
        raise NotImplementedError

    def scrape_product_details(self, soup):
        raise NotImplementedError

    def get_total_results(self, soup):
        raise NotImplementedError("Este método debe ser implementado por subclases.")

    def export_to_csv(self, product_name):
        raise NotImplementedError
