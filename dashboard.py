"""Dashboard entry point — creates Flask server and Dash app."""
import dash
from flask import Flask
from flask_socketio import SocketIO

from config import SERVER_CONFIG, EXTERNAL_STYLESHEETS
from ui import load_index_html, create_layout
from callbacks import register_callbacks

server = Flask(__name__)
socketio = SocketIO(server)


class Dashboard:
    def __init__(self):
        self.app = dash.Dash(__name__, server=server, external_stylesheets=EXTERNAL_STYLESHEETS)
        self.app.config.suppress_callback_exceptions = True
        self.app.index_string = load_index_html()
        self.app.layout = create_layout()

        # Import Container here to avoid circular imports
        from container import Container
        self.services = Container.create_for_dashboard()
        register_callbacks(self.app, self.services)

    def run(self):
        socketio.run(server, **SERVER_CONFIG)
