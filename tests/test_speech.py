import sys
import unittest
from unittest.mock import patch

from gui.speech import SpeechNarrator


class SpeechNarratorTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux speech engine selection")
    @patch("gui.speech.subprocess.Popen")
    @patch("gui.speech.shutil.which")
    def test_speaks_text_with_installed_engine(self, which, popen) -> None:
        which.side_effect = lambda name: (
            "/usr/bin/espeak-ng" if name == "espeak-ng" else None
        )
        narrator = SpeechNarrator()

        narrator.speak("The trail opens before you.")

        popen.assert_called_once_with(
            ["/usr/bin/espeak-ng", "The trail opens before you."]
        )

    @patch("gui.speech.shutil.which", return_value=None)
    def test_reports_missing_speech_engine(self, _which) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "No speech engine"):
            SpeechNarrator().speak("A story.")

    def test_rejects_empty_text(self) -> None:
        with self.assertRaisesRegex(ValueError, "no story text"):
            SpeechNarrator().speak("  ")


if __name__ == "__main__":
    unittest.main()
