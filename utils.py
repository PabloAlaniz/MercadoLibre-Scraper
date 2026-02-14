"""
Generic utility functions for MercadoLibre Scraper.

Only truly generic helpers live here. Retailer-specific and
presentation-specific functions belong in their respective packages.
"""

import os
import glob
import logging
import re

logging.basicConfig(level=logging.DEBUG)


def format_filename(product_name):
    """Convert product name to URL-safe filename format.

    Example:
        >>> format_filename("Notebook Gamer")
        'notebook-gamer'
    """
    return product_name.replace(' ', '-').lower()


def format_price(df):
    """Format price column in DataFrame for numerical operations.

    Removes thousand separators and converts to float.
    """
    if "price" in df.columns:
        df = df.copy()
        df["price"] = df["price"].astype(str).str.replace(".", "").str.replace(",", ".").astype(float)
    return df


def format_price_for_display(price):
    """Format price for human-readable display.

    Uses Argentine formatting: thousands separator (.) and decimal comma (,).

    Example:
        >>> format_price_for_display(150000)
        '$150.000,00'
    """
    try:
        price_float = float(price)
        return "${:,.2f}".format(price_float).replace(",", "@").replace(".", ",").replace("@", ".")
    except ValueError:
        return price


def get_latest_csv(directory):
    """Find the most recently created CSV file in a directory."""
    list_of_files = glob.glob(os.path.join(directory, "*.csv"))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return os.path.basename(latest_file).replace("_scraped_data_detailed.csv", "")


def format_link_to_markdown(link):
    """Convert a URL to Markdown link format.

    Example:
        >>> format_link_to_markdown("https://example.com")
        '[Link](https://example.com)'
    """
    return f"[Link]({link})"


def extract_url_from_markdown(markdown_link):
    """Extract URL from a Markdown-formatted link.

    Example:
        >>> extract_url_from_markdown("[Link](https://example.com)")
        'https://example.com'
    """
    pattern = r'\[.*\]\((.*)\)'
    match = re.search(pattern, markdown_link)
    if match:
        return match.group(1)
    return None
