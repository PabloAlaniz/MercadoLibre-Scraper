import importlib.util
from pathlib import Path
import logging


ROOT = Path(__file__).resolve().parents[1]
LOG_CONFIG_PATH = ROOT / "log_config.py"


def _load_real_log_config():
    spec = importlib.util.spec_from_file_location("real_log_config", LOG_CONFIG_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_setup_logging_sets_levels():
    log_config = _load_real_log_config()
    log_config.setup_logging()

    assert logging.getLogger("urllib3").level == logging.ERROR
    assert logging.getLogger("werkzeug").level == logging.ERROR
    assert logging.getLogger("socketio").level == logging.WARNING
    assert logging.getLogger("scraper").level == logging.INFO
    assert logging.getLogger("mercadolibre_scraper").level == logging.INFO


def test_get_logger_returns_named_logger_with_config():
    log_config = _load_real_log_config()
    logger = log_config.get_logger("test_logger")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"
