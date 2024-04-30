from utils import format_price_for_display, format_filename, format_link_to_markdown
from config import DATA_DIRECTORY, CSV_SEPARATOR
import pandas as pd
import os
import requests
from log_config import get_logger
from dash.dash_table import DataTable, FormatTemplate


logger = get_logger(__name__)


class DataManager:

    def __init__(self):
        self.df = pd.DataFrame()

    def prepare_table_data(self, data):
        self.df = pd.DataFrame(data)
        columns = []
        if not self.df.empty:
            # Convertir precios de USD a pesos o viceversa
            self.convert_price()  # Asegúrate de llamar a convert_price aquí

            # Aplica formatos específicos si las columnas existen
            if 'post_link' in self.df.columns:
                self.df['post_link'] = self.df['post_link'].apply(format_link_to_markdown)

            # Ordena por una columna común o por la primera columna si 'price' no está presente
            sort_column = 'price' if 'price' in self.df.columns else self.df.columns[0]
            sorted_df = self.df.sort_values(by=sort_column, ascending=True)

            # Aplica formatos específicos si las columnas existen
            if 'price' in sorted_df.columns:
                sorted_df["price"] = sorted_df["price"].apply(format_price_for_display)

                money = FormatTemplate.money(2)

                columns = [
                    {'name': 'Title', 'id': 'title', 'type': 'text'},
                    {'name': 'Price', 'id': 'price', 'type': 'text'},
                    {'name': 'Price in Pesos', 'id': 'price_pesos', 'type': 'text'},
                    {"name": "Price in USD", "id": "price_usd", "type": "numeric", "format": money},
                    {'name': 'Link', 'id': 'post_link', 'type': 'text', 'presentation': 'markdown'},
                    {'name': 'Image', 'id': 'image link', 'type': 'text'}
                ]

                # Convertir el DataFrame a un formato adecuado para Dash DataTable
                data = sorted_df.to_dict('records')

                logger.info("DATA: ")
                logger.info(data)

        return data, columns

    def generate_columns(self, data):
        columns = []
        for key in data[0].keys():
            if "link" in key.lower():  # Detecta si la clave es un enlace
                columns.append({'name': key.capitalize(), 'id': key, 'type': 'text', 'presentation': 'markdown', 'sortable': True})
            else:
                columns.append({'name': key.capitalize(), 'id': key, 'sortable': True})
        return columns

    def load_data(self, product_name):
        try:
            filename = f'{format_filename(product_name)}.csv'
            file_path = os.path.join(DATA_DIRECTORY, filename)
            self.df = pd.read_csv(file_path, sep=CSV_SEPARATOR)
            logger.info(f"Datos cargados exitosamente desde {file_path}")
        except Exception as e:
            logger.error(f"Error al cargar datos desde {file_path}: {e}")

    def fetch_usd_exchange_rate(self):
        try:
            response = requests.get("https://dolarapi.com/v1/dolares/blue")
            data = response.json()
            return data['venta']
        except Exception as e:
            logger.error(f"Error al obtener la tasa de cambio USD: {e}")
            return None

    def convert_price(self):
        if 'price' in self.df.columns:
            logger.info("Inicio de la conversión de precios.")
            exchange_rate = self.fetch_usd_exchange_rate()
            if exchange_rate is not None:
                logger.info(f"Tasa de cambio obtenida: {exchange_rate}")
                self.df['price'] = self.df['price'].astype(str)

                def convert(value):
                    if "U$S" in value:
                        number = float(value.replace("U$S", "").replace(".", "").strip())
                        converted_value_pesos = number * exchange_rate
                        return converted_value_pesos, number  # Retiene el valor en USD
                    else:
                        number = float(value.replace("$", "").replace(".", "").strip())
                        converted_value_usd = round(number / exchange_rate)
                        return number, converted_value_usd  # Retiene el valor en pesos y convierte a USD

                # Aplicar la conversión y asignar los valores convertidos a nuevas columnas
                self.df[['price_pesos', 'price_usd']] = self.df.apply(lambda row: pd.Series(convert(row['price'])),
                                                                      axis=1)

                self.df['price_pesos'] = pd.to_numeric(self.df['price_pesos'], errors='coerce')
                self.df['price_usd'] = pd.to_numeric(self.df['price_usd'], errors='coerce')
                logger.info("Conversión de precios completada.")
            else:
                logger.error("No se pudo obtener la tasa de cambio USD para la conversión.")
    def process_and_convert_products(self, products):
        # Convertir lista de productos en DataFrame
        self.df = pd.DataFrame(products)

        # Aplicar conversiones de precio
        self.convert_price()

        # Generar columnas para la visualización
        columns = self.generate_columns(self.df.to_dict('records'))

        return self.df.to_dict('records'), columns
