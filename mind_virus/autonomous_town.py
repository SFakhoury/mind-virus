from __future__ import annotations

from dataclasses import asdict, dataclass

from mind_virus.agent import Agent
from mind_virus.conversation_planning import plan_grounded_conversation
from mind_virus.memory_context import ConversationContext
from mind_virus.world import WorldState, build_default_world


@dataclass(frozen=True)
class AutonomousConversation:
    minute: int
    day: int
    speaker: str
    listener: str
    location_id: str
    location_name: str
    topic: str
    message: str
    retrieval_query: str
    supporting_memory_ids: tuple[str, ...]


class AutonomousTown:
    """Coordinate persistent world encounters with agents' private memories."""

    def __init__(
        self,
        world: WorldState | None = None,
        agents: dict[str, Agent] | None = None,
    ) -> None:
        self.world = world if world is not None else build_default_world()
        self.agents = agents if agents is not None else build_default_agents()
        missing = set(self.world.residents) - set(self.agents)
        if missing:
            raise ValueError(
                f"Missing cognitive agents for residents: {sorted(missing)}"
            )
        self.conversations: list[AutonomousConversation] = []
        self._event_cursor = 0

    def tick(self, minutes: int = 1) -> list[AutonomousConversation]:
        self.world.tick(minutes)
        return self.process_new_interactions()

    def process_new_interactions(self) -> list[AutonomousConversation]:
        """Turn newly recorded world interactions into grounded dialogue."""
        new_conversations: list[AutonomousConversation] = []
        events = self.world.event_log[self._event_cursor:]
        self._event_cursor = len(self.world.event_log)
        for event in events:
            if event.get("type") != "interaction":
                continue
            names = event.get("residents")
            if not isinstance(names, list) or len(names) != 2:
                raise ValueError("Interaction event must contain two residents.")
            speaker = self.agents[str(names[0])]
            listener = self.agents[str(names[1])]
            location_id = str(event["location"])
            location_name = self.world.locations[location_id].name
            topic = "current town events"
            context = ConversationContext(
                partner_name=listener.name,
                location_name=location_name,
                activity="conversation",
                topic=topic,
            )
            plan = plan_grounded_conversation(
                speaker,
                listener,
                context,
            )
            listener.hear(
                speaker,
                plan.proposed_message,
                importance=4,
                interpretation=plan.proposed_message,
            )
            conversation = AutonomousConversation(
                minute=int(event["minute"]),
                day=int(event["day"]),
                speaker=speaker.name,
                listener=listener.name,
                location_id=location_id,
                location_name=location_name,
                topic=plan.topic,
                message=plan.proposed_message,
                retrieval_query=plan.retrieval_query,
                supporting_memory_ids=plan.memory_ids,
            )
            self.conversations.append(conversation)
            new_conversations.append(conversation)
        return new_conversations

    def browser_state(self) -> dict[str, object]:
        state = self.world.browser_state()
        state["autonomous_conversations"] = [
            asdict(conversation) for conversation in self.conversations[-20:]
        ]
        return state


def build_default_agents() -> dict[str, Agent]:
    return {
        "Alice": Agent(
            "Alice",
            "A careful local reporter who attributes sources clearly.",
        ),
        "Bob": Agent(
            "Bob",
            "A bakery worker with firsthand knowledge of bakery operations.",
        ),
        "Charlie": Agent(
            "Charlie",
            "A sociable librarian who distinguishes reports from facts.",
        ),
        "Dana": Agent(
            "Dana",
            "A skeptical town planner who seeks direct evidence.",
        ),
    }
