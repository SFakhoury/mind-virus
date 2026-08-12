from pathlib import Path

from mind_virus.live_robustness_pilot import LiveRobustnessPlan, collect_live_robustness_pilot


def main() -> None:
    plan = LiveRobustnessPlan()
    plan.validate()
    print("PHASE 12: LIVE ROBUSTNESS PILOT")
    print("-" * 42)
    print(f"Models: {', '.join(plan.models)}")
    print(f"Prompt variants: {', '.join(plan.prompt_variants)}")
    print(f"Planned maximum calls: {plan.planned_calls}")
    print(f"Estimated cost: ${plan.estimated_cost_usd:.4f}")
    print(f"Hard cost ceiling: ${plan.cost_ceiling_usd:.2f}")
    print("Results checkpoint after every call.")
    if input("Type RUN to begin paid collection: ").strip() != "RUN":
        print("Cancelled. No API requests were made.")
        return
    from openai import OpenAI
    output = Path("results/phase12_live_robustness_pilot.json")
    records = collect_live_robustness_pilot(plan, output, client=OpenAI())
    total_cost = sum(float(item["estimated_cost_usd"]) for item in records)
    print(f"Completed records: {len(records)}/{plan.planned_calls}")
    print(f"Observed estimated cost: ${total_cost:.4f}")
    print(f"Saved to: {output}")


if __name__ == "__main__":
    main()
