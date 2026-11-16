import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from gui.terminal import open_terminal


class OpenTerminalTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux terminal selection")
    @patch("gui.terminal.subprocess.Popen")
    @patch("gui.terminal.shutil.which")
    def test_launches_available_terminal_in_requested_directory(
        self, which, popen
    ) -> None:
        which.side_effect = lambda name: (
            "/usr/bin/konsole" if name == "konsole" else None
        )
        working_directory = Path("/tmp/rpg-game")

        open_terminal(working_directory)

        popen.assert_called_once_with(
            [
                "/usr/bin/konsole",
                "--workdir",
                str(working_directory),
            ],
            cwd=working_directory,
        )

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux terminal selection")
    @patch("gui.terminal.shutil.which", return_value=None)
    def test_reports_when_no_terminal_is_available(self, _which) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "No supported terminal"):
            open_terminal(Path("/tmp/rpg-game"))


if __name__ == "__main__":
    unittest.main()
