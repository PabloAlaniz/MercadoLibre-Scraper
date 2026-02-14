"""Use case: search for products on MercadoLibre."""
from __future__ import annotations

from typing import TYPE_CHECKING

from log_config import get_logger

if TYPE_CHECKING:
    from domain.ports import ScraperPort, ProductExporterPort

logger = get_logger(__name__)


class SearchProductsUseCase:
    """Orchestrates a product search: scrape listings and optionally export."""

    def __init__(self, scraper: ScraperPort, exporter: ProductExporterPort = None):
        self.scraper = scraper
        self.exporter = exporter

    def execute(self, domain: str, product_name: str, limit: int) -> list[dict]:
        results = self.scraper.scrape_product_list(domain, product_name, limit)

        if self.exporter and results:
            self.exporter.export(results, product_name)

        return results
