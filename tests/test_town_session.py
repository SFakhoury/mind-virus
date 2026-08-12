import unittest

from mind_virus.decision import TransmissionDecision
from mind_virus.town_session import TownSession


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


if __name__ == "__main__":
    unittest.main()
