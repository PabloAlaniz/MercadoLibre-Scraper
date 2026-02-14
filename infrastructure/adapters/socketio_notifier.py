"""SocketIO adapter for ProgressNotifierPort."""


class SocketIOProgressNotifier:
    """Notifies scraping progress via SocketIO websocket events."""

    def __init__(self, socketio_instance):
        self.socketio = socketio_instance

    def notify_progress(self, current: int, total: int) -> None:
        self.socketio.emit('scrape_status', {'progress': current, 'total': total})
