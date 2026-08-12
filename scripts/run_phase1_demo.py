from mind_virus.agent import Agent
from mind_virus.conversation import Conversation


def personality_interpreter(
    listener: Agent,
    speaker: Agent,
    message: str,
) -> str:
    """Temporary deterministic interpreter for the Phase 1 demo."""
    cleaned_message = message.rstrip(".")

    return (
        f"{speaker.name} reported that {cleaned_message}. "
        f"Because I am {listener.personality.lower()}, "
        "I should remember the report from my own perspective."
    )


def main() -> None:
    alice = Agent(
        name="Alice",
        personality="Friendly, curious, and observant",
    )
    bob = Agent(
        name="Bob",
        personality="Reserved, cautious, and analytical",
    )

    alice.observe(
        event="The bakery was unusually crowded this morning.",
        importance=7,
    )

    alice_recall = alice.recall(
        context="What happened at the bakery?",
        limit=1,
    )
    spoken_message = alice_recall[0].content

    conversation = Conversation(
        interpreter=personality_interpreter,
    )
    bob_memory = conversation.deliver(
        speaker=alice,
        listener=bob,
        message=spoken_message,
        importance=6,
    )

    bob_recall = bob.recall(
        context="What did Alice report about the bakery?",
        limit=1,
    )

    print("PHASE 1: CORE AGENT LOOP")
    print("-" * 40)
    print(f"Alice observed: {spoken_message}")
    print(f'Alice says: "{spoken_message}"')
    print(f"Bob remembers: {bob_memory.content}")
    print(f"Bob later recalls: {bob_recall[0].content}")
    print("-" * 40)
    print(f"Alice memory count: {len(alice.memories)}")
    print(f"Bob memory count: {len(bob.memories)}")
    print("Phase 1 loop completed successfully.")


if __name__ == "__main__":
    main()

