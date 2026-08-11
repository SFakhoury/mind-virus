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
