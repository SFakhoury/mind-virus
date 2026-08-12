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
from mind_virus.town_dialogue import (
    OpenAITownDialogueMaker,
    TownDialogue,
)
from mind_virus.world import build_default_world


HOST = "127.0.0.1"
PORT = 8000
UI_DIRECTORY = Path(__file__).resolve().parent.parent / "town_ui"
SESSION_OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "results"
    / "town_session_latest.json"
)
WORLD_OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "results"
    / "town_world_latest.json"
)


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


def simulation_dialogue(speaker, listener):
    exchanges = {
        "Bob": (
            "The bakery rumor was incorrect, so I clarified what I know firsthand.",
            "That correction is more reliable than the original secondhand report.",
        ),
        "Charlie": (
            "I recorded the correction at the library information desk.",
            "Good. Residents should be able to distinguish the correction from the rumor.",
        ),
        "Dana": (
            "The bus stop inspection is scheduled for tomorrow morning.",
            "I will include that confirmed update in my town notes.",
        ),
    }
    first, reply = exchanges[speaker.name]
    return TownDialogue(
        speaker_message=first,
        listener_reply=reply,
        topic="town update",
        references_rumor="rumor" in first.lower(),
    )


def usage_summary(decision_maker, dialogue_maker):
    usages = [
        getattr(decision_maker, "usage", None),
        getattr(dialogue_maker, "usage", None),
    ]
    calls = sum(usage.calls for usage in usages if usage is not None)
    input_tokens = sum(
        usage.input_tokens for usage in usages if usage is not None
    )
    output_tokens = sum(
        usage.output_tokens for usage in usages if usage is not None
    )
    estimated_cost = sum(
        usage.estimated_cost_usd for usage in usages if usage is not None
    )
    return {
        "calls": calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": estimated_cost,
    }


def make_handler(
    session: TownSession,
    world,
    mode: str,
    decision_maker,
    dialogue_maker,
):
    def snapshot():
        usage = usage_summary(decision_maker, dialogue_maker)
        session.save(SESSION_OUTPUT, mode=mode, usage=usage)
        return {"mode": mode, "usage": usage, **session.state()}

    class TownHandler(SimpleHTTPRequestHandler):
        def send_json(self, payload, status=200):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/api/world":
                self.send_json(world.browser_state())
                return
            if self.path == "/api/state":
                self.send_json(snapshot())
                return
            super().do_GET()

        def do_POST(self):
            if self.path == "/api/world/tick":
                world.tick(5)
                world.save(WORLD_OUTPUT)
                self.send_json(world.browser_state())
                return
            if self.path == "/api/chat":
                try:
                    chat = session.chat(dialogue_maker)
                except RuntimeError as error:
                    self.send_json({"error": str(error)}, 409)
                    return
                self.send_json({"chat": chat, "state": snapshot()})
                return
            if self.path != "/api/step":
                self.send_json({"error": "Not found."}, 404)
                return
            try:
                turn = session.step()
            except RuntimeError as error:
                self.send_json({"error": str(error)}, 409)
                return
            self.send_json({"turn": asdict(turn), "state": snapshot()})

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
        print("LIVE AI mode can make at most 4 paid API calls.")
        if input("Type RUN to continue: ").strip() != "RUN":
            print("Live town cancelled.")
            return
        decision_maker = OpenAIDecisionMaker()
        dialogue_maker = OpenAITownDialogueMaker()
    else:
        decision_maker = simulation_decision
        dialogue_maker = simulation_dialogue

    session = TownSession(decision_maker)
    world = build_default_world()
    server = ThreadingHTTPServer(
        (HOST, PORT),
        make_handler(
            session,
            world,
            mode,
            decision_maker,
            dialogue_maker,
        ),
    )
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
