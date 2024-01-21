import http.server
import socketserver
import threading
import time
import subprocess
import os
import palworld_utils
from dotenv import load_dotenv

load_dotenv()

metrics = {}
flag = False


class PalWorldRequestHandler(http.server.BaseHTTPRequestHandler):
    global metrics

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

        self.wfile.write(b"# HELP palworld_active_users_count The number of active users in palworld server.\n")
        self.wfile.write(b"# TYPE palworld_active_users_count gauge\n")
        value = str(metrics["palworld_active_users_count"]).encode()
        self.wfile.write(b"palworld_active_users_count " + value + b"\n")


def update():
    global metrics
    global flag

    while True:
        sleep_to = time.time() + 5.0

        metrics["palworld_active_users_count"] = palworld_utils.get_active_user_count()

        while time.time() < sleep_to:
            if flag:
                return
            time.sleep(1.0)


if __name__ == "__main__":
    print("starting palworld-exporter")
    thread = threading.Thread(target=update)
    thread.start()

    Handler = PalWorldRequestHandler
    host = os.getenv("EXPORTER_HOST")
    port = os.getenv("EXPORTER_PORT")
    with socketserver.TCPServer((host, int(port)), Handler) as httpd:
        print(f"serving at http://{host}:{port}")
        httpd.serve_forever()

    flag = True

