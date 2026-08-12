import unittest

from mind_virus.experiment_spec import NetworkSpec
from mind_virus.social_network import build_social_network


class SocialNetworkTests(unittest.TestCase):
    def test_chain_has_expected_edges(self):
        network = build_social_network(NetworkSpec("chain", 4), seed=7)
        self.assertEqual(network.edges, ((0, 1), (1, 2), (2, 3)))

    def test_ring_closes_the_chain(self):
        network = build_social_network(NetworkSpec("ring", 4), seed=7)
        self.assertEqual(
            network.edges, ((0, 1), (0, 3), (1, 2), (2, 3))
        )

    def test_complete_network_connects_every_pair(self):
        network = build_social_network(NetworkSpec("complete", 5), seed=7)
        self.assertEqual(len(network.edges), 10)
        self.assertEqual(network.neighbors(0), (1, 2, 3, 4))

    def test_small_world_is_reproducible_for_same_seed(self):
        spec = NetworkSpec("small_world", 12, 0.6)
        self.assertEqual(
            build_social_network(spec, seed=2026),
            build_social_network(spec, seed=2026),
        )

    def test_small_world_seed_can_change_edges(self):
        spec = NetworkSpec("small_world", 12, 1.0)
        self.assertNotEqual(
            build_social_network(spec, seed=1).edges,
            build_social_network(spec, seed=2).edges,
        )

    def test_all_supported_structures_are_connected(self):
        for structure in ("chain", "ring", "small_world", "complete"):
            with self.subTest(structure=structure):
                probability = 0.8 if structure == "small_world" else 0.0
                network = build_social_network(
                    NetworkSpec(structure, 10, probability), seed=99
                )
                self.assertTrue(network.is_connected)

    def test_unknown_node_has_no_silent_result(self):
        network = build_social_network(NetworkSpec("chain", 4), seed=7)
        with self.assertRaises(KeyError):
            network.neighbors(99)


if __name__ == "__main__":
    unittest.main()
