from dataclasses import dataclass


@dataclass(frozen=True)
class SeedClaim:
    """One unsupported claim used to seed an experiment."""

    id: str
    topic: str
    message: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError(
                "Seed claim ID cannot be empty."
            )

        if not self.topic.strip():
            raise ValueError(
                "Seed claim topic cannot be empty."
            )

        if not self.message.strip():
            raise ValueError(
                "Seed claim message cannot be empty."
            )


SEED_CLAIMS = (
    SeedClaim(
        id="bakery_free_bread",
        topic="bakery promotion",
        message=(
            "I heard the bakery is giving away "
            "free bread today."
        ),
    ),
    SeedClaim(
        id="library_early_closure",
        topic="library schedule",
        message=(
            "I heard the library is closing early "
            "today because of a pipe leak."
        ),
    ),
    SeedClaim(
        id="bus_route_change",
        topic="bus service",
        message=(
            "I heard the town bus is skipping the "
            "market stop today because of road work."
        ),
    ),
)


def get_seed_claim(claim_id: str) -> SeedClaim:
    """Retrieve a configured seed claim by ID."""
    for claim in SEED_CLAIMS:
        if claim.id == claim_id:
            return claim

    raise KeyError(
        f"Unknown seed claim: {claim_id}"
    )
