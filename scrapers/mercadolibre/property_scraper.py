"""Standalone property detail extraction for MercadoLibre."""


def scrape_property_details(soup):
    """Extract property-specific details from a MercadoLibre product page.

    Args:
        soup (BeautifulSoup): Parsed HTML of the product detail page.

    Returns:
        dict: Dictionary with 'm2' key.
    """
    return {
        'm2': extract_m2(soup),
    }


def extract_m2(soup):
    """Extract square meters from product page."""
    m2_element = soup.find('span', string=lambda text: text and "m²" in text)
    return m2_element.text if m2_element else None
