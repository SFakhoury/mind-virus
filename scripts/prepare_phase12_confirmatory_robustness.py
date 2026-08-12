from mind_virus.confirmatory_robustness import ConfirmatoryRobustnessProtocol


def main() -> None:
    protocol = ConfirmatoryRobustnessProtocol()
    output = protocol.freeze("docs/phase12-confirmatory-robustness-protocol.json")
    print("PHASE 12: CONFIRMATORY ROBUSTNESS PROTOCOL")
    print("-" * 50)
    print(f"Protocol fingerprint: {protocol.fingerprint}")
    print(f"Claims: {len(protocol.plan.claims)}")
    print(f"Trials per condition/cell: {protocol.plan.base.trials_per_cell}")
    print(f"Planned API calls: {protocol.planned_calls}")
    print(f"Conservative estimated cost: ${protocol.plan.estimated_cost_usd:.4f}")
    print(f"Hard cost ceiling: ${protocol.plan.cost_ceiling_usd:.2f}")
    print(f"Frozen protocol: {output}")
    print("No API requests were made.")


if __name__ == "__main__":
    main()
