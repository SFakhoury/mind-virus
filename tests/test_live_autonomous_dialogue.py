import unittest
from unittest.mock import Mock

from mind_virus.agent import Agent
from mind_virus.api_budget import BudgetExceeded, BudgetLedger, BudgetPolicy
from mind_virus.autonomous_town import AutonomousTown
from mind_virus.conversation_planning import plan_grounded_conversation
from mind_virus.live_autonomous_dialogue import (
    OpenAIAutonomousDialogueMaker,
    StructuredAutonomousDialogue,
)
from mind_virus.memory_context import ConversationContext


class FakeUsage:
    input_tokens = 120
    output_tokens = 30


class LiveAutonomousDialogueTests(unittest.TestCase):
    def setUp(self):
        self.speaker = Agent("Dana", "A skeptical town planner")
        self.listener = Agent("Alice", "A careful reporter")
        self.memory = self.speaker.observe(
            "At Town Hall, I review public plans.", 6
        )
        self.plan = plan_grounded_conversation(
            self.speaker,
            self.listener,
            ConversationContext(
                "Alice", "Town Hall", "conversation", "public plans"
            ),
        )
        self.parsed = StructuredAutonomousDialogue(
            speaker_message="I review public plans here at Town Hall.",
            communicative_intent="share role knowledge",
        )
        self.response = Mock(output_parsed=self.parsed, usage=FakeUsage())
        self.client = Mock()
        self.client.responses.parse.return_value = self.response
        self.budget = BudgetLedger()
        self.maker = OpenAIAutonomousDialogueMaker(
            self.budget, client=self.client, model="test-model"
        )

    def test_returns_structured_dialogue(self):
        result = self.maker(self.speaker, self.listener, self.plan)

        self.assertEqual(result.speaker_message, self.parsed.speaker_message)
        self.assertEqual(result.communicative_intent, self.parsed.communicative_intent)
        self.assertEqual(result.delivery_mode, "live-ai")
        self.assertEqual(result.attempts, 1)
        self.assertIs(
            self.client.responses.parse.call_args.kwargs["text_format"],
            StructuredAutonomousDialogue,
        )

    def test_prompt_contains_grounding_and_identity(self):
        self.maker(self.speaker, self.listener, self.plan)

        request = self.client.responses.parse.call_args.kwargs
        self.assertIn(self.memory.id, request["input"])
        self.assertIn(self.memory.content, request["input"])
        self.assertIn("Never invent evidence", request["instructions"])
        self.assertIn("Do not decide what the listener believes", request["instructions"])

    def test_actual_usage_is_charged_to_speaker(self):
        self.maker(self.speaker, self.listener, self.plan)

        usage = self.budget.agent_usage["Dana"]
        self.assertEqual(usage.calls, 1)
        self.assertEqual(usage.input_tokens, 120)
        self.assertEqual(usage.output_tokens, 30)

    def test_failed_request_releases_reservation(self):
        self.client.responses.parse.side_effect = RuntimeError("temporary failure")

        with self.assertRaises(RuntimeError):
            self.maker(self.speaker, self.listener, self.plan)

        self.assertEqual(self.budget.reservations, {})

    def test_budget_denial_prevents_api_request(self):
        budget = BudgetLedger(BudgetPolicy(max_session_tokens=1))
        maker = OpenAIAutonomousDialogueMaker(budget, client=self.client)

        with self.assertRaises(BudgetExceeded):
            maker(self.speaker, self.listener, self.plan)

        self.client.responses.parse.assert_not_called()

    def test_autonomous_town_uses_structured_live_message(self):
        town = AutonomousTown(dialogue_maker=self.maker)

        town.tick(20)

        self.assertEqual(town.conversations[0].dialogue_mode, "live-ai")
        self.assertEqual(town.conversations[0].message, self.parsed.speaker_message)
        self.assertEqual(
            town.conversations[0].communicative_intent,
            self.parsed.communicative_intent,
        )

    def test_rejected_invention_is_logged_then_retried(self):
        invented = StructuredAutonomousDialogue(
            speaker_message="Mayor Jordan approved 12 grants at Town Hall.",
            communicative_intent="report approval",
        )
        self.client.responses.parse.side_effect = [
            Mock(output_parsed=invented, usage=FakeUsage()), self.response
        ]

        result = self.maker(self.speaker, self.listener, self.plan)

        self.assertEqual(result.delivery_mode, "live-ai")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(self.budget.session_usage.calls, 2)
        self.assertEqual(len(self.maker.rejections), 1)
        self.assertIn(
            "message introduces unsupported named entities",
            self.maker.rejection_log()[0]["reasons"],
        )

    def test_repeated_invention_uses_safe_fallback(self):
        invented = StructuredAutonomousDialogue(
            speaker_message="Mayor Jordan approved 12 grants at Town Hall.",
            communicative_intent="report approval",
        )
        self.client.responses.parse.return_value = Mock(
            output_parsed=invented, usage=FakeUsage()
        )

        result = self.maker(self.speaker, self.listener, self.plan)

        self.assertEqual(result.speaker_message, self.plan.proposed_message)
        self.assertEqual(result.delivery_mode, "fallback")
        self.assertEqual(len(self.maker.rejections), 2)

    def test_town_keeps_failed_encounter_available_for_retry(self):
        town = AutonomousTown(dialogue_maker=self.maker)
        self.client.responses.parse.side_effect = RuntimeError("temporary failure")

        with self.assertRaises(RuntimeError):
            town.tick(20)
        self.assertEqual(town.conversations, [])

        self.client.responses.parse.side_effect = None
        self.client.responses.parse.return_value = self.response
        recovered = town.process_new_interactions()

        self.assertEqual(len(recovered), 1)
        self.assertEqual(recovered[0].message, self.parsed.speaker_message)


if __name__ == "__main__":
    unittest.main()
