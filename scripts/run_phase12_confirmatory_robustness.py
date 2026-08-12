from pathlib import Path

from mind_virus.confirmatory_robustness import (
    ConfirmatoryRobustnessProtocol, collect_confirmatory_robustness,
)


def main() -> None:
    protocol = ConfirmatoryRobustnessProtocol()
    protocol_path = Path("docs/phase12-confirmatory-robustness-protocol.json")
    protocol.validate()
    print("PHASE 12: CONFIRMATORY ROBUSTNESS COLLECTION")
    print("-" * 52)
    print(f"Protocol: {protocol.fingerprint}")
    print(f"Maximum calls: {protocol.planned_calls}")
    print(f"Conservative estimate: ${protocol.plan.estimated_cost_usd:.4f}")
    print(f"Hard cost ceiling: ${protocol.plan.cost_ceiling_usd:.2f}")
    print("This creates a new dataset and does not reuse pilot records.")
    print("Every completed call is checkpointed for safe resume.")
    if input("Type CONFIRM to begin paid collection: ").strip() != "CONFIRM":
        print("Cancelled. No API requests were made.")
        return
    from openai import OpenAI
    output = Path("results/phase12_confirmatory_robustness.json")
    records = collect_confirmatory_robustness(
        protocol, protocol_path, output, client=OpenAI()
    )
    cost = sum(float(item["estimated_cost_usd"]) for item in records)
    print(f"Completed records: {len(records)}/{protocol.planned_calls}")
    print(f"Observed estimated cost: ${cost:.4f}")
    print(f"Saved to: {output}")


if __name__ == "__main__":
    main()
