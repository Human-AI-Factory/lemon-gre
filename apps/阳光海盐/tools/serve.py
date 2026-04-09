from __future__ import annotations

import argparse
import os
import socket
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
RELEASE_ROOT = SCRIPT_PATH.parents[1]
WEB_ROOT = RELEASE_ROOT / "web"


class ThemeHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "application/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml",
        ".webmanifest": "application/manifest+json; charset=utf-8",
    }

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def get_local_ips() -> list[str]:
    ips: set[str] = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                ips.add(ip)
    except OSError:
        pass

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if not ip.startswith("127."):
                ips.add(ip)
    except OSError:
        pass

    return sorted(ips)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve release assets.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=43123)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()

    handler = partial(ThemeHandler, directory=os.fspath(WEB_ROOT))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    local_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    local_url = f"http://{local_host}:{args.port}/index.html"

    print(f"Serving {WEB_ROOT}")
    print(f"Local: {local_url}")
    if args.host == "0.0.0.0":
        for ip in get_local_ips():
            print(f"LAN:   http://{ip}:{args.port}/index.html")

    if args.open:
        webbrowser.open(local_url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
