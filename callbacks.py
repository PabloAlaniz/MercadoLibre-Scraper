from dash.dependencies import Output, Input, State
from utils import extract_url_from_markdown
from log_config import get_logger
import pandas as pd
import json
import ui
logger = get_logger(__name__)


def register_callbacks(app, services):
    @app.callback(
        [Output("scrape-message", "children"),
         Output("scrape-message", "is_open"),
         Output('table-initial', 'data'),
         Output('table-initial', 'columns'),
         Output('trigger-for-detailed-scrape', 'children'),
         Output('temp-data-storage', 'children')
         ],
        [Input("btn-scrape", "n_clicks")],
        [State("input-product", "value")]
    )
    def run_scrape(n_clicks, input_product_name):
        if n_clicks > 0 and input_product_name:
            data = services.search_products.execute('ar', input_product_name, 100)
            if data:
                message = f"Scraping para {input_product_name} completado!"
            else:
                message = f"No se encontraron datos para {input_product_name}."
            msg_open = True
            data, columns = services.presenter.prepare_table_data(data or [])
            trigger = 'updated'
            json_data = json.dumps(data)
            logger.info(f"Cantidad de datos: {len(data)}")
        else:
            message, msg_open, data, columns, json_data = "", False, [], [], None
            trigger = None

        return message, msg_open, data, columns, trigger, json_data

    @app.callback(
        [Output('table-detailed', 'data'),
         Output('table-detailed', 'columns'),
         Output('table-initial-container', 'style')
        ],
        [Input('trigger-for-detailed-scrape', 'children')],
        [State('temp-data-storage', 'children')]
    )
    def run_scrape_detailed(trigger, json_data):
        if trigger and json_data:
            table_data = json.loads(json_data)
            urls = [extract_url_from_markdown(row['post_link']) for row in table_data]
            products = services.get_product_details.execute(urls)
            products, columns = services.presenter.process_and_convert_products(products)
            return products, columns, {'display': 'none'}
        else:
            return [], [], {'display': 'block'}

    @app.callback(
        Output('scatter-plot-container', 'children'),
        [Input('table-detailed', 'data')]
    )
    def update_scatter_plot(data):
        if data:
            df = pd.DataFrame(data)
            scatter_plot = ui.create_scatter_plot(
                df,
                x_col='km',
                y_col='price_usd',
                color_col='year',
                labels={"km": "Kilómetros", "price_usd": "Precio (USD)", "year": "Año"},
                title="Relación entre Precio, Kilómetros y Año del Auto")
            return scatter_plot
        return None
