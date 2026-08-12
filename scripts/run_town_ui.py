from __future__ import annotations

import argparse
from dataclasses import asdict
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import webbrowser
from threading import Lock

from mind_virus.autonomous_town import AutonomousTown
from mind_virus.api_auth import APIAuthenticator
from mind_virus.background_jobs import BackgroundJobQueue
from mind_virus.decision import OpenAIDecisionMaker, TransmissionDecision
from mind_virus.town_session import TownSession
from mind_virus.production_store import ProductionStore
from mind_virus.live_sync import LiveStateBroker
from mind_virus.observability import OperationalMetrics, production_logger
from mind_virus.town_dialogue import (
    OpenAITownDialogueMaker,
    TownDialogue,
)


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
DATABASE_OUTPUT = Path(__file__).resolve().parent.parent / "results" / "mind_virus.db"
LOG_OUTPUT = Path(__file__).resolve().parent.parent / "results" / "mind_virus.log.jsonl"
API_VERSION = "v1"


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
    town: AutonomousTown,
    mode: str,
    decision_maker,
    dialogue_maker,
    experience: str = "autonomous-town",
    store: ProductionStore | None = None,
    authenticator: APIAuthenticator | None = None,
    jobs: BackgroundJobQueue | None = None,
):
    broker = LiveStateBroker()
    mutation_lock = Lock()
    metrics = OperationalMetrics()
    logger = production_logger(LOG_OUTPUT)

    def snapshot():
        usage = usage_summary(decision_maker, dialogue_maker)
        session.save(SESSION_OUTPUT, mode=mode, usage=usage)
        payload = {
            "mode": mode,
            "experience": experience,
            "usage": usage,
            **session.state(),
        }
        if store is not None:
            store.save_current_state(mode, payload)
        return payload

    class TownHandler(SimpleHTTPRequestHandler):
        def authorized(self) -> bool:
            auth = authenticator or APIAuthenticator()
            if auth.authorize(self.headers.get("X-Mind-Virus-Token")):
                return True
            self.send_json({"error": "Authentication required."}, 401)
            return False

        def send_json(self, payload, status=200):
            metrics.increment("responses_total")
            if status >= 400:
                metrics.increment("errors_total")
            logger.info("http_response", extra={"context": {"path": self.path, "status": status}})
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path.startswith("/api/v1/jobs/"):
                job_id = self.path.rsplit("/", 1)[-1]
                status = jobs.status(job_id) if jobs else None
                self.send_json(status or {"error": "Job not found."}, 200 if status else 404)
                return
            if self.path == "/api/v1/events":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                revision = -1
                try:
                    while True:
                        revision, payload = broker.wait_for_update(revision)
                        event = "data: " + json.dumps(payload or {"heartbeat": True}) + "\n\n"
                        self.wfile.write(event.encode("utf-8"))
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            if self.path == "/api/v1/health":
                health = store.health() if store else {"status": "ok", "database": "disabled"}
                self.send_json({"api_version": API_VERSION, **health,
                                "queue": jobs.metrics() if jobs else {}})
                return
            if self.path == "/api/v1/metrics":
                self.send_json({**metrics.snapshot(), "queue": jobs.metrics() if jobs else {}})
                return
            if self.path == "/api/v1/state":
                self.send_json(snapshot())
                return
            if self.path == "/api/v1/state/latest":
                saved = store.load_current_state() if store else None
                if saved is None:
                    self.send_json({"error": "No persisted town state exists."}, 404)
                else:
                    self.send_json(saved)
                return
            if self.path == "/api/world":
                self.send_json(town.browser_state())
                return
            if self.path == "/api/state":
                self.send_json(snapshot())
                return
            super().do_GET()

        def do_POST(self):
            metrics.increment("mutation_requests_total")
            path = self.path.removeprefix("/api/v1") if self.path.startswith("/api/v1/") else self.path
            if mode == "live-ai" and path in ("/api/chat", "/api/step") and not self.authorized():
                metrics.increment("authentication_failures_total")
                return
            if path == "/jobs/step":
                if jobs is None or not self.authorized():
                    return
                try:
                    job_id = jobs.submit(lambda: self.run_step())
                except RuntimeError as error:
                    self.send_json({"error": str(error)}, 503)
                    return
                self.send_json({"job_id": job_id, "status": "queued"}, 202)
                return
            if path == "/api/world/tick":
                with mutation_lock:
                    town.tick(5)
                    town.world.save(WORLD_OUTPUT)
                    world = town.browser_state()
                    broker.publish({"state": snapshot(), "world": world})
                self.send_json(world)
                return
            if path == "/api/chat":
                try:
                    with mutation_lock:
                        chat = session.chat(dialogue_maker)
                        state = snapshot()
                        broker.publish({"state": state, "world": town.browser_state()})
                except RuntimeError as error:
                    self.send_json({"error": str(error)}, 409)
                    return
                self.send_json({"chat": chat, "state": state})
                return
            if path != "/api/step":
                self.send_json({"error": "Not found."}, 404)
                return
            try:
                result = self.run_step()
            except RuntimeError as error:
                self.send_json({"error": str(error)}, 409)
                return
            self.send_json(result)

        def run_step(self):
            with mutation_lock:
                turn = session.step()
                state = snapshot()
                broker.publish({"state": state, "world": town.browser_state()})
                return {"turn": asdict(turn), "state": state}

    return partial(TownHandler, directory=str(UI_DIRECTORY))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use paid model-backed listener decisions.",
    )
    parser.add_argument(
        "--research-demo",
        action="store_true",
        help="Run the legacy controlled rumor-propagation UI sequence.",
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Require authenticated paid routes and production settings.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mode = "live-ai" if args.live else "simulation"
    experience = (
        "legacy-research-demo"
        if args.research_demo or args.live
        else "autonomous-town"
    )
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
    town = AutonomousTown()
    store = ProductionStore(DATABASE_OUTPUT)
    authenticator = APIAuthenticator.from_environment(required=args.production)
    jobs = BackgroundJobQueue()
    server = ThreadingHTTPServer(
        (HOST, PORT),
        make_handler(
            session,
            town,
            mode,
            decision_maker,
            dialogue_maker,
            experience,
            store,
            authenticator,
            jobs,
        ),
    )
    url = f"http://{HOST}:{PORT}"
    print("PHASE 7: PYTHON-BACKED INTERACTIVE TOWN")
    print("-" * 48)
    print(f"Mode: {mode}")
    print(f"Experience: {experience}")
    print(f"Open: {url}")
    print("Press Ctrl+C to stop the town server.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nTown server stopped.")
    finally:
        server.server_close()
        jobs.shutdown()


if __name__ == "__main__":
    main()
