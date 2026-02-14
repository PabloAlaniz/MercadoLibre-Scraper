"""Dash presentation layer — formats scraping data for Dash DataTable display."""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from utils import format_price_for_display, format_link_to_markdown
import pandas as pd
from log_config import get_logger
from dash.dash_table import DataTable, FormatTemplate

if TYPE_CHECKING:
    from domain.ports import ExchangeRatePort

logger = get_logger(__name__)


class DashPresenter:

    def __init__(self, exchange_rate_provider: ExchangeRatePort):
        self.df = pd.DataFrame()
        self.exchange_rate_provider = exchange_rate_provider

    def prepare_table_data(self, data: list[dict]) -> tuple[list[dict], list[dict]]:
        self.df = pd.DataFrame(data)
        columns = []
        if not self.df.empty:
            self.convert_price()

            if 'post_link' in self.df.columns:
                self.df['post_link'] = self.df['post_link'].apply(format_link_to_markdown)

            sort_column = 'price' if 'price' in self.df.columns else self.df.columns[0]
            sorted_df = self.df.sort_values(by=sort_column, ascending=True)

            if 'price' in sorted_df.columns:
                sorted_df["price"] = sorted_df["price"].apply(format_price_for_display)

                money = FormatTemplate.money(2)

                columns = [
                    {'name': 'Title', 'id': 'title', 'type': 'text'},
                    {'name': 'Price', 'id': 'price', 'type': 'text'},
                    {'name': 'Price in Pesos', 'id': 'price_pesos', 'type': 'text'},
                    {"name": "Price in USD", "id": "price_usd", "type": "numeric", "format": money},
                    {'name': 'Link', 'id': 'post_link', 'type': 'text', 'presentation': 'markdown'},
                    {'name': 'Image', 'id': 'image_link', 'type': 'text'}
                ]

                data = sorted_df.to_dict('records')

                logger.info("DATA: ")
                logger.info(data)

        return data, columns

    def generate_columns(self, data: list[dict]) -> list[dict]:
        columns = []
        for key in data[0].keys():
            if "link" in key.lower():
                columns.append({'name': key.capitalize(), 'id': key, 'type': 'text', 'presentation': 'markdown', 'sortable': True})
            else:
                columns.append({'name': key.capitalize(), 'id': key, 'sortable': True})
        return columns

    def fetch_usd_exchange_rate(self) -> Optional[float]:
        return self.exchange_rate_provider.get_usd_to_ars_rate()

    def convert_price(self) -> None:
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

    def convert_single_price(self, value: str, exchange_rate: float) -> pd.Series:
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

    def process_and_convert_products(self, products: list[dict]) -> tuple[list[dict], list[dict]]:
        self.df = pd.DataFrame(products)
        self.convert_price()
        self.df = self.remove_empty_columns(self.df, ['shipping', 'cuotas'])
        columns = self.generate_columns(self.df.to_dict('records'))
        return self.df.to_dict('records'), columns
