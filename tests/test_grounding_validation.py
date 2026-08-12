import unittest

from mind_virus.agent import Agent
from mind_virus.conversation_planning import plan_grounded_conversation
from mind_virus.grounding_validation import validate_grounded_dialogue
from mind_virus.memory_context import ConversationContext


class GroundingValidationTests(unittest.TestCase):
    def setUp(self):
        speaker = Agent("Dana", "Planner")
        listener = Agent("Alice", "Reporter")
        speaker.observe("At Town Hall, I review public plans.", 6)
        self.plan = plan_grounded_conversation(
            speaker,
            listener,
            ConversationContext("Alice", "Town Hall", "conversation", "public plans"),
        )

    def test_accepts_message_supported_by_grounding(self):
        result = validate_grounded_dialogue(
            "I review public plans at Town Hall.", self.plan
        )

        self.assertTrue(result.accepted)

    def test_rejects_invented_named_entity(self):
        result = validate_grounded_dialogue(
            "Mayor Jordan approved public plans at Town Hall.", self.plan
        )

        self.assertFalse(result.accepted)
        self.assertIn("message introduces unsupported named entities", result.reasons)

    def test_rejects_invented_number(self):
        result = validate_grounded_dialogue(
            "I review 12 public plans at Town Hall.", self.plan
        )

        self.assertFalse(result.accepted)
        self.assertIn("message introduces unsupported numbers", result.reasons)

    def test_no_memory_requires_uncertain_message(self):
        empty_speaker = Agent("Dana", "Planner")
        listener = Agent("Alice", "Reporter")
        plan = plan_grounded_conversation(
            empty_speaker,
            listener,
            ConversationContext("Alice", "Town Hall", "conversation", "festival"),
        )

        result = validate_grounded_dialogue("The festival starts today.", plan)

        self.assertFalse(result.accepted)
        self.assertIn("factual statement has no retrieved memory support", result.reasons)


if __name__ == "__main__":
    unittest.main()
