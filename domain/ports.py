"""
Port interfaces (Protocol classes) for the MercadoLibre Scraper domain.

These define the contracts that adapters must satisfy. Using Protocol
means existing classes automatically satisfy the interface without
changing their inheritance — duck typing with static checking.
"""
from __future__ import annotations

from typing import Protocol, Any, Optional


class ScraperPort(Protocol):
    """Interface for web scraping operations."""

    def get_page_content(self, url: str) -> Any:
        """Fetch and parse a web page."""
        ...

    def scrape_product_list(
        self, domain: str, product_name: str, user_scraping_limit: int
    ) -> list[dict]:
        """Scrape product listings from search results."""
        ...

    def scrape_product_details(self, soup: Any) -> dict:
        """Scrape details from a product detail page."""
        ...


class ExchangeRatePort(Protocol):
    """Interface for fetching currency exchange rates."""

    def get_usd_to_ars_rate(self) -> Optional[float]:
        """Get the current USD to ARS exchange rate."""
        ...


class ProgressNotifierPort(Protocol):
    """Interface for notifying scraping progress."""

    def notify_progress(self, current: int, total: int) -> None:
        """Notify progress update."""
        ...


class ProductExporterPort(Protocol):
    """Interface for exporting product data."""

    def export(self, data: list[dict], product_name: str) -> None:
        """Export product data (e.g., to CSV)."""
        ...
