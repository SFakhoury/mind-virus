from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ResultJournal:
    """Append-only experiment journal supporting safe resumption."""

    def __init__(
        self,
        path: str | Path,
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def trial_key(
        claim_id: str,
        condition: str,
        trial: int,
    ) -> str:
        """Create a stable unique key for one condition-trial."""
        if not claim_id.strip():
            raise ValueError(
                "Claim ID cannot be empty."
            )

        if condition not in {
            "baseline",
            "skeptical",
        }:
            raise ValueError(
                "Condition must be baseline or skeptical."
            )

        if trial < 0:
            raise ValueError(
                "Trial cannot be negative."
            )

        return f"{claim_id}:{condition}:{trial}"

    def append(
        self,
        record: dict[str, Any],
    ) -> None:
        """Append one completed trial and flush it to disk."""
        key = record.get("trial_key")

        if not isinstance(key, str) or not key:
            raise ValueError(
                "Journal record needs a trial_key."
            )

        if key in self.completed_keys():
            raise ValueError(
                f"Trial already recorded: {key}"
            )

        serialized = json.dumps(
            record,
            separators=(",", ":"),
        )

        with self.path.open(
            "a",
            encoding="utf-8",
            newline="\n",
        ) as output_file:
            output_file.write(serialized)
            output_file.write("\n")
            output_file.flush()

    def records(self) -> list[dict[str, Any]]:
        """Load all complete journal records."""
        if not self.path.exists():
            return []

        loaded: list[dict[str, Any]] = []

        with self.path.open(
            encoding="utf-8",
        ) as input_file:
            for line_number, line in enumerate(
                input_file,
                start=1,
            ):
                stripped = line.strip()

                if not stripped:
                    continue

                try:
                    record = json.loads(stripped)
                except json.JSONDecodeError as error:
                    raise ValueError(
                        "Invalid journal JSON on line "
                        f"{line_number}."
                    ) from error

                if not isinstance(record, dict):
                    raise ValueError(
                        "Every journal line must contain an object."
                    )

                loaded.append(record)

        return loaded

    def completed_keys(self) -> set[str]:
        """Return unique identifiers for completed trials."""
        keys: set[str] = set()

        for record in self.records():
            key = record.get("trial_key")

            if not isinstance(key, str) or not key:
                raise ValueError(
                    "Stored journal record lacks a trial_key."
                )

            if key in keys:
                raise ValueError(
                    f"Duplicate stored trial: {key}"
                )

            keys.add(key)

        return keys

    def is_complete(
        self,
        claim_id: str,
        condition: str,
        trial: int,
    ) -> bool:
        """Check whether one matched trial condition is saved."""
        key = self.trial_key(
            claim_id,
            condition,
            trial,
        )

        return key in self.completed_keys()

    def progress(
        self,
        expected_trials: int,
    ) -> tuple[int, int]:
        """Return completed and expected record counts."""
        if expected_trials < 1:
            raise ValueError(
                "Expected trials must be at least 1."
            )

        completed = len(self.completed_keys())

        if completed > expected_trials:
            raise ValueError(
                "Journal contains more trials than expected."
            )

        return completed, expected_trials
