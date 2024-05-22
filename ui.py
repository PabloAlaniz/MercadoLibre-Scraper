import dash_bootstrap_components as dbc
from dash import html, dash_table
from dash import dcc
import plotly.express as px
from utils import clean_km


def load_index_html():
    with open('templates/main_template.html', 'r') as file:
        return file.read()


def create_layout():
    layout = dbc.Container(
        [
            dbc.Row([
                dbc.Col([
                    html.H1("ML Scraper", className="text-center p-5"),
                    dbc.Input(id="input-product", placeholder="Ingresa el nombre del producto...", type="text"),
                    html.Br(),
                    dbc.Button("Buscar", id="btn-scrape", n_clicks=0),
                    dbc.Alert(id="scrape-message", color="primary", is_open=False),
                    html.Div(id="scrape-progress"),  # Agrega este elemento para mostrar el progreso
                    html.Br(),
                    html.Div(id='trigger-for-detailed-scrape', style={'display': 'none'}),
                    html.Br(),
                    html.Div(id='temp-data-storage', style={'display': 'none'}),
                    html.Div(id='table-initial-container', children=[dash_table.DataTable(id='table-initial', columns=[], data=[])]),
                    dash_table.DataTable(
                        id='table-detailed',
                        columns=[],
                        data=[],
                        filter_action='native',
                        sort_action='native',
                        sort_mode='multi'
                    ),
                    html.Div(id='scatter-plot-container')
                ], width=12),
            ]),
            html.Script(src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/3.0.3/socket.io.js"),
            html.Script("""
                // Your JavaScript code to listen to SocketIO events and update the scrape-progress element
                var socket = io.connect('http://127.0.0.1:5000');
                socket.on('scrape_status', function(data) {
                    document.getElementById('scrape-progress').innerText =
                        'Scrape Progress: ' + data.progress + '/' + data.total;
                });
            """),
        ],
        fluid=True,
    )
    return dcc.Loading(layout, type="circle")


def create_scatter_plot(data, x_col, y_col, color_col, labels, title):
    if x_col not in data.columns or y_col not in data.columns or color_col not in data.columns:
        return html.Div("Una o más columnas especificadas no están presentes en los datos.", style={'color': 'red'})

    if x_col == 'km':
        data['km'] = data['km'].apply(clean_km)

    fig = px.scatter(data, x=x_col, y=y_col, color=color_col,
                     labels=labels, title=title)
    return dcc.Graph(figure=fig)
