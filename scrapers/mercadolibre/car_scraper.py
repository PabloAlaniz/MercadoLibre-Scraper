"""Standalone car detail extraction for MercadoLibre."""


def scrape_car_details(soup):
    """Extract car-specific details from a MercadoLibre product page.

    Args:
        soup (BeautifulSoup): Parsed HTML of the product detail page.

    Returns:
        dict: Dictionary with 'year' and 'km' keys.
    """
    return {
        'year': extract_year(soup),
        'km': extract_km(soup),
    }


def extract_year(soup):
    """Extract vehicle year from product page subtitle."""
    subtitle_element = soup.find('span', class_='ui-pdp-subtitle')
    if subtitle_element:
        parts = subtitle_element.text.split('·')
        year_km_part = parts[0].strip() if len(parts) > 0 else ""
        year, km = year_km_part.split('|') if '|' in year_km_part else (None, None)
        return year.strip() if year else None
    return None


def extract_km(soup):
    """Extract kilometers from product page subtitle."""
    subtitle_element = soup.find('span', class_='ui-pdp-subtitle')
    if subtitle_element:
        parts = subtitle_element.text.split('·')
        year_km_part = parts[0].strip() if len(parts) > 0 else ""
        year, km = year_km_part.split('|') if '|' in year_km_part else (None, None)
        return km.strip() if km else None
    return None
