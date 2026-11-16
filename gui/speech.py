import shutil
import subprocess
import sys


class SpeechNarrator:
    """Speak story text with the platform's installed speech engine."""

    def __init__(self) -> None:
        self._process: subprocess.Popen | None = None

    def speak(self, text: str) -> None:
        text = text.strip()
        if not text:
            raise ValueError("There is no story text to read.")

        executable, command, use_stdin = self._command()
        self.stop()
        if use_stdin:
            process = subprocess.Popen(
                [executable, *command],
                stdin=subprocess.PIPE,
                text=True,
            )
            try:
                if process.stdin is not None:
                    process.stdin.write(text)
                    process.stdin.close()
            except OSError:
                process.terminate()
                raise
        else:
            process = subprocess.Popen([executable, *command, text])
        self._process = process

    @staticmethod
    def _command() -> tuple[str, list[str], bool]:
        if sys.platform == "darwin":
            executable = shutil.which("say")
            if executable:
                return executable, [], False
        elif sys.platform == "win32":
            executable = shutil.which("powershell.exe") or shutil.which("powershell")
            if executable:
                script = (
                    "Add-Type -AssemblyName System.Speech; "
                    "$text = [Console]::In.ReadToEnd(); "
                    "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    "$speaker.Speak($text)"
                )
                return executable, ["-NoProfile", "-NonInteractive", "-Command", script], True
        else:
            for name in ("espeak-ng", "espeak", "spd-say"):
                executable = shutil.which(name)
                if executable:
                    return executable, [], False

        raise FileNotFoundError(
            "No speech engine is installed. Install espeak-ng, espeak, or "
            "speech-dispatcher on Linux, or enable the system speech engine."
        )

    def stop(self) -> None:
        process, self._process = self._process, None
        if process is None or process.poll() is not None:
            return
        try:
            process.terminate()
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
