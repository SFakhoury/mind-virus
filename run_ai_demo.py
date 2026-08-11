import os

from agent import Agent
from ai_interpreter import OpenAIInterpreter
from conversation import Conversation


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is not set. "
            "Set it before running the live AI demo."
        )

    alice = Agent(
        name="Alice",
        personality="Excitable, social, and highly trusting",
    )
    bob = Agent(
        name="Bob",
        personality="Cautious, analytical, and evidence-seeking",
    )

    bob.observe(
        event=(
            "The bakery charged normal prices yesterday."
        ),
        importance=7,
    )

    conversation = Conversation(
        interpreter=OpenAIInterpreter(),
    )

    memory = conversation.deliver(
        speaker=alice,
        listener=bob,
        message=(
            "I heard the bakery is giving away free bread."
        ),
        importance=6,
    )

    print("PHASE 4: MODEL-BACKED INTERPRETATION")
    print("-" * 45)
    print(
        'Alice says: "I heard the bakery is giving '
        'away free bread."'
    )
    print(f"Bob privately remembers: {memory.content}")
    print("-" * 45)
    print("Live AI interpretation completed successfully.")


if __name__ == "__main__":
    main()
