"""Service for converting product prices between currencies."""
from __future__ import annotations

from typing import TYPE_CHECKING

from log_config import get_logger

if TYPE_CHECKING:
    from domain.ports import ExchangeRatePort

logger = get_logger(__name__)


class PriceConversionService:
    """Converts product prices using an injected exchange rate provider."""

    def __init__(self, exchange_rate_provider: ExchangeRatePort):
        self.exchange_rate_provider = exchange_rate_provider

    def get_exchange_rate(self):
        return self.exchange_rate_provider.get_usd_to_ars_rate()

    def convert_prices(self, products: list[dict]) -> list[dict]:
        """Add price_pesos and price_usd fields to each product dict.

        Returns the same list with added fields. Products without a 'price'
        key are left unchanged.
        """
        rate = self.exchange_rate_provider.get_usd_to_ars_rate()
        if rate is None:
            logger.error("No se pudo obtener la tasa de cambio USD para la conversión.")
            return products

        logger.info(f"Tasa de cambio obtenida: {rate}")

        for product in products:
            price_str = str(product.get('price', ''))
            if not price_str:
                continue

            try:
                if "U$S" in price_str:
                    number = float(price_str.replace("U$S", "").replace(".", "").strip())
                    product['price_pesos'] = number * rate
                    product['price_usd'] = number
                else:
                    number = float(price_str.replace("$", "").replace(".", "").strip())
                    product['price_pesos'] = number
                    product['price_usd'] = round(number / rate)
            except (ValueError, ZeroDivisionError):
                continue

        return products
