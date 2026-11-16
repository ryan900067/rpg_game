import tkinter as tk
from tkinter import ttk


class StartScreen(ttk.Frame):
    """Starter layout to replace with the game's main menu."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        ttk.Label(self, text="RPG Game", font=("TkDefaultFont", 24, "bold")).pack(
            pady=(48, 12)
        )
        ttk.Label(self, text="Tkinter interface template").pack()

        # Add menu controls here and connect them to the app/game when ready.
