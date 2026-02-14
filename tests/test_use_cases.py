"""Tests for application use cases and services."""
import pytest
from unittest.mock import Mock, patch, call


class TestSearchProductsUseCase:
    """Tests for SearchProductsUseCase."""

    def test_execute_calls_scraper(self):
        from application.use_cases.search_products import SearchProductsUseCase

        mock_scraper = Mock()
        mock_scraper.scrape_product_list.return_value = [
            {'title': 'Product 1', 'price': '100'},
        ]

        use_case = SearchProductsUseCase(scraper=mock_scraper)
        result = use_case.execute('ar', 'notebook', 50)

        mock_scraper.scrape_product_list.assert_called_once_with('ar', 'notebook', 50)
        assert len(result) == 1
        assert result[0]['title'] == 'Product 1'

    def test_execute_exports_when_exporter_provided(self):
        from application.use_cases.search_products import SearchProductsUseCase

        mock_scraper = Mock()
        mock_scraper.scrape_product_list.return_value = [{'title': 'P1'}]
        mock_exporter = Mock()

        use_case = SearchProductsUseCase(scraper=mock_scraper, exporter=mock_exporter)
        use_case.execute('ar', 'notebook', 50)

        mock_exporter.export.assert_called_once_with([{'title': 'P1'}], 'notebook')

    def test_execute_does_not_export_when_no_results(self):
        from application.use_cases.search_products import SearchProductsUseCase

        mock_scraper = Mock()
        mock_scraper.scrape_product_list.return_value = []
        mock_exporter = Mock()

        use_case = SearchProductsUseCase(scraper=mock_scraper, exporter=mock_exporter)
        use_case.execute('ar', 'notebook', 50)

        mock_exporter.export.assert_not_called()

    def test_execute_works_without_exporter(self):
        from application.use_cases.search_products import SearchProductsUseCase

        mock_scraper = Mock()
        mock_scraper.scrape_product_list.return_value = [{'title': 'P1'}]

        use_case = SearchProductsUseCase(scraper=mock_scraper)
        result = use_case.execute('ar', 'notebook', 50)

        assert len(result) == 1


class TestGetProductDetailsUseCase:
    """Tests for GetProductDetailsUseCase."""

    def test_execute_sequential(self):
        from application.use_cases.get_product_details import GetProductDetailsUseCase

        mock_scraper = Mock()
        mock_scraper.get_page_content.return_value = Mock()
        mock_scraper.scrape_product_details.return_value = {'title': 'Detail'}

        use_case = GetProductDetailsUseCase(scraper=mock_scraper)
        results = use_case.execute(['url1', 'url2'], threaded=False)

        assert len(results) == 2
        assert mock_scraper.get_page_content.call_count == 2

    def test_execute_threaded(self):
        from application.use_cases.get_product_details import GetProductDetailsUseCase

        mock_scraper = Mock()
        mock_scraper.get_page_content.return_value = Mock()
        mock_scraper.scrape_product_details.return_value = {'title': 'Detail'}

        use_case = GetProductDetailsUseCase(scraper=mock_scraper)
        results = use_case.execute(['url1', 'url2'], threaded=True)

        assert len(results) == 2

    def test_execute_skips_none_soups(self):
        from application.use_cases.get_product_details import GetProductDetailsUseCase

        mock_scraper = Mock()
        mock_scraper.get_page_content.side_effect = [None, Mock()]
        mock_scraper.scrape_product_details.return_value = {'title': 'Detail'}

        use_case = GetProductDetailsUseCase(scraper=mock_scraper)
        results = use_case.execute(['bad_url', 'good_url'], threaded=False)

        assert len(results) == 1


class TestPriceConversionService:
    """Tests for PriceConversionService."""

    def test_convert_ars_prices(self):
        from application.services.price_conversion import PriceConversionService

        mock_provider = Mock()
        mock_provider.get_usd_to_ars_rate.return_value = 1000.0

        service = PriceConversionService(exchange_rate_provider=mock_provider)
        products = [{'price': '$ 100.000', 'title': 'Test'}]

        result = service.convert_prices(products)

        assert result[0]['price_pesos'] == 100000.0
        assert result[0]['price_usd'] == 100

    def test_convert_usd_prices(self):
        from application.services.price_conversion import PriceConversionService

        mock_provider = Mock()
        mock_provider.get_usd_to_ars_rate.return_value = 1000.0

        service = PriceConversionService(exchange_rate_provider=mock_provider)
        products = [{'price': 'U$S 15.000', 'title': 'Test'}]

        result = service.convert_prices(products)

        assert result[0]['price_usd'] == 15000.0
        assert result[0]['price_pesos'] == 15000000.0

    def test_convert_prices_returns_unchanged_on_rate_failure(self):
        from application.services.price_conversion import PriceConversionService

        mock_provider = Mock()
        mock_provider.get_usd_to_ars_rate.return_value = None

        service = PriceConversionService(exchange_rate_provider=mock_provider)
        products = [{'price': '$ 100.000', 'title': 'Test'}]

        result = service.convert_prices(products)

        assert 'price_pesos' not in result[0]
        assert 'price_usd' not in result[0]

    def test_get_exchange_rate(self):
        from application.services.price_conversion import PriceConversionService

        mock_provider = Mock()
        mock_provider.get_usd_to_ars_rate.return_value = 1200.0

        service = PriceConversionService(exchange_rate_provider=mock_provider)
        assert service.get_exchange_rate() == 1200.0


class TestContainerCreation:
    """Tests for Container factory methods."""

    def test_create_for_cli(self):
        from container import Container, ApplicationServices

        services = Container.create_for_cli()

        assert isinstance(services, ApplicationServices)
        assert services.search_products is not None
        assert services.get_product_details is not None
        assert services.price_conversion is not None
        assert services.presenter is not None

    def test_create_for_api(self):
        from container import Container, ApplicationServices

        services = Container.create_for_api()

        assert isinstance(services, ApplicationServices)
        assert services.search_products is not None

    def test_create_for_cli_with_retailer_param(self):
        from container import Container

        services = Container.create_for_cli(retailer='mercadolibre')
        assert services.search_products is not None

    def test_create_for_cli_unknown_retailer_raises(self):
        from container import Container

        with pytest.raises(ValueError, match="Unknown retailer"):
            Container.create_for_cli(retailer='ebay')
