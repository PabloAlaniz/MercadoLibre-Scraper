"""Composition root — wires adapters, use cases, and services together."""
from dataclasses import dataclass

from application.use_cases.search_products import SearchProductsUseCase
from application.use_cases.get_product_details import GetProductDetailsUseCase
from application.services.price_conversion import PriceConversionService
from presentation.dash_presenter import DashPresenter


@dataclass
class ApplicationServices:
    """Holds all application-level services required by the presentation layer."""
    search_products: SearchProductsUseCase
    get_product_details: GetProductDetailsUseCase
    price_conversion: PriceConversionService
    presenter: DashPresenter


class Container:
    """Factory methods for assembling the application in different contexts."""

    @staticmethod
    def _create_scraper(retailer: str, notifier, config=None):
        if retailer == 'mercadolibre':
            from scrapers.mercadolibre.mercadolibre_scraper import MercadoLibreScraper
            return MercadoLibreScraper(progress_notifier=notifier, config=config)
        raise ValueError(f"Unknown retailer: {retailer}")

    @staticmethod
    def create_for_dashboard(retailer: str = 'mercadolibre') -> ApplicationServices:
        from flask_socketio import SocketIO
        from config import SCRAPER_CONFIG, DATA_DIRECTORY, CSV_SEPARATOR
        from infrastructure.adapters.socketio_notifier import SocketIOProgressNotifier
        from infrastructure.adapters.dolarapi_client import DolarApiExchangeRate
        from infrastructure.adapters.csv_exporter import CsvProductExporter

        # Import the socketio instance created in dashboard.py
        from dashboard import socketio

        notifier = SocketIOProgressNotifier(socketio)
        scraper = Container._create_scraper(retailer, notifier, SCRAPER_CONFIG)
        exchange_rate = DolarApiExchangeRate()
        exporter = CsvProductExporter(DATA_DIRECTORY, CSV_SEPARATOR)

        return ApplicationServices(
            search_products=SearchProductsUseCase(scraper=scraper, exporter=exporter),
            get_product_details=GetProductDetailsUseCase(scraper=scraper),
            price_conversion=PriceConversionService(exchange_rate_provider=exchange_rate),
            presenter=DashPresenter(exchange_rate_provider=exchange_rate),
        )

    @staticmethod
    def create_for_cli(retailer: str = 'mercadolibre') -> ApplicationServices:
        from infrastructure.adapters.null_notifier import NullProgressNotifier
        from infrastructure.adapters.dolarapi_client import DolarApiExchangeRate
        from infrastructure.adapters.csv_exporter import CsvProductExporter

        notifier = NullProgressNotifier()
        scraper = Container._create_scraper(retailer, notifier)
        exchange_rate = DolarApiExchangeRate()
        exporter = CsvProductExporter("data", ";")

        return ApplicationServices(
            search_products=SearchProductsUseCase(scraper=scraper, exporter=exporter),
            get_product_details=GetProductDetailsUseCase(scraper=scraper),
            price_conversion=PriceConversionService(exchange_rate_provider=exchange_rate),
            presenter=DashPresenter(exchange_rate_provider=exchange_rate),
        )

    @staticmethod
    def create_for_api(retailer: str = 'mercadolibre') -> ApplicationServices:
        from infrastructure.adapters.null_notifier import NullProgressNotifier
        from infrastructure.adapters.dolarapi_client import DolarApiExchangeRate

        notifier = NullProgressNotifier()
        scraper = Container._create_scraper(retailer, notifier)
        exchange_rate = DolarApiExchangeRate()

        return ApplicationServices(
            search_products=SearchProductsUseCase(scraper=scraper),
            get_product_details=GetProductDetailsUseCase(scraper=scraper),
            price_conversion=PriceConversionService(exchange_rate_provider=exchange_rate),
            presenter=DashPresenter(exchange_rate_provider=exchange_rate),
        )
