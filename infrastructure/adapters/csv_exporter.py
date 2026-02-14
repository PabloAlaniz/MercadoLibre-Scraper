"""CSV adapter for ProductExporterPort."""
import os

import pandas as pd
from log_config import get_logger

logger = get_logger(__name__)


class CsvProductExporter:
    """Exports product data to CSV files."""

    def __init__(self, data_directory: str, csv_separator: str):
        self.data_directory = data_directory
        self.csv_separator = csv_separator

    def export(self, data: list[dict], product_name: str) -> None:
        try:
            filename = f"{product_name.replace(' ', '-')}.csv"
            logger.info(f"Preparando para exportar datos del producto: {product_name}")

            if not os.path.exists(self.data_directory):
                os.makedirs(self.data_directory)
                logger.info(f"Creado el directorio de datos: {self.data_directory}")

            df = pd.DataFrame(data)
            file_path = os.path.join(self.data_directory, filename)

            df.to_csv(file_path, sep=self.csv_separator)
            logger.info(f"Datos exportados exitosamente a {file_path}")

        except Exception as e:
            logger.error(f"Error al exportar datos a CSV: {e}")
