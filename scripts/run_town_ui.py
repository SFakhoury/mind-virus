from __future__ import annotations

import argparse
from dataclasses import asdict
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import webbrowser

from mind_virus.decision import OpenAIDecisionMaker, TransmissionDecision
from mind_virus.town_session import TownSession


HOST = "127.0.0.1"
PORT = 8000
UI_DIRECTORY = Path(__file__).resolve().parent.parent / "town_ui"


def simulation_decision(listener, speaker, message):
    """Free deterministic mode for UI development."""
    if listener.name == "Bob":
        return TransmissionDecision(
            remembered_message=(
                "Alice asked about a bakery giveaway, but I know from "
                "working there that none was announced."
            ),
            believes_claim=False,
            repeats_claim=False,
            belief_confidence=0.05,
            reason="My firsthand bakery knowledge contradicts the rumor.",
        )
    return TransmissionDecision(
        remembered_message=f"{speaker.name} reported: {message}",
        believes_claim=False,
        repeats_claim=True,
        belief_confidence=0.2,
        reason="The report is memorable but remains unverified.",
    )


def make_handler(session: TownSession, mode: str):
    class TownHandler(SimpleHTTPRequestHandler):
        def send_json(self, payload, status=200):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/api/state":
                self.send_json({"mode": mode, **session.state()})
                return
            super().do_GET()

        def do_POST(self):
            if self.path != "/api/step":
                self.send_json({"error": "Not found."}, 404)
                return
            try:
                turn = session.step()
            except RuntimeError as error:
                self.send_json({"error": str(error)}, 409)
                return
            self.send_json({"turn": asdict(turn), "state": session.state()})

    return partial(TownHandler, directory=str(UI_DIRECTORY))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use paid model-backed listener decisions.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mode = "live-ai" if args.live else "simulation"
    if args.live:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        print("LIVE AI mode can make at most 3 paid API calls.")
        if input("Type RUN to continue: ").strip() != "RUN":
            print("Live town cancelled.")
            return
        decision_maker = OpenAIDecisionMaker()
    else:
        decision_maker = simulation_decision

    session = TownSession(decision_maker)
    server = ThreadingHTTPServer((HOST, PORT), make_handler(session, mode))
    url = f"http://{HOST}:{PORT}"
    print("PHASE 7: PYTHON-BACKED INTERACTIVE TOWN")
    print("-" * 48)
    print(f"Mode: {mode}")
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
