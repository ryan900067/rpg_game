from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import main as game_engine

from .screens import AdventureScreenState, StartScreen
from .speech import SpeechNarrator
from .terminal import open_terminal


class RPGApp:
    """Top-level window and screen controller for the RPG interface."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Ashen Trail - RPG Game")
        self.root.geometry("1100x780")
        self.root.minsize(900, 680)

        self.player = game_engine.VideoGame(name="Adventurer")
        self.narrator = SpeechNarrator()
        self.route = game_engine.create_adventure_stages(1)
        self.route_index = 0
        self.location = self.route[0][1]
        self.biome = game_engine.methods.create_map(self.location).biome
        self.story = (
            "The forest trail opens at the river crossing. Explore to discover "
            "what waits along the route."
        )

        self.container = ttk.Frame(root, padding=16, style="Game.TFrame")
        self.container.pack(fill="both", expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.show_start_screen()

    def show_start_screen(self) -> None:
        """Display the initial screen."""
        for child in self.container.winfo_children():
            child.destroy()
        current_stage = min(max(self.route_index - 1, 0), len(self.route) - 1)
        next_encounter = (
            self.route[current_stage][0]
            if self.route
            else "No encounters configured"
        )
        state = AdventureScreenState(
            player=self.player,
            location=self.location,
            biome=self.biome,
            locations_explored=self.route_index,
            route_length=len(self.route),
            next_encounter=next_encounter,
            story=self.story,
        )
        StartScreen(
            self.container,
            state,
            self.explore,
            self.open_terminal,
            self.narrate,
        ).pack(fill="both", expand=True)

    def explore(self) -> None:
        """Explore the next route area using the existing exploration logic."""
        if self.route_index >= len(self.route) or self.player.health <= 0:
            return

        _monster_name, destination = self.route[self.route_index]
        self.route_index += 1
        self.location = destination
        self.biome = game_engine.methods.create_map(destination).biome
        output = StringIO()

        def confirm_discovery(prompt: str) -> bool:
            narrative = output.getvalue().strip()
            question = prompt.removesuffix("(y/n):").strip()
            message = "\n\n".join(part for part in (narrative, question) if part)
            return messagebox.askyesno("Discovery", message, parent=self.root)

        with redirect_stdout(output):
            self.player = game_engine.run_exploration(
                self.player,
                destination,
                confirm_fn=confirm_discovery,
                use_groq=False,
            )
        self.story = output.getvalue().strip()
        self.show_start_screen()

    def open_terminal(self) -> None:
        """Open an interactive terminal in the project directory."""
        try:
            open_terminal(Path.cwd())
        except OSError as error:
            messagebox.showerror(
                "Could not open terminal",
                str(error),
                parent=self.root,
            )

    def narrate(self) -> None:
        """Read the current field report aloud when requested."""
        try:
            self.narrator.speak(self.story)
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Narration unavailable",
                str(error),
                parent=self.root,
            )

    def close(self) -> None:
        self.narrator.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    RPGApp(root)
    root.mainloop()
