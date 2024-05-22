from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper


class CarScraper(MercadoLibreScraper):
    def scrape_specific_details(self, soup):
        return {
            'year': self.extract_year(soup),
            'km': self.extract_km(soup),
        }

    @staticmethod
    def extract_year(soup):
        subtitle_element = soup.find('span', class_='ui-pdp-subtitle')
        if subtitle_element:
            parts = subtitle_element.text.split('·')
            year_km_part = parts[0].strip() if len(parts) > 0 else ""
            year, km = year_km_part.split('|') if '|' in year_km_part else (None, None)
            return year.strip() if year else None
        return None

    @staticmethod
    def extract_km(soup):
        subtitle_element = soup.find('span', class_='ui-pdp-subtitle')
        if subtitle_element:
            parts = subtitle_element.text.split('·')
            year_km_part = parts[0].strip() if len(parts) > 0 else ""
            year, km = year_km_part.split('|') if '|' in year_km_part else (None, None)
            return km.strip() if km else None
        return None
