from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random
from typing import Literal


ReviewLabel = Literal["supported", "unsupported", "unclear"]


@dataclass(frozen=True)
class RawOutputRecord:
    record_id: str
    model: str
    condition: str
    claim_id: str
    prompt_context: str
    model_output: str

    def __post_init__(self) -> None:
        if not self.record_id.strip() or not self.model_output.strip():
            raise ValueError("Raw-output record ID and output cannot be empty.")


@dataclass(frozen=True)
class BlindedReviewItem:
    review_id: str
    prompt_context: str
    model_output: str


@dataclass(frozen=True)
class ReviewDecision:
    review_id: str
    reviewer_id: str
    label: ReviewLabel
    notes: str = ""

    def __post_init__(self) -> None:
        if self.label not in {"supported", "unsupported", "unclear"}:
            raise ValueError("Unsupported review label.")
        if not self.reviewer_id.strip():
            raise ValueError("Reviewer ID cannot be empty.")


@dataclass(frozen=True)
class ReviewAgreement:
    reviewed_items: int
    exact_agreement: float
    cohens_kappa: float
    disagreements: tuple[str, ...]


def create_blinded_review_packet(
    records: list[RawOutputRecord],
    *,
    seed: int = 2026,
) -> tuple[tuple[BlindedReviewItem, ...], dict[str, dict[str, str]]]:
    if not records:
        raise ValueError("At least one raw output is required.")
    if len({record.record_id for record in records}) != len(records):
        raise ValueError("Raw-output record IDs must be unique.")
    pairs = []
    key: dict[str, dict[str, str]] = {}
    for record in records:
        review_id = hashlib.sha256(
            f"{seed}|{record.record_id}".encode("utf-8")
        ).hexdigest()[:16]
        item = BlindedReviewItem(
            review_id, record.prompt_context, record.model_output
        )
        key[review_id] = {
            "record_id": record.record_id,
            "model": record.model,
            "condition": record.condition,
            "claim_id": record.claim_id,
        }
        pairs.append(item)
    random.Random(seed).shuffle(pairs)
    return tuple(pairs), key


def save_review_packet(
    items: tuple[BlindedReviewItem, ...],
    key: dict[str, dict[str, str]],
    packet_path: str | Path,
    key_path: str | Path,
) -> tuple[Path, Path]:
    packet_output = Path(packet_path)
    key_output = Path(key_path)
    if packet_output.resolve() == key_output.resolve():
        raise ValueError("The blinded packet and private key require separate files.")
    packet_output.parent.mkdir(parents=True, exist_ok=True)
    key_output.parent.mkdir(parents=True, exist_ok=True)
    packet_output.write_text(
        json.dumps([asdict(item) for item in items], indent=2), encoding="utf-8"
    )
    key_output.write_text(json.dumps(key, indent=2), encoding="utf-8")
    return packet_output, key_output


def measure_review_agreement(
    first: list[ReviewDecision],
    second: list[ReviewDecision],
) -> ReviewAgreement:
    first_by_id = _index_decisions(first)
    second_by_id = _index_decisions(second)
    if set(first_by_id) != set(second_by_id) or not first_by_id:
        raise ValueError("Reviewers must judge the same nonempty set of items.")
    ids = sorted(first_by_id)
    matches = sum(first_by_id[item].label == second_by_id[item].label for item in ids)
    observed = matches / len(ids)
    labels = ("supported", "unsupported", "unclear")
    expected = sum(
        sum(first_by_id[item].label == label for item in ids) / len(ids)
        * sum(second_by_id[item].label == label for item in ids) / len(ids)
        for label in labels
    )
    kappa = 1.0 if expected == 1.0 and observed == 1.0 else (
        (observed - expected) / (1 - expected) if expected < 1.0 else 0.0
    )
    disagreements = tuple(
        item for item in ids
        if first_by_id[item].label != second_by_id[item].label
    )
    return ReviewAgreement(len(ids), observed, kappa, disagreements)


def _index_decisions(decisions: list[ReviewDecision]) -> dict[str, ReviewDecision]:
    indexed = {decision.review_id: decision for decision in decisions}
    if len(indexed) != len(decisions):
        raise ValueError("A reviewer cannot submit duplicate decisions.")
    return indexed
