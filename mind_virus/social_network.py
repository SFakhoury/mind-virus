from __future__ import annotations

from dataclasses import dataclass
import random

from mind_virus.experiment_spec import NetworkSpec


Edge = tuple[int, int]


@dataclass(frozen=True)
class SocialNetwork:
    structure: str
    nodes: tuple[int, ...]
    edges: tuple[Edge, ...]

    def __post_init__(self) -> None:
        node_set = set(self.nodes)
        if len(node_set) != len(self.nodes):
            raise ValueError("Network nodes must be unique.")
        if any(left == right for left, right in self.edges):
            raise ValueError("Social networks cannot contain self-loops.")
        if any(left not in node_set or right not in node_set for left, right in self.edges):
            raise ValueError("Every edge endpoint must be a network node.")
        if len(set(self.edges)) != len(self.edges):
            raise ValueError("Social-network edges must be unique.")

    def neighbors(self, node: int) -> tuple[int, ...]:
        if node not in self.nodes:
            raise KeyError(f"Unknown network node: {node}")
        connected = {
            right if left == node else left
            for left, right in self.edges
            if left == node or right == node
        }
        return tuple(sorted(connected))

    @property
    def is_connected(self) -> bool:
        visited = {self.nodes[0]}
        pending = [self.nodes[0]]
        while pending:
            current = pending.pop()
            for neighbor in self.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    pending.append(neighbor)
        return len(visited) == len(self.nodes)


def build_social_network(spec: NetworkSpec, seed: int) -> SocialNetwork:
    """Build a deterministic undirected network from an experiment spec."""
    nodes = tuple(range(spec.town_size))
    if spec.structure == "chain":
        edges = [(node, node + 1) for node in nodes[:-1]]
    elif spec.structure == "ring":
        edges = _ring_edges(spec.town_size)
    elif spec.structure == "complete":
        edges = [
            (left, right)
            for left in nodes
            for right in nodes
            if left < right
        ]
    else:
        edges = _connected_small_world(
            spec.town_size, spec.rewiring_probability, seed
        )
    return SocialNetwork(spec.structure, nodes, tuple(sorted(edges)))


def _ring_edges(size: int) -> list[Edge]:
    return sorted({_edge(node, (node + 1) % size) for node in range(size)})


def _connected_small_world(size: int, probability: float, seed: int) -> list[Edge]:
    original = _ring_edges(size)
    if size < 4 or probability == 0.0:
        return original
    for attempt in range(100):
        rng = random.Random(f"{seed}:{attempt}")
        edges = set(original)
        for left, right in original:
            if rng.random() >= probability:
                continue
            without_current = edges - {_edge(left, right)}
            occupied = {
                other if first == left else first
                for first, other in without_current
                if first == left or other == left
            }
            candidates = [
                node for node in range(size)
                if node != left and node not in occupied
            ]
            if candidates:
                edges.remove(_edge(left, right))
                edges.add(_edge(left, rng.choice(candidates)))
        candidate = SocialNetwork("small_world", tuple(range(size)), tuple(sorted(edges)))
        if candidate.is_connected:
            return list(candidate.edges)
    return original


def _edge(left: int, right: int) -> Edge:
    return (left, right) if left < right else (right, left)
