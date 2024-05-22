from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper

class PropertyScraper(MercadoLibreScraper):

    def scrape_specific_details(self, soup):
        return {
            'm2': self.extract_m2(soup),
        }

    @staticmethod
    def extract_m2(soup):
        m2_element = soup.find('span', string=lambda text: text and "m²" in text)
        return m2_element.text if m2_element else None
