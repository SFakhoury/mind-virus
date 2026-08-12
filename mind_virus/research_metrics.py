from __future__ import annotations

from dataclasses import dataclass
import re
from statistics import mean


@dataclass(frozen=True)
class MutationMetrics:
    transmissions: int
    final_similarity: float
    average_step_similarity: float
    retained_terms: tuple[str, ...]
    lost_terms: tuple[str, ...]
    introduced_terms: tuple[str, ...]


@dataclass(frozen=True)
class CalibrationMetrics:
    observations: int
    brier_score: float
    expected_calibration_error: float


@dataclass(frozen=True)
class NetworkPropagationMetrics:
    exposed_agents: int
    reach_fraction: float
    maximum_generation: int
    unique_transmission_edges: int
    edge_coverage: float


def measure_claim_mutation(messages: list[str]) -> MutationMetrics:
    """Measure lexical preservation and mutation along one claim lineage."""
    if not messages:
        raise ValueError("At least one claim message is required.")
    token_sets = [_terms(message) for message in messages]
    similarities = [
        _jaccard(left, right)
        for left, right in zip(token_sets, token_sets[1:])
    ]
    original = token_sets[0]
    final = token_sets[-1]
    return MutationMetrics(
        transmissions=len(messages) - 1,
        final_similarity=_jaccard(original, final),
        average_step_similarity=mean(similarities) if similarities else 1.0,
        retained_terms=tuple(sorted(original & final)),
        lost_terms=tuple(sorted(original - final)),
        introduced_terms=tuple(sorted(final - original)),
    )


def measure_calibration(
    confidences: list[float],
    outcomes: list[bool | int],
    *,
    bins: int = 5,
) -> CalibrationMetrics:
    """Measure probabilistic belief calibration with Brier score and ECE."""
    if len(confidences) != len(outcomes) or not confidences:
        raise ValueError("Confidence and outcome samples must be nonempty and paired.")
    if bins < 1:
        raise ValueError("Calibration bins must be positive.")
    if any(not 0.0 <= value <= 1.0 for value in confidences):
        raise ValueError("Confidence values must be between 0 and 1.")
    if any(value not in (0, 1, False, True) for value in outcomes):
        raise ValueError("Calibration outcomes must be binary.")
    numeric = [int(value) for value in outcomes]
    brier = mean((confidence - outcome) ** 2
                 for confidence, outcome in zip(confidences, numeric))
    error = 0.0
    for index in range(bins):
        low = index / bins
        high = (index + 1) / bins
        members = [
            position for position, confidence in enumerate(confidences)
            if low <= confidence < high or (index == bins - 1 and confidence == 1.0)
        ]
        if members:
            average_confidence = mean(confidences[position] for position in members)
            empirical_rate = mean(numeric[position] for position in members)
            error += len(members) / len(confidences) * abs(
                average_confidence - empirical_rate
            )
    return CalibrationMetrics(len(confidences), brier, error)


def measure_network_propagation(
    *,
    exposed_nodes: set[int],
    total_nodes: int,
    transmission_edges: list[tuple[int, int]],
    total_network_edges: int,
    maximum_generation: int,
) -> NetworkPropagationMetrics:
    if total_nodes < 1 or total_network_edges < 1:
        raise ValueError("Network size and edge count must be positive.")
    if not exposed_nodes.issubset(set(range(total_nodes))):
        raise ValueError("Exposed nodes must belong to the network.")
    if maximum_generation < 0:
        raise ValueError("Maximum generation cannot be negative.")
    unique_edges = {
        tuple(sorted(edge)) for edge in transmission_edges
    }
    if any(left == right for left, right in unique_edges):
        raise ValueError("Transmission edges cannot be self-loops.")
    if len(unique_edges) > total_network_edges:
        raise ValueError("Transmissions cannot cover more edges than the network contains.")
    return NetworkPropagationMetrics(
        exposed_agents=len(exposed_nodes),
        reach_fraction=len(exposed_nodes) / total_nodes,
        maximum_generation=maximum_generation,
        unique_transmission_edges=len(unique_edges),
        edge_coverage=len(unique_edges) / total_network_edges,
    )


def _terms(message: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", message.casefold()))


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0
