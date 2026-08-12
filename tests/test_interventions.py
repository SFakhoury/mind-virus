import unittest

from mind_virus.experiment_spec import InterventionSpec
from mind_virus.interventions import (
    INTERVENTION_INSTRUCTIONS,
    assign_intervention,
    build_experimental_agents,
)


class InterventionAssignmentTests(unittest.TestCase):
    def test_control_treats_no_residents(self):
        assignment = assign_intervention(10, InterventionSpec("none"), 42)
        self.assertEqual(assignment.treated_positions, ())

    def test_source_is_never_treated(self):
        assignment = assign_intervention(
            10, InterventionSpec("skepticism", 1.0), 42
        )
        self.assertNotIn(0, assignment.treated_positions)
        self.assertEqual(len(assignment.treated_positions), 9)

    def test_assignment_is_reproducible(self):
        intervention = InterventionSpec("fact_check", 0.4)
        self.assertEqual(
            assign_intervention(12, intervention, 99),
            assign_intervention(12, intervention, 99),
        )

    def test_different_seeds_can_change_assignment(self):
        intervention = InterventionSpec("skepticism", 0.35)
        self.assertNotEqual(
            assign_intervention(12, intervention, 1).treated_positions,
            assign_intervention(12, intervention, 2).treated_positions,
        )

    def test_small_positive_intensity_still_treats_one_resident(self):
        assignment = assign_intervention(
            4, InterventionSpec("inoculation", 0.01), 7
        )
        self.assertEqual(len(assignment.treated_positions), 1)

    def test_each_active_intervention_changes_only_treated_personalities(self):
        for intervention_type in ("skepticism", "fact_check", "inoculation"):
            with self.subTest(intervention_type=intervention_type):
                agents, assignment = build_experimental_agents(
                    8, InterventionSpec(intervention_type, 0.5), 17
                )
                instruction = INTERVENTION_INSTRUCTIONS[intervention_type]
                for position, agent in enumerate(agents):
                    self.assertEqual(
                        instruction in agent.personality,
                        position in assignment.treated_positions,
                    )

    def test_agent_names_are_stable_across_conditions(self):
        baseline, _ = build_experimental_agents(6, InterventionSpec("none"), 11)
        treated, _ = build_experimental_agents(
            6, InterventionSpec("skepticism", 0.5), 11
        )
        self.assertEqual(
            [agent.name for agent in baseline], [agent.name for agent in treated]
        )

    def test_custom_source_position_is_respected(self):
        assignment = assign_intervention(
            6, InterventionSpec("fact_check", 1.0), 3, source_position=4
        )
        self.assertNotIn(4, assignment.treated_positions)
        self.assertNotIn(4, assignment.eligible_positions)


if __name__ == "__main__":
    unittest.main()
