import tkinter as tk
from tkinter import ttk

from .screens import StartScreen


class RPGApp:
    """Top-level window and screen controller for the RPG interface."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("RPG Game")
        self.root.geometry("800x600")
        self.root.minsize(640, 480)

        self.container = ttk.Frame(root, padding=16)
        self.container.pack(fill="both", expand=True)
        self.show_start_screen()

    def show_start_screen(self) -> None:
        """Display the initial screen."""
        for child in self.container.winfo_children():
            child.destroy()
        StartScreen(self.container).pack(fill="both", expand=True)


def main() -> None:
    root = tk.Tk()
    RPGApp(root)
    root.mainloop()
