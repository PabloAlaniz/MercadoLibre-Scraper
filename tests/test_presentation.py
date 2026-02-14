"""Tests for DashPresenter (presentation layer)."""
import pytest
from unittest.mock import Mock, MagicMock


class TestDashPresenter:
    """Tests for DashPresenter class."""

    def _make_presenter(self, exchange_rate=1000.0):
        from presentation.dash_presenter import DashPresenter

        mock_provider = Mock()
        mock_provider.get_usd_to_ars_rate.return_value = exchange_rate
        return DashPresenter(exchange_rate_provider=mock_provider)

    def test_fetch_usd_exchange_rate(self):
        presenter = self._make_presenter(exchange_rate=1200.0)
        rate = presenter.fetch_usd_exchange_rate()
        assert rate == 1200.0

    def test_convert_single_price_ars(self):
        import pandas as pd
        presenter = self._make_presenter()

        result = presenter.convert_single_price("$ 100.000", 1000.0)
        assert isinstance(result, pd.Series)
        assert result[0] == 100000.0  # price_pesos
        assert result[1] == 100  # price_usd

    def test_convert_single_price_usd(self):
        import pandas as pd
        presenter = self._make_presenter()

        result = presenter.convert_single_price("U$S 15.000", 1000.0)
        assert isinstance(result, pd.Series)
        assert result[0] == 15000000.0  # price_pesos
        assert result[1] == 15000.0  # price_usd

    def test_remove_empty_columns(self):
        import pandas as pd
        presenter = self._make_presenter()

        df = pd.DataFrame({
            'title': ['Product 1'],
            'price': ['100'],
            'shipping': [None],
        })
        result = presenter.remove_empty_columns(df, ['shipping'])
        assert 'shipping' not in result.columns
        assert 'title' in result.columns

    def test_remove_empty_columns_keeps_non_empty(self):
        import pandas as pd
        presenter = self._make_presenter()

        df = pd.DataFrame({
            'title': ['Product 1'],
            'shipping': ['Llega mañana'],
        })
        result = presenter.remove_empty_columns(df, ['shipping'])
        assert 'shipping' in result.columns

    def test_generate_columns(self):
        presenter = self._make_presenter()

        data = [{'title': 'Test', 'price': '100', 'post_link': 'http://example.com'}]
        columns = presenter.generate_columns(data)

        assert len(columns) == 3
        link_col = next(c for c in columns if c['id'] == 'post_link')
        assert link_col['presentation'] == 'markdown'

    def test_process_and_convert_products(self):
        presenter = self._make_presenter()

        products = [
            {'title': 'Product 1', 'price': '$ 100.000', 'shipping': None},
        ]
        data, columns = presenter.process_and_convert_products(products)

        assert len(data) == 1
        assert 'price_pesos' in data[0]
        assert 'price_usd' in data[0]
        # shipping column should be removed (all None)
        assert 'shipping' not in data[0]
