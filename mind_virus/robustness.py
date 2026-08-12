from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random

from mind_virus.experiment_spec import GeneralizedExperimentSpec


@dataclass(frozen=True)
class RobustnessSpec:
    models: tuple[str, ...]
    prompt_variants: tuple[str, ...]
    temperatures: tuple[float, ...]
    repetitions_per_cell: int = 1

    def __post_init__(self) -> None:
        if not self.models or any(not item.strip() for item in self.models):
            raise ValueError("At least one named model is required.")
        if len(set(self.models)) != len(self.models):
            raise ValueError("Model names must be unique.")
        if not self.prompt_variants or any(
            not item.strip() for item in self.prompt_variants
        ):
            raise ValueError("At least one named prompt variant is required.")
        if len(set(self.prompt_variants)) != len(self.prompt_variants):
            raise ValueError("Prompt variants must be unique.")
        if not self.temperatures:
            raise ValueError("At least one temperature is required.")
        if len(set(self.temperatures)) != len(self.temperatures):
            raise ValueError("Temperatures must be unique.")
        if any(not 0.0 <= value <= 2.0 for value in self.temperatures):
            raise ValueError("Temperatures must be between 0 and 2.")
        if self.repetitions_per_cell < 1:
            raise ValueError("Repetitions per robustness cell must be positive.")

    @property
    def cell_count(self) -> int:
        return (
            len(self.models)
            * len(self.prompt_variants)
            * len(self.temperatures)
            * self.repetitions_per_cell
        )


@dataclass(frozen=True)
class RobustnessCell:
    execution_index: int
    cell_id: str
    model: str
    prompt_variant: str
    temperature: float
    repetition: int
    seed: int
    experiment_fingerprint: str


@dataclass(frozen=True)
class RobustnessManifest:
    experiment_fingerprint: str
    cells: tuple[RobustnessCell, ...]

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return output


def build_robustness_manifest(
    experiment: GeneralizedExperimentSpec,
    robustness: RobustnessSpec,
) -> RobustnessManifest:
    cells: list[RobustnessCell] = []
    for model in robustness.models:
        for prompt in robustness.prompt_variants:
            for temperature in robustness.temperatures:
                for repetition in range(robustness.repetitions_per_cell):
                    label = f"{model}|{prompt}|{temperature:.3f}|{repetition}"
                    digest = hashlib.sha256(
                        f"{experiment.seed}|{experiment.fingerprint}|{label}".encode("utf-8")
                    ).digest()
                    cells.append(
                        RobustnessCell(
                            -1,
                            hashlib.sha256(label.encode("utf-8")).hexdigest()[:12],
                            model,
                            prompt,
                            temperature,
                            repetition,
                            int.from_bytes(digest[:8], "big"),
                            experiment.fingerprint,
                        )
                    )
    order_seed = int.from_bytes(
        hashlib.sha256(
            f"{experiment.seed}|{experiment.fingerprint}|robustness-order".encode("utf-8")
        ).digest()[:8],
        "big",
    )
    random.Random(order_seed).shuffle(cells)
    ordered = tuple(
        RobustnessCell(**{**asdict(cell), "execution_index": index})
        for index, cell in enumerate(cells)
    )
    return RobustnessManifest(experiment.fingerprint, ordered)
