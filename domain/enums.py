"""
Domain enums for MercadoLibre Scraper.

Only generic enums live here. Retailer-specific enums belong
in their respective scraper packages.
"""
from enum import Enum


class Currency(str, Enum):
    """Currency codes."""
    ARS = 'ARS'
    USD = 'USD'
