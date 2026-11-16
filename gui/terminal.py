import shutil
import subprocess
import sys
from pathlib import Path


def open_terminal(working_directory: Path) -> None:
    """Open an interactive system terminal in the requested directory."""
    if sys.platform == "win32":
        subprocess.Popen(
            ["cmd.exe"],
            cwd=working_directory,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return

    if sys.platform == "darwin":
        subprocess.Popen(["open", "-a", "Terminal"], cwd=working_directory)
        return

    terminal_options = (
        ("gnome-terminal", ("--working-directory", str(working_directory))),
        ("konsole", ("--workdir", str(working_directory))),
        ("xfce4-terminal", ("--working-directory", str(working_directory))),
        ("x-terminal-emulator", ()),
        ("xterm", ()),
    )
    for terminal, options in terminal_options:
        executable = shutil.which(terminal)
        if executable:
            subprocess.Popen([executable, *options], cwd=working_directory)
            return

    raise FileNotFoundError(
        "No supported terminal emulator was found. Install a terminal emulator "
        "such as GNOME Terminal, Konsole, or xterm."
    )
