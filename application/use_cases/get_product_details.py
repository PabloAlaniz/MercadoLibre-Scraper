"""Use case: get detailed information for a list of product URLs."""
from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from log_config import get_logger

if TYPE_CHECKING:
    from domain.ports import ScraperPort

logger = get_logger(__name__)


class GetProductDetailsUseCase:
    """Orchestrates fetching product detail pages (optionally threaded)."""

    def __init__(self, scraper: ScraperPort):
        self.scraper = scraper

    def execute(self, urls: list[str], threaded: bool = True) -> list[dict]:
        if threaded:
            return self._execute_threaded(urls)
        return self._execute_sequential(urls)

    def _get_single_detail(self, url: str):
        soup = self.scraper.get_page_content(url)
        if not soup:
            return None
        return self.scraper.scrape_product_details(soup)

    def _execute_sequential(self, urls: list[str]) -> list[dict]:
        products = []
        for url in urls:
            product = self._get_single_detail(url)
            if product:
                products.append(product)
        return products

    def _execute_threaded(self, urls: list[str]) -> list[dict]:
        products = []
        lock = threading.Lock()

        def _fetch(url):
            product = self._get_single_detail(url)
            if product:
                with lock:
                    products.append(product)

        threads = [threading.Thread(target=_fetch, args=(url,)) for url in urls]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        return products
