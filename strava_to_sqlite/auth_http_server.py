"""Simple HTTP server to handle the OAuth2 redirect"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib.parse import urlparse, parse_qs


class AuthHTTPRequestHandler(BaseHTTPRequestHandler):
    """Handler for OAuth callback"""

    def _set_headers(self):
        """Set response headers"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):  # pylint: disable=invalid-name
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        authorization_code = query["code"][0]
        self.server.set_app_data("authorization_code", authorization_code)
        self._set_headers()
        self.wfile.write(bytes("received get request", "utf-8"))
        # h/t
        # https://stackoverflow.com/questions/19040055/how-do-i-shutdown-an-httpserver-from-inside-a-request-handler-in-python pylint: disable=line-too-long
        threading.Thread(target=self.server.shutdown, daemon=True).start()


class DataSavingHTTPServer(HTTPServer):
    """A simple HTTP server that allows storing simple data"""

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self._app_data = {}

    def set_app_data(self, key, val):
        """Set a data element for later use"""
        self._app_data[key] = val

    def get_app_data(self, key):
        """Retrieve a data element"""
        return self._app_data[key]
