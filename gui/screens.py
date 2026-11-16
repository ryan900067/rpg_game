import tkinter as tk
from tkinter import ttk


class StartScreen(ttk.Frame):
    """Basic adventure screen layout; controls await game integration."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text="RPG Game", font=("TkDefaultFont", 20, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 16)
        )

        player = ttk.LabelFrame(self, text="Character", padding=12)
        player.grid(row=1, column=0, sticky="ns", padx=(0, 12))
        for row, (label, value) in enumerate(
            (
                ("Name", "Adventurer"),
                ("Level", "1"),
                ("Health", "100 / 100"),
                ("Coins", "0"),
            )
        ):
            ttk.Label(player, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Label(player, text=value).grid(
                row=row, column=1, sticky="e", padx=(12, 0), pady=4
            )

        adventure = ttk.LabelFrame(self, text="Adventure", padding=12)
        adventure.grid(row=1, column=1, sticky="nsew")
        adventure.columnconfigure(0, weight=1)
        adventure.rowconfigure(1, weight=1)
        ttk.Label(
            adventure,
            text="The journey begins...",
            font=("TkDefaultFont", 14),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(
            adventure,
            text="Your story and encounters will appear here.",
            anchor="nw",
            justify="left",
            wraplength=480,
        ).grid(row=1, column=0, sticky="nsew")

        actions = ttk.Frame(self)
        actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        for column, action in enumerate(("Explore", "Inventory", "Save")):
            ttk.Button(actions, text=action, state="disabled").grid(
                row=0, column=column, sticky="ew", padx=(0, 8)
            )
            actions.columnconfigure(column, weight=1)
