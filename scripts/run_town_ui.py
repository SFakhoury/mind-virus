from __future__ import annotations

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import webbrowser


HOST = "127.0.0.1"
PORT = 8000
UI_DIRECTORY = Path(__file__).resolve().parent.parent / "town_ui"


def main() -> None:
    handler = partial(
        SimpleHTTPRequestHandler,
        directory=str(UI_DIRECTORY),
    )
    server = ThreadingHTTPServer((HOST, PORT), handler)
    url = f"http://{HOST}:{PORT}"

    print("PHASE 7: INTERACTIVE VISUAL TOWN")
    print("-" * 40)
    print(f"Town UI directory: {UI_DIRECTORY}")
    print(f"Open: {url}")
    print("Press Ctrl+C to stop the town server.")

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nTown server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
