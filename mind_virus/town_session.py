from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

from .agent import Agent
from .decision import TransmissionDecision
from .town_dialogue import TownDialogue


DecisionMaker = Callable[[Agent, Agent, str], TransmissionDecision]


@dataclass(frozen=True)
class TownTurn:
    speaker: str
    listener: str
    message: str
    remembered_message: str
    believes_claim: bool
    repeats_claim: bool
    belief_confidence: float
    reason: str
    generation: int


class TownSession:
    """Stateful bridge between research agents and the browser town."""

    def __init__(self, decision_maker: DecisionMaker) -> None:
        if not callable(decision_maker):
            raise TypeError("Decision maker must be callable.")

        self._decision_maker = decision_maker
        self.agents = [
            Agent(
                "Alice",
                "A careful local reporter who attributes sources clearly.",
            ),
            Agent(
                "Bob",
                "The bakery worker. He knows no giveaway was announced and corrects unsupported bakery claims.",
            ),
            Agent(
                "Charlie",
                "A sociable librarian who discusses interesting reports but distinguishes rumors from facts.",
            ),
            Agent(
                "Dana",
                "A skeptical town planner who seeks direct evidence before accepting claims.",
            ),
        ]
        self.agents[1].observe(
            "I work at Sunrise Bakery, and no free-bread giveaway was announced.",
            importance=9,
        )
        self.original_message = (
            "I heard the bakery is giving away free bread today."
        )
        self.current_message = self.original_message
        self.generation = 0
        self.turns: list[TownTurn] = []
        self.stopped = False
        self.chat_count = 0

    def step(self) -> TownTurn:
        if self.stopped:
            raise RuntimeError("The claim is no longer being repeated.")
        if self.generation >= len(self.agents) - 1:
            raise RuntimeError("The claim reached the final agent.")

        speaker = self.agents[self.generation]
        listener = self.agents[self.generation + 1]
        decision = self._decision_maker(
            listener,
            speaker,
            self.current_message,
        )

        listener.hear(
            speaker=speaker,
            message=self.current_message,
            importance=6,
            interpretation=decision.remembered_message,
        )
        self.generation += 1
        turn = TownTurn(
            speaker=speaker.name,
            listener=listener.name,
            message=self.current_message,
            remembered_message=decision.remembered_message,
            believes_claim=decision.believes_claim,
            repeats_claim=decision.repeats_claim,
            belief_confidence=decision.belief_confidence,
            reason=decision.reason,
            generation=self.generation,
        )
        self.turns.append(turn)
        self.stopped = not decision.repeats_claim
        if decision.repeats_claim:
            self.current_message = decision.remembered_message
        return turn

    def state(self) -> dict[str, object]:
        return {
            "generation": self.generation,
            "stopped": self.stopped,
            "current_message": self.current_message,
            "agents": [
                {
                    "name": agent.name,
                    "personality": agent.personality,
                    "memory_count": len(agent.memories),
                }
                for agent in self.agents
            ],
            "turns": [asdict(turn) for turn in self.turns],
            "chat_count": self.chat_count,
        }

    def chat(self, dialogue_maker) -> dict[str, object]:
        """Generate and remember one post-propagation conversation."""
        if self.chat_count >= 3:
            raise RuntimeError("The three-conversation limit was reached.")
        pair_index = self.chat_count % 3
        pairs = ((1, 2), (2, 3), (3, 0))
        speaker_index, listener_index = pairs[pair_index]
        speaker = self.agents[speaker_index]
        listener = self.agents[listener_index]
        dialogue: TownDialogue = dialogue_maker(speaker, listener)
        speaker.remember(dialogue.speaker_message, 4, "dialogue")
        listener.hear(
            speaker,
            dialogue.speaker_message,
            importance=4,
            interpretation=dialogue.listener_reply,
        )
        self.chat_count += 1
        return {
            "speaker": speaker.name,
            "listener": listener.name,
            **dialogue.model_dump(),
            "chat_number": self.chat_count,
        }
