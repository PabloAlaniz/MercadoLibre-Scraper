import threading
from log_config import get_logger
logger = get_logger(__name__)
class ScraperManager:
    def __init__(self, data_manager, scraper):
        self.data_manager = data_manager
        self.scraper = scraper

    def get_product_list(self, product_name):
        domain = 'ar'  # Ejemplo de dominio
        user_scraping_limit = 100  # Ejemplo de límite de scraping

        product_data_list = self.scraper.scrape_product_list(domain, product_name, user_scraping_limit)

        if product_data_list:
            # Exportar los datos recolectados a CSV

            logger.info(f"Scraping para {product_name} completado con éxito.")
            return product_data_list, f"Scraping para {product_name} completado!"
        else:
            logger.warning(f"No se encontraron datos para {product_name}.")
            return None, f"No se encontraron datos para {product_name}."

    def get_product_details(self, url):
        soup = self.scraper.get_page_content(url)
        if not soup:
            return False

        product = self.scraper.scrape_product_details(soup)
        return product

    def get_products_details(self, urls):
        products = []
        for url in urls:
            product = self.get_product_details(url)
            if product:
                products.append(product)
        return products

    def get_product_details_thread(self, url, products):
        product = self.get_product_details(url)
        if product:
            products.append(product)

    def get_products_details_thread(self, urls):
        products = []
        threads = []

        # Crear y comenzar un hilo para cada URL
        for url in urls:
            thread = threading.Thread(target=self.get_product_details_thread, args=(url, products))
            threads.append(thread)
            thread.start()

        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()

        return products