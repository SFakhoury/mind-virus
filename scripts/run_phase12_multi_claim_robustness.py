from pathlib import Path

from mind_virus.multi_claim_robustness_pilot import (
    MultiClaimRobustnessPlan, collect_multi_claim_robustness,
)


def main() -> None:
    plan = MultiClaimRobustnessPlan()
    plan.validate()
    print("PHASE 12: LIVE MULTI-CLAIM ROBUSTNESS PILOT")
    print("-" * 50)
    print(f"Claims: {len(plan.claims)}")
    print(f"Models: {', '.join(plan.base.models)}")
    print(f"Prompt variants: {', '.join(plan.base.prompt_variants)}")
    print(f"Maximum calls: {plan.planned_calls}")
    print(f"Estimated cost: ${plan.estimated_cost_usd:.4f}")
    print(f"Hard cost ceiling: ${plan.cost_ceiling_usd:.2f}")
    print("Results checkpoint after every call.")
    if input("Type RUN to begin paid collection: ").strip() != "RUN":
        print("Cancelled. No API requests were made.")
        return
    from openai import OpenAI
    output = Path("results/phase12_multi_claim_robustness.json")
    records = collect_multi_claim_robustness(plan, output, client=OpenAI())
    cost = sum(float(item["estimated_cost_usd"]) for item in records)
    print(f"Completed records: {len(records)}/{plan.planned_calls}")
    print(f"Observed estimated cost: ${cost:.4f}")
    print(f"Saved to: {output}")


if __name__ == "__main__":
    main()
