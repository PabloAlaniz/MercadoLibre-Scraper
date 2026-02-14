"""Tests for infrastructure adapters."""
import os
import tempfile

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestNullProgressNotifier:
    """NullProgressNotifier should silently discard all notifications."""

    def test_notify_progress_does_nothing(self):
        from infrastructure.adapters.null_notifier import NullProgressNotifier

        notifier = NullProgressNotifier()
        # Should not raise
        notifier.notify_progress(5, 10)

    def test_satisfies_protocol(self):
        from infrastructure.adapters.null_notifier import NullProgressNotifier

        notifier = NullProgressNotifier()
        assert hasattr(notifier, 'notify_progress')
        assert callable(notifier.notify_progress)


class TestSocketIOProgressNotifier:
    """SocketIOProgressNotifier should emit events via socketio."""

    def test_notify_progress_emits_event(self):
        from infrastructure.adapters.socketio_notifier import SocketIOProgressNotifier

        mock_socketio = Mock()
        notifier = SocketIOProgressNotifier(mock_socketio)

        notifier.notify_progress(3, 10)

        mock_socketio.emit.assert_called_once_with(
            'scrape_status', {'progress': 3, 'total': 10}
        )

    def test_multiple_notifications(self):
        from infrastructure.adapters.socketio_notifier import SocketIOProgressNotifier

        mock_socketio = Mock()
        notifier = SocketIOProgressNotifier(mock_socketio)

        notifier.notify_progress(1, 5)
        notifier.notify_progress(2, 5)
        notifier.notify_progress(3, 5)

        assert mock_socketio.emit.call_count == 3


class TestDolarApiExchangeRate:
    """DolarApiExchangeRate should fetch from dolarapi.com."""

    def test_get_rate_success(self):
        from infrastructure.adapters.dolarapi_client import DolarApiExchangeRate

        client = DolarApiExchangeRate()

        with patch('infrastructure.adapters.dolarapi_client.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'venta': 1200.0}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            rate = client.get_usd_to_ars_rate()

            assert rate == 1200.0
            mock_get.assert_called_once_with("https://dolarapi.com/v1/dolares/blue")

    def test_get_rate_returns_none_on_error(self):
        from infrastructure.adapters.dolarapi_client import DolarApiExchangeRate
        import requests

        client = DolarApiExchangeRate()

        with patch('infrastructure.adapters.dolarapi_client.requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException('Network error')

            rate = client.get_usd_to_ars_rate()

            assert rate is None


class TestCsvProductExporter:
    """CsvProductExporter should write CSV files."""

    def test_export_creates_file(self):
        from infrastructure.adapters.csv_exporter import CsvProductExporter

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = CsvProductExporter(tmpdir, ';')

            data = [
                {'title': 'Product 1', 'price': '100'},
                {'title': 'Product 2', 'price': '200'},
            ]
            exporter.export(data, 'test product')

            expected_file = os.path.join(tmpdir, 'test-product.csv')
            assert os.path.exists(expected_file)

    def test_export_creates_directory_if_missing(self):
        from infrastructure.adapters.csv_exporter import CsvProductExporter

        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, 'new_subdir')
            exporter = CsvProductExporter(subdir, ';')

            data = [{'title': 'Product 1', 'price': '100'}]
            exporter.export(data, 'test')

            assert os.path.exists(subdir)
            assert os.path.exists(os.path.join(subdir, 'test.csv'))

    def test_export_uses_correct_separator(self):
        from infrastructure.adapters.csv_exporter import CsvProductExporter

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = CsvProductExporter(tmpdir, '|')

            data = [{'title': 'Product 1', 'price': '100'}]
            exporter.export(data, 'test')

            file_path = os.path.join(tmpdir, 'test.csv')
            with open(file_path) as f:
                content = f.read()
            assert '|' in content
