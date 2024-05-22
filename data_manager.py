from utils import format_price_for_display, format_filename, format_link_to_markdown
from config import DATA_DIRECTORY, CSV_SEPARATOR
import pandas as pd
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

    def fetch_usd_exchange_rate(self):
        try:
            response = requests.get("https://dolarapi.com/v1/dolares/blue")
            response.raise_for_status()
            data = response.json()
            return data['venta']
        except requests.RequestException as e:
            logger.error(f"Error al obtener la tasa de cambio USD: {e}")
            return None

    def convert_price(self):
        if 'price' not in self.df.columns:
            return

        logger.info("Inicio de la conversión de precios.")
        exchange_rate = self.fetch_usd_exchange_rate()
        if exchange_rate is None:
            logger.error("No se pudo obtener la tasa de cambio USD para la conversión.")
            return

        logger.info(f"Tasa de cambio obtenida: {exchange_rate}")

        self.df['price'] = self.df['price'].astype(str)
        self.df[['price_pesos', 'price_usd']] = self.df.apply(lambda row: self.convert_single_price(row['price'], exchange_rate), axis=1)

        self.df['price_pesos'] = pd.to_numeric(self.df['price_pesos'], errors='coerce')
        self.df['price_usd'] = pd.to_numeric(self.df['price_usd'], errors='coerce')
        logger.info("Conversión de precios completada.")

    def convert_single_price(self, value, exchange_rate):
        if "U$S" in value:
            number = float(value.replace("U$S", "").replace(".", "").strip())
            converted_value_pesos = number * exchange_rate
            return pd.Series([converted_value_pesos, number])
        else:
            number = float(value.replace("$", "").replace(".", "").strip())
            converted_value_usd = round(number / exchange_rate)
            return pd.Series([number, converted_value_usd])

    def remove_empty_columns(self, df, columns):
        for column in columns:
            if column in df.columns and df[column].isnull().all():
                logger.info(f"Eliminando columna vacía: {column}")
                df.drop(columns=[column], inplace=True)
        return df

    def process_and_convert_products(self, products):
        # Convertir lista de productos en DataFrame
        self.df = pd.DataFrame(products)

        # Aplicar conversiones de precio
        self.convert_price()

        # Eliminar columnas con todos los valores None
        self.df = self.remove_empty_columns(self.df, ['envio', 'cuotas'])

        # Generar columnas para la visualización
        columns = self.generate_columns(self.df.to_dict('records'))

        return self.df.to_dict('records'), columns
