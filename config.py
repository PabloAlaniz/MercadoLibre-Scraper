"""Application configuration constants.

Flask server and SocketIO are created in dashboard.py, not here.
"""
import dash_bootstrap_components as dbc

EXTERNAL_STYLESHEETS = [dbc.themes.BOOTSTRAP]
DATA_DIRECTORY = "data"
CSV_SEPARATOR = ";"
SERVER_CONFIG = {
    "debug": True,
    "allow_unsafe_werkzeug": True,
    "port": 5003
}
SCRAPER_CONFIG = {
    'base_url': 'https://listado.mercadolibre.com.{domain}/',
    'page_increment': 50,
    'max_pages': 100
}
