import unittest

from mind_virus.assignment import (
    BASE_PERSONALITY,
    assign_agents,
)


class AssignmentTests(unittest.TestCase):
    def test_baseline_contains_no_skeptics(self) -> None:
        agents, positions = assign_agents(
            condition="baseline",
            count=10,
            skeptic_fraction=0.35,
            seed=2026,
        )

        self.assertEqual(positions, set())
        self.assertTrue(
            all(
                agent.personality == BASE_PERSONALITY
                for agent in agents
            )
        )

    def test_skeptic_fraction_is_applied(self) -> None:
        agents, positions = assign_agents(
            condition="skeptical",
            count=10,
            skeptic_fraction=0.35,
            seed=2026,
        )

        self.assertEqual(len(positions), 3)
        self.assertNotIn(0, positions)

        identified = {
            index
            for index, agent in enumerate(agents)
            if "corroborating evidence" in agent.personality
        }

        self.assertEqual(identified, positions)

    def test_assignment_is_reproducible(self) -> None:
        _, first = assign_agents(
            "skeptical",
            12,
            0.35,
            100,
        )
        _, second = assign_agents(
            "skeptical",
            12,
            0.35,
            100,
        )

        self.assertEqual(first, second)

    def test_non_treatment_personality_is_matched(self) -> None:
        baseline, _ = assign_agents(
            "baseline",
            4,
            0.35,
            2026,
        )
        skeptical, positions = assign_agents(
            "skeptical",
            4,
            0.35,
            2026,
        )

        for position in range(4):
            if position not in positions:
                self.assertEqual(
                    baseline[position].personality,
                    skeptical[position].personality,
                )


if __name__ == "__main__":
    unittest.main()
