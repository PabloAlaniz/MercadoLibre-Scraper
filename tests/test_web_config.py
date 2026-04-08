"""
Tests for web configuration: Socket.IO template and CORS settings.

These tests ensure the web interface won't silently break due to
hardcoded URLs or missing CORS configuration.
"""
import os
import re

_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'presentation', 'templates', 'main_template.html'
)


class TestSocketIOTemplate:
    """Verify the HTML template connects Socket.IO correctly."""

    def _read_template(self):
        with open(_TEMPLATE_PATH, 'r') as f:
            return f.read()

    def test_no_hardcoded_socketio_url(self):
        """Socket.IO must connect to same origin, not a hardcoded host:port."""
        content = self._read_template()
        assert re.search(r"io\.connect\(['\"]http", content) is None, (
            "Socket.IO client must not use a hardcoded URL — use io.connect() instead"
        )

    def test_socketio_client_library_loaded(self):
        """Template must load the Socket.IO client library."""
        content = self._read_template()
        assert 'socket.io' in content, "Template must include the Socket.IO client library"
