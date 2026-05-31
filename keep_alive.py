"""
Keep-alive web server for Replit — prevents the repl from sleeping.
Use with UptimeRobot to ping the URL every 5 minutes.
"""
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Mafia Bot ishlayapti!")
    def log_message(self, *args):
        pass  # Suppress logs

def run():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
