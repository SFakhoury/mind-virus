from __future__ import annotations

from dataclasses import asdict, dataclass

from mind_virus.agent import Agent
from mind_virus.autonomous_interpretation import interpret_autonomous_message
from mind_virus.claim import Claim
from mind_virus.conversation_planning import plan_grounded_conversation
from mind_virus.memory_context import ConversationContext
from mind_virus.reflection import reflect_on_memories
from mind_virus.topic_selection import select_conversation_topic
from mind_virus.planning import DailyPlan, create_daily_plan
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
    topic_source_memory_ids: tuple[str, ...]
    topic_reason: str
    message: str
    retrieval_query: str
    supporting_memory_ids: tuple[str, ...]
    speaker_memory_id: str
    listener_memory_id: str
    claim_id: str
    topic_id: str
    listener_interpretation: str
    listener_believes: bool
    listener_repeats: bool
    listener_confidence: float
    listener_reason: str
    listener_relevant_memory_ids: tuple[str, ...]


@dataclass(frozen=True)
class AutonomousReflection:
    minute: int
    day: int
    agent: str
    topic: str
    memory_id: str
    source_memory_ids: tuple[str, ...]
    content: str


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
        self.reflections: list[AutonomousReflection] = []
        self.daily_plans: list[DailyPlan] = []
        self._event_cursor = 0

    def tick(self, minutes: int = 1) -> list[AutonomousConversation]:
        if minutes < 1:
            raise ValueError("Tick duration must be at least one minute.")
        for _ in range(minutes):
            self._ensure_daily_plans()
            self.world.tick()
        return self.process_new_interactions()

    def _ensure_daily_plans(self) -> None:
        for name, resident in self.world.residents.items():
            if resident.daily_goal_day == self.world.day:
                continue
            plan = create_daily_plan(
                self.agents[name],
                resident,
                self.world.locations,
                self.world.day,
            )
            resident.daily_goal_day = plan.day
            resident.daily_goal = plan.goal
            resident.goal_destination_id = plan.destination_id
            resident.goal_activity = plan.activity
            resident.goal_source = plan.source
            resident.goal_reason = plan.reason
            resident.goal_memory_ids = plan.source_memory_ids
            self.daily_plans.append(plan)

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
            selected_topic = select_conversation_topic(
                speaker,
                partner_name=listener.name,
                location_name=location_name,
                activity="conversation",
            )
            topic = selected_topic.label
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
            relationship_trust = self.world.residents[
                listener.name
            ].relationships.get(speaker.name, 0.5)
            interpretation = interpret_autonomous_message(
                listener,
                speaker,
                plan.proposed_message,
                supporting_memory_ids=plan.memory_ids,
                relationship_trust=relationship_trust,
            )
            claim = Claim(
                content=plan.proposed_message,
                source_agent=speaker.name,
                confidence=0.8 if plan.memory_ids else 0.3,
            )
            if interpretation.believes_message:
                listener.consider_claim(
                    claim,
                    acceptance_threshold=interpretation.acceptance_threshold,
                    belief_confidence=interpretation.confidence,
                )
            speaker_memory = speaker.remember(
                f'I told {listener.name}: "{plan.proposed_message}"',
                4,
                "dialogue",
                related_memory_ids=plan.memory_ids,
            )
            listener_memory = listener.hear(
                speaker,
                plan.proposed_message,
                importance=4,
                interpretation=interpretation.remembered_message,
                related_memory_ids=plan.memory_ids,
            )
            conversation = AutonomousConversation(
                minute=int(event["minute"]),
                day=int(event["day"]),
                speaker=speaker.name,
                listener=listener.name,
                location_id=location_id,
                location_name=location_name,
                topic=plan.topic,
                topic_source_memory_ids=selected_topic.source_memory_ids,
                topic_reason=selected_topic.reason,
                message=plan.proposed_message,
                retrieval_query=plan.retrieval_query,
                supporting_memory_ids=plan.memory_ids,
                speaker_memory_id=speaker_memory.id,
                listener_memory_id=listener_memory.id,
                claim_id=claim.id,
                topic_id=claim.topic_id,
                listener_interpretation=interpretation.remembered_message,
                listener_believes=interpretation.believes_message,
                listener_repeats=interpretation.repeats_message,
                listener_confidence=interpretation.confidence,
                listener_reason=interpretation.reason,
                listener_relevant_memory_ids=interpretation.relevant_memory_ids,
            )
            self.conversations.append(conversation)
            new_conversations.append(conversation)
            self._reflect_if_ready(speaker, topic)
            self._reflect_if_ready(listener, topic)
        return new_conversations

    def _reflect_if_ready(self, agent: Agent, topic: str) -> None:
        reflection = reflect_on_memories(agent, topic)
        if reflection is None or any(
            item.memory_id == reflection.id for item in self.reflections
        ):
            return
        self.reflections.append(
            AutonomousReflection(
                minute=self.world.absolute_minute,
                day=self.world.day,
                agent=agent.name,
                topic=topic,
                memory_id=reflection.id,
                source_memory_ids=reflection.related_memory_ids,
                content=reflection.content,
            )
        )

    def browser_state(self) -> dict[str, object]:
        state = self.world.browser_state()
        state["autonomous_conversations"] = [
            asdict(conversation) for conversation in self.conversations[-20:]
        ]
        state["autonomous_reflections"] = [
            asdict(reflection) for reflection in self.reflections[-20:]
        ]
        state["daily_plans"] = [asdict(plan) for plan in self.daily_plans[-20:]]
        return state


def build_default_agents() -> dict[str, Agent]:
    agents = {
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
    agents["Dana"].observe(
        "At Town Hall, I review public plans and current town events.",
        importance=5,
    )
    return agents
