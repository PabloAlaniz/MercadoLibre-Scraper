"""DolarAPI adapter for ExchangeRatePort."""
from __future__ import annotations

from typing import Optional

import requests
from log_config import get_logger

logger = get_logger(__name__)


class DolarApiExchangeRate:
    """Fetches USD/ARS blue exchange rate from dolarapi.com."""

    URL = "https://dolarapi.com/v1/dolares/blue"

    def get_usd_to_ars_rate(self) -> Optional[float]:
        try:
            response = requests.get(self.URL)
            response.raise_for_status()
            data = response.json()
            return data['venta']
        except requests.RequestException as e:
            logger.error(f"Error al obtener la tasa de cambio USD: {e}")
            return None
