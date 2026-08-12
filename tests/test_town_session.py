import unittest
from unittest.mock import Mock

from mind_virus.agent import Agent
from mind_virus.decision import TransmissionDecision
from mind_virus.town_session import TownSession
from mind_virus.town_dialogue import TownDialogue
from mind_virus.town_dialogue import OpenAITownDialogueMaker


class TownSessionTests(unittest.TestCase):
    def test_bob_starts_with_firsthand_bakery_memory(self):
        session = TownSession(self.repeating_decision)
        memories = session.agents[1].memories.all()

        self.assertEqual(len(memories), 1)
        self.assertIn("no free-bread giveaway", memories[0].content)

    def test_step_uses_real_agents_and_stores_listener_memory(self):
        session = TownSession(self.repeating_decision)
        turn = session.step()

        self.assertEqual(turn.speaker, "Alice")
        self.assertEqual(turn.listener, "Bob")
        self.assertEqual(session.generation, 1)
        self.assertEqual(len(session.agents[1].memories), 2)

    def test_non_repeating_decision_stops_propagation(self):
        session = TownSession(self.stopping_decision)
        turn = session.step()

        self.assertFalse(turn.repeats_claim)
        self.assertTrue(session.state()["stopped"])
        with self.assertRaises(RuntimeError):
            session.step()

    def test_chat_stores_generated_exchange_in_memories(self):
        session = TownSession(self.stopping_decision)
        chat = session.chat(self.dialogue)

        self.assertEqual(chat["speaker"], "Bob")
        self.assertEqual(chat["listener"], "Charlie")
        self.assertEqual(session.state()["chat_count"], 1)
        self.assertEqual(len(session.agents[1].memories), 2)
        self.assertEqual(len(session.agents[2].memories), 1)

    def test_chat_limit_is_three(self):
        session = TownSession(self.stopping_decision)
        for _ in range(3):
            session.chat(self.dialogue)
        with self.assertRaises(RuntimeError):
            session.chat(self.dialogue)

    def test_live_dialogue_prompt_forbids_invented_evidence(self):
        parsed = TownDialogue(
            speaker_message="There is no direct evidence.",
            listener_reply="Then I will keep the claim unverified.",
            topic="bakery rumor",
            references_rumor=True,
        )
        response = Mock(output_parsed=parsed, usage=None)
        client = Mock()
        client.responses.parse.return_value = response
        maker = OpenAITownDialogueMaker(client=client)
        speaker = Agent("Alice", "Reporter")
        listener = Agent("Dana", "Planner")

        maker(speaker, listener)

        instructions = client.responses.parse.call_args.kwargs["instructions"]
        self.assertIn("Use ONLY facts explicitly contained", instructions)
        self.assertIn("Never invent", instructions)
        self.assertIn("written statement", instructions)
        self.assertIn("inspection", instructions)

    @staticmethod
    def repeating_decision(listener, speaker, message):
        return TransmissionDecision(
            remembered_message=f"{speaker.name} reported: {message}",
            believes_claim=False,
            repeats_claim=True,
            belief_confidence=0.2,
            reason="The report is memorable but unverified.",
        )

    @staticmethod
    def stopping_decision(listener, speaker, message):
        return TransmissionDecision(
            remembered_message=f"{speaker.name} reported: {message}",
            believes_claim=False,
            repeats_claim=False,
            belief_confidence=0.1,
            reason="Firsthand bakery evidence contradicts the rumor.",
        )

    @staticmethod
    def dialogue(speaker, listener):
        return TownDialogue(
            speaker_message="I have a confirmed town update.",
            listener_reply="I will remember the confirmed update.",
            topic="town update",
            references_rumor=False,
        )


if __name__ == "__main__":
    unittest.main()
