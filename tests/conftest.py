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
sys.modules['dash.dash_table'] = mock_dash
sys.modules['dash_bootstrap_components'] = mock_dash

# Mock config module with test values (only constants now)
mock_config = MagicMock()
mock_config.SCRAPER_CONFIG = {
    'base_url': 'https://listado.mercadolibre.com.{domain}/',
    'page_increment': 50,
    'max_pages': 10
}
mock_config.DATA_DIRECTORY = './data'
mock_config.CSV_SEPARATOR = ','
mock_config.EXTERNAL_STYLESHEETS = []
mock_config.SERVER_CONFIG = {"debug": True, "allow_unsafe_werkzeug": True, "port": 5003}
sys.modules['config'] = mock_config

# Mock dashboard module to prevent Flask/SocketIO creation during tests
mock_dashboard = MagicMock()
mock_dashboard.socketio = MagicMock()
mock_dashboard.server = MagicMock()
sys.modules['dashboard'] = mock_dashboard

# Mock log_config
mock_log_config = MagicMock()
mock_log_config.get_logger = lambda x: MagicMock()
sys.modules['log_config'] = mock_log_config
