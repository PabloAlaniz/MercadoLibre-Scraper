"""
Utility functions for MercadoLibre Scraper.

This module provides helper functions for formatting data, handling files,
and managing WebSocket communication.
"""

import os
import glob
from config import socketio, DATA_DIRECTORY, CSV_SEPARATOR
import json
import dash
import logging
import re

logging.basicConfig(level=logging.DEBUG)


def format_filename(product_name):
    """
    Convert product name to URL-safe filename format.

    Args:
        product_name (str): Product name with spaces.

    Returns:
        str: Lowercase filename with hyphens instead of spaces.

    Example:
        >>> format_filename("Notebook Gamer")
        'notebook-gamer'
    """
    return product_name.replace(' ', '-').lower()


def format_price(df):
    """
    Format price column in DataFrame for numerical operations.

    Removes thousand separators and converts to float.

    Args:
        df (pandas.DataFrame): DataFrame with 'price' column.

    Returns:
        pandas.DataFrame: DataFrame with formatted price column.
    """
    if "price" in df.columns:
        df = df.copy()
        df["price"] = df["price"].astype(str).str.replace(".", "").str.replace(",", ".").astype(float)
    return df


def clean_km(km_str):
    """
    Clean and parse kilometer values from car listings.

    Args:
        km_str (str): Kilometer string (e.g., "50.000 km").

    Returns:
        int: Parsed kilometer value without separators.

    Example:
        >>> clean_km("50.000 km")
        50000
    """
    return int(km_str.replace(' km', '').replace('.', ''))


def format_price_for_display(price):
    """
    Format price for human-readable display in dashboard.

    Uses Argentine formatting: thousands separator (.) and decimal comma (,).

    Args:
        price (str or float): Price value to format.

    Returns:
        str: Formatted price string (e.g., "$150.000,00").

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
    """
    Find the most recently created CSV file in a directory.

    Args:
        directory (str): Directory path to search.

    Returns:
        str or None: Base filename without suffix, or None if no files found.

    Example:
        >>> get_latest_csv("data/")
        'notebook-gamer'
    """
    list_of_files = glob.glob(os.path.join(directory, "*.csv"))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return os.path.basename(latest_file).replace("_scraped_data_detailed.csv", "")


def format_link_to_markdown(link):
    """
    Convert a URL to Markdown link format.

    Args:
        link (str): Raw URL.

    Returns:
        str: Markdown-formatted link.

    Example:
        >>> format_link_to_markdown("https://example.com")
        '[Link](https://example.com)'
    """
    return f"[Link]({link})"


def extract_url_from_markdown(markdown_link):
    """
    Extract URL from a Markdown-formatted link.

    Args:
        markdown_link (str): Markdown link string (e.g., "[Text](url)").

    Returns:
        str or None: Extracted URL, or None if not a valid Markdown link.

    Example:
        >>> extract_url_from_markdown("[Link](https://example.com)")
        'https://example.com'
    """
    pattern = r'\[.*\]\((.*)\)'
    match = re.search(pattern, markdown_link)
    if match:
        return match.group(1)
    return None

@socketio.on('scrape_status')
def update_scrape_progress(message):
    progress = message['progress']
    total = message['total']
    # Emit the progress to the frontend
    dash.callback_context.response.set_data(json.dumps({
        'response': {
            'progress': progress,
            'total': total
        }
    }))

def export_to_csv(self, product_name):
    try:
        # Reemplazar espacios por guiones en el nombre del producto
        filename = f"{product_name.replace(' ', '-')}.csv"
        logger.info(f"Preparando para exportar datos del producto: {product_name}")

        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            logger.info(f"Creado el directorio de datos: {self.data_directory}")

        df = pd.DataFrame(self.data)
        file_path = os.path.join(self.data_directory, filename)

        df.to_csv(file_path, sep=self.csv_separator)
        logger.info(f"Datos exportados exitosamente a {file_path}")

    except Exception as e:
        logger.error(f"Error al exportar datos a CSV: {e}")
