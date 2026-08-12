import json
from pathlib import Path

from mind_virus.agent import Agent
from mind_virus.ai_interpreter import OpenAIInterpreter


def main() -> None:
    agents = [
        Agent(
            "Alice",
            "Social, trusting, and enthusiastic",
        ),
        Agent(
            "Bob",
            "Cautious, analytical, and evidence-seeking",
        ),
        Agent(
            "Charlie",
            "Excitable and prone to exaggeration",
        ),
        Agent(
            "Dana",
            "Skeptical and reluctant to accept hearsay",
        ),
    ]

    interpreter = OpenAIInterpreter()
    message = "I heard the bakery is giving away free bread."

    transcript = [
        {
            "generation": 0,
            "speaker": agents[0].name,
            "listener": agents[1].name,
            "message": message,
        }
    ]

    print("LIVE AI PROPAGATION CHAIN")
    print("-" * 60)
    print(f"Generation 0 — Alice: {message}")

    for generation in range(1, len(agents)):
        speaker = agents[generation - 1]
        listener = agents[generation]

        interpretation = interpreter(
            listener=listener,
            speaker=speaker,
            message=message,
        )

        listener.hear(
            speaker=speaker,
            message=message,
            importance=6,
            interpretation=interpretation,
        )

        print(
            f"Generation {generation} — "
            f"{listener.name}: {interpretation}"
        )

        transcript.append(
            {
                "generation": generation,
                "speaker": speaker.name,
                "listener": listener.name,
                "message": interpretation,
            }
        )

        message = interpretation

    output = Path("results/ai_propagation_chain.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(transcript, indent=2),
        encoding="utf-8",
    )

    print("-" * 60)
    print(f"Transcript saved to: {output}")
    print("Live propagation chain completed successfully.")


if __name__ == "__main__":
    main()
