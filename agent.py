from dataclasses import dataclass, field

from memory import Memory, MemorySource, MemoryStream


@dataclass
class Agent:
    """An individual agent with a personality and private memories."""

    name: str
    personality: str
    memories: MemoryStream = field(
        default_factory=MemoryStream,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.personality = self.personality.strip()

        if not self.name:
            raise ValueError("Agent name cannot be empty.")

        if not self.personality:
            raise ValueError("Agent personality cannot be empty.")

    def remember(
        self,
        content: str,
        importance: int,
        source: MemorySource,
    ) -> Memory:
        """Create and store a new private memory."""
        memory = Memory(
            content=content,
            importance=importance,
            source=source,
        )
        self.memories.add(memory)
        return memory

    def observe(
        self,
        event: str,
        importance: int,
    ) -> Memory:
        """Store something the agent directly observed."""
        return self.remember(
            content=event,
            importance=importance,
            source="observation",
        )

    def hear(
        self,
        speaker: "Agent",
        message: str,
        importance: int,
        interpretation: str | None = None,
    ) -> Memory:
        """Store the listener's memory of another agent's statement."""
        cleaned_message = message.strip()

        if not cleaned_message:
            raise ValueError("Dialogue message cannot be empty.")

        if interpretation is None:
            memory_content = (
                f'{speaker.name} said: "{cleaned_message}"'
            )
        else:
            cleaned_interpretation = interpretation.strip()

            if not cleaned_interpretation:
                raise ValueError(
                    "Dialogue interpretation cannot be empty."
                )

            memory_content = (
                f"{speaker.name} said something I interpreted as: "
                f'"{cleaned_interpretation}"'
            )

        return self.remember(
            content=memory_content,
            importance=importance,
            source="dialogue",
        )

    def recall(
        self,
        context: str,
        limit: int = 5,
    ) -> list[Memory]:
        """Retrieve memories useful to the current context."""
        return self.memories.retrieve(
            query=context,
            limit=limit,
        )
