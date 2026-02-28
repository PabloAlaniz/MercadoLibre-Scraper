import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.py"


def _load_real_config():
    spec = importlib.util.spec_from_file_location("real_config", CONFIG_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_config_constants_from_file():
    config = _load_real_config()

    assert config.DATA_DIRECTORY == "data"
    assert config.CSV_SEPARATOR == ";"
    assert config.SERVER_CONFIG["debug"] is True
    assert config.SERVER_CONFIG["allow_unsafe_werkzeug"] is True
    assert config.SERVER_CONFIG["port"] == 5003


def test_scraper_config_defaults():
    config = _load_real_config()

    assert config.SCRAPER_CONFIG["base_url"].startswith("https://listado.mercadolibre.com")
    assert config.SCRAPER_CONFIG["page_increment"] == 50
    assert config.SCRAPER_CONFIG["max_pages"] == 100
