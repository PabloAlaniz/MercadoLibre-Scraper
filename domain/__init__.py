"""
Domain layer for MercadoLibre Scraper.

Pure Python types with no external dependencies.
"""
from domain.enums import Currency
from domain.value_objects import Money, Kilometers, SquareMeters
from domain.entities import ProductListing, ProductDetail, CarProductDetail, PropertyProductDetail
from domain.ports import (
    ScraperPort,
    ExchangeRatePort,
    ProgressNotifierPort,
    ProductExporterPort,
)

__all__ = [
    'Currency',
    'Money',
    'Kilometers',
    'SquareMeters',
    'ProductListing',
    'ProductDetail',
    'CarProductDetail',
    'PropertyProductDetail',
    'ScraperPort',
    'ExchangeRatePort',
    'ProgressNotifierPort',
    'ProductExporterPort',
]
