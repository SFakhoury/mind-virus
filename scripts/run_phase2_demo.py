from mind_virus.agent import Agent
from mind_virus.claim import Claim


def main() -> None:
    alice = Agent("Alice", "Observant")
    bob = Agent("Bob", "Trusting")
    charlie = Agent("Charlie", "Skeptical")

    original = Claim(
        content="The bakery is giving away free bread.",
        source_agent=alice.name,
        confidence=0.85,
    )

    bob.hear(
        speaker=alice,
        message=original.content,
        importance=7,
    )
    bob_belief = bob.consider_claim(
        original,
        acceptance_threshold=0.5,
    )

    repeated = bob.repeat_claim(
        topic_id=original.topic_id,
        content="The bakery probably has free bread.",
        confidence=0.65,
    )

    charlie.hear(
        speaker=bob,
        message=repeated.content,
        importance=5,
    )
    charlie_belief = charlie.consider_claim(
        repeated,
        acceptance_threshold=0.8,
    )

    print("PHASE 2: STRUCTURED CLAIM PROPAGATION")
    print("-" * 45)
    print(f"Topic: {original.topic_id}")
    print(f"Generation 0: {original.content}")
    print(f"Bob accepted: {bob_belief is not None}")
    print(f"Generation 1: {repeated.content}")
    print(f"Charlie accepted: {charlie_belief is not None}")
    print(f"Lineage preserved: {repeated.parent_id == original.id}")
    print("-" * 45)
    print("Phase 2 completed successfully.")


if __name__ == "__main__":
    main()

