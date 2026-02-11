"""
Pytest configuration and fixtures for MercadoLibre-Scraper tests.

Mocks heavy dependencies to allow unit testing without full stack.
"""
import sys
from unittest.mock import Mock, MagicMock

# Mock heavy dependencies before they're imported
mock_flask = MagicMock()
mock_flask.Flask = MagicMock()
sys.modules['flask'] = mock_flask

mock_socketio = MagicMock()
sys.modules['flask_socketio'] = mock_socketio

mock_dash = MagicMock()
sys.modules['dash'] = mock_dash
sys.modules['dash_bootstrap_components'] = mock_dash

# Mock config module with test values
mock_config = MagicMock()
mock_config.socketio = MagicMock()
mock_config.SCRAPER_CONFIG = {
    'base_url': 'https://listado.mercadolibre.com.{domain}/',
    'page_increment': 50,
    'max_pages': 10
}
mock_config.DATA_DIRECTORY = './data'
mock_config.CSV_SEPARATOR = ','
sys.modules['config'] = mock_config

# DO NOT mock utils - it's internal code we want to test for real
# (tests in test_utils.py need real implementations)

# Mock log_config
mock_log_config = MagicMock()
mock_log_config.get_logger = lambda x: MagicMock()
sys.modules['log_config'] = mock_log_config
