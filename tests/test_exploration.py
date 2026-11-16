import unittest
from unittest.mock import patch

import main


class RunExplorationTests(unittest.TestCase):
    @patch(
        "main.methods.roll_exploration_event",
        return_value={
            "kind": "spring",
            "scene": "a hidden spring",
            "prompt": "Drink from the spring? (y/n): ",
        },
    )
    @patch("main.random.randint", return_value=20)
    def test_uses_confirmation_callback_and_applies_accepted_event(
        self, _randint, _event
    ) -> None:
        player = main.VideoGame(health=50, name="Test Adventurer")
        prompts = []

        result = main.run_exploration(
            player,
            "forest clearing",
            confirm_fn=lambda prompt: prompts.append(prompt) or True,
            use_groq=False,
        )

        self.assertIs(result, player)
        self.assertEqual(player.health, 70)
        self.assertEqual(len(prompts), 1)

    @patch(
        "main.methods.roll_exploration_event",
        return_value={
            "kind": "spring",
            "scene": "a hidden spring",
            "prompt": "Drink from the spring? (y/n): ",
        },
    )
    def test_declined_event_does_not_change_player(self, _event) -> None:
        player = main.VideoGame(health=50, name="Test Adventurer")

        main.run_exploration(
            player,
            "forest clearing",
            confirm_fn=lambda _prompt: False,
            use_groq=False,
        )

        self.assertEqual(player.health, 50)


if __name__ == "__main__":
    unittest.main()
