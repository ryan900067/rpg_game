from dataclasses import dataclass
from collections.abc import Callable
import tkinter as tk
from tkinter import ttk
from typing import Protocol


BACKGROUND = "#0d1520"
CARD = "#172434"
TEXT = "#edf2f7"
MUTED = "#b0bdc9"
GOLD = "#f4cb70"


class PlayerView(Protocol):
    name: str
    health: int
    strength: int
    level: int
    coins: int
    inventory: list[str]


@dataclass(frozen=True)
class AdventureScreenState:
    player: PlayerView
    location: str
    biome: str
    locations_explored: int
    route_length: int
    next_encounter: str
    story: str


def configure_styles() -> None:
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Game.TFrame", background=BACKGROUND)
    style.configure("Card.TFrame", background=CARD)
    style.configure("Game.TLabel", background=BACKGROUND, foreground=TEXT)
    style.configure("Card.TLabel", background=CARD, foreground=TEXT)
    style.configure(
        "HeaderMuted.TLabel",
        background=BACKGROUND,
        foreground=MUTED,
        font=("TkDefaultFont", 10),
    )
    style.configure(
        "HeaderGold.TLabel",
        background=BACKGROUND,
        foreground=GOLD,
        font=("TkDefaultFont", 10, "bold"),
    )
    style.configure(
        "Muted.TLabel",
        background=CARD,
        foreground=MUTED,
        font=("TkDefaultFont", 10),
    )
    style.configure(
        "Gold.TLabel",
        background=CARD,
        foreground=GOLD,
        font=("TkDefaultFont", 11, "bold"),
    )
    style.configure(
        "Title.TLabel",
        background=CARD,
        foreground=TEXT,
        font=("TkDefaultFont", 17, "bold"),
    )
    style.configure(
        "Card.TLabelframe",
        background=CARD,
        bordercolor="#334353",
        relief="solid",
    )
    style.configure("Card.TSeparator", background="#344556")
    style.configure(
        "Card.TLabelframe.Label",
        background=CARD,
        foreground=GOLD,
        font=("TkDefaultFont", 10, "bold"),
    )
    style.configure(
        "Action.TButton",
        background="#506e8a",
        foreground="white",
        padding=(10, 8),
        font=("TkDefaultFont", 9, "bold"),
    )
    style.map(
        "Action.TButton",
        background=[("disabled", "#354655"), ("active", "#6487a7")],
        foreground=[("disabled", "#c5d0da")],
    )
    style.configure(
        "Explore.TButton",
        background="#9b773f",
        foreground="white",
        padding=(10, 8),
        font=("TkDefaultFont", 9, "bold"),
    )
    style.map(
        "Explore.TButton",
        background=[("disabled", "#715b38"), ("active", "#bd9654")],
        foreground=[("disabled", "#eee0bd")],
    )
    style.configure(
        "Terminal.TButton",
        background="#347f92",
        foreground="white",
        padding=(10, 8),
        font=("TkDefaultFont", 9, "bold"),
    )
    style.map(
        "Terminal.TButton",
        background=[("active", "#4b9db2")],
    )
    style.configure(
        "Game.Horizontal.TProgressbar",
        background="#d95157",
        troughcolor="#303b48",
        bordercolor="#303b48",
        lightcolor="#d95157",
        darkcolor="#d95157",
    )
    style.configure(
        "XP.Horizontal.TProgressbar",
        background="#65b9a2",
        troughcolor="#303b48",
        bordercolor="#303b48",
        lightcolor="#65b9a2",
        darkcolor="#65b9a2",
    )


class AdventureMap(tk.Canvas):
    """Static, resizable world map preview for the adventure screen."""

    biome_tiles = {
        "Verdant Forest": (
            "GGGGGRRRFFGG",
            "GGPPGGGFFFGG",
            "GWPPPGGGGGGG",
            "WWWPPPGGGFGG",
            "GGWWPPPGGGGG",
            "GGGGGPPPGGGG",
            "GGFFGGGGGGGG",
            "GGFFGGGGGGGG",
        ),
        "Open Road": (
            "GGGGGGGGGGGG",
            "GGGPPPGGGGGG",
            "GGRPPPGGGGGG",
            "GGRPPPGGGFGG",
            "GGGPPPGGGFGG",
            "GGGGPPPGGGGG",
            "GGGGGGGGGGGG",
            "GGFFGGGGGGGG",
        ),
        "Coastal Reach": (
            "WWWWWWWWWWWW",
            "WSSSSSSSSSSW",
            "WSSPPPPSSSSW",
            "WSSPPPPSSSSW",
            "WSSSSPPPSSSW",
            "WSSSSSSPPSSW",
            "WSSSSSSSSSSW",
            "WWWWWWWWWWWW",
        ),
    }
    player_routes = {
        "Verdant Forest": (
            (2, 1), (3, 1), (3, 2), (4, 2),
            (4, 3), (5, 3), (5, 4), (6, 4),
        ),
        "Open Road": (
            (3, 1), (4, 1), (5, 1), (5, 2),
            (5, 3), (5, 4), (4, 5), (5, 5),
        ),
        "Coastal Reach": (
            (3, 2), (4, 2), (5, 2), (6, 2),
            (6, 3), (6, 4), (7, 4), (8, 5),
        ),
    }

    def __init__(
        self, parent: tk.Widget, biome: str, locations_explored: int
    ) -> None:
        super().__init__(
            parent,
            height=390,
            background=CARD,
            highlightthickness=0,
        )
        self.tiles = self.biome_tiles.get(biome, self.biome_tiles["Verdant Forest"])
        self.player_route = self.player_routes.get(
            biome, self.player_routes["Verdant Forest"]
        )
        self.player_route_index = min(locations_explored, len(self.player_route) - 1)
        self.bind("<Configure>", self._draw_map)

    def _draw_map(self, _event: tk.Event) -> None:
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        columns, rows = len(self.tiles[0]), len(self.tiles)
        map_height = height - 34
        tile_size = min((width - 20) / columns, (map_height - 10) / rows)
        if tile_size <= 0:
            return

        map_width = columns * tile_size
        map_height = rows * tile_size
        left = (width - map_width) / 2
        top = (height - 34 - map_height) / 2
        for row, line in enumerate(self.tiles):
            for column, tile in enumerate(line):
                x1 = left + column * tile_size
                y1 = top + row * tile_size
                x2, y2 = x1 + tile_size, y1 + tile_size
                colors = {
                    "W": "#347f92",
                    "P": "#b78d58",
                    "F": "#285541",
                    "R": "#74736d",
                    "S": "#c4a46a",
                    "G": "#5d8951" if (row + column) % 2 else "#527d4c",
                }
                self.create_rectangle(
                    x1, y1, x2, y2, fill=colors[tile], outline="#263c36", width=1
                )
                if tile == "W":
                    self._draw_water(x1, y1, tile_size)
                elif tile == "F":
                    self._draw_tree(x1, y1, tile_size)
                elif tile == "R":
                    self._draw_mountain(x1, y1, tile_size)

        self._draw_bridge(left, top, tile_size)
        player_column, player_row = self.player_route[self.player_route_index]
        self._draw_marker(
            left, top, tile_size, player_column, player_row, "player"
        )
        self._draw_marker(left, top, tile_size, 9, 4, "scout")
        self._draw_marker(left, top, tile_size, 7, 2, "guide")
        self._draw_marker(left, top, tile_size, 10, 6, "chest")
        self._draw_legend(width, height)

    def _draw_water(self, x: float, y: float, size: float) -> None:
        for offset in (0.32, 0.72):
            self.create_line(
                x + size * 0.15,
                y + size * offset,
                x + size * 0.85,
                y + size * offset,
                fill="#74bbcb",
                width=2,
            )

    def _draw_tree(self, x: float, y: float, size: float) -> None:
        self.create_rectangle(
            x + size * 0.43,
            y + size * 0.56,
            x + size * 0.58,
            y + size * 0.9,
            fill="#765238",
            outline="",
        )
        self.create_polygon(
            x + size * 0.5,
            y + size * 0.05,
            x + size * 0.1,
            y + size * 0.72,
            x + size * 0.9,
            y + size * 0.72,
            fill="#1f4738",
            outline="#82a267",
        )
        self.create_polygon(
            x + size * 0.5,
            y + size * 0.24,
            x + size * 0.18,
            y + size * 0.82,
            x + size * 0.82,
            y + size * 0.82,
            fill="#326348",
            outline="",
        )

    def _draw_mountain(self, x: float, y: float, size: float) -> None:
        self.create_polygon(
            x + size * 0.08,
            y + size * 0.9,
            x + size * 0.4,
            y + size * 0.16,
            x + size * 0.62,
            y + size * 0.64,
            x + size * 0.82,
            y + size * 0.1,
            x + size * 0.96,
            y + size * 0.9,
            fill="#a4a69e",
            outline="#dad7c4",
        )

    def _draw_bridge(self, left: float, top: float, tile_size: float) -> None:
        x1 = left + 2 * tile_size
        x2 = left + 5 * tile_size
        y = top + 3.5 * tile_size
        for offset in (-0.22, 0, 0.22):
            self.create_line(
                x1,
                y + offset * tile_size,
                x2,
                y + offset * tile_size,
                fill="#684d37",
                width=max(2, int(tile_size * 0.07)),
            )

    def _draw_marker(
        self,
        left: float,
        top: float,
        tile_size: float,
        column: int,
        row: int,
        kind: str,
    ) -> None:
        center_x = left + (column + 0.5) * tile_size
        center_y = top + (row + 0.5) * tile_size
        radius = tile_size * 0.3
        if kind == "player":
            self.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill="#edcf72",
                outline="#fff0bb",
                width=2,
            )
            self.create_oval(
                center_x - radius * 0.35,
                center_y - radius * 0.65,
                center_x + radius * 0.35,
                center_y,
                fill="#f1d0a1",
                outline="",
            )
            self.create_polygon(
                center_x - radius * 0.55,
                center_y + radius * 0.75,
                center_x - radius * 0.4,
                center_y,
                center_x + radius * 0.4,
                center_y,
                center_x + radius * 0.55,
                center_y + radius * 0.75,
                fill="#3979d4",
                outline="",
            )
        elif kind == "scout":
            self.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill="#6da353",
                outline="#d0e08b",
                width=2,
            )
            self.create_polygon(
                center_x - radius * 0.7,
                center_y - radius * 0.5,
                center_x - radius * 1.15,
                center_y - radius * 1.2,
                center_x - radius * 0.2,
                center_y - radius * 0.8,
                fill="#9aba62",
            )
            self.create_polygon(
                center_x + radius * 0.7,
                center_y - radius * 0.5,
                center_x + radius * 1.15,
                center_y - radius * 1.2,
                center_x + radius * 0.2,
                center_y - radius * 0.8,
                fill="#9aba62",
            )
            for offset in (-0.35, 0.35):
                self.create_oval(
                    center_x + offset * radius - 1,
                    center_y - 1,
                    center_x + offset * radius + 1,
                    center_y + 2,
                    fill="#17211d",
                )
        elif kind == "guide":
            self.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill="#b87fd1",
                outline="#ead4f4",
                width=2,
            )
            self.create_oval(
                center_x - radius * 0.35,
                center_y - radius * 0.65,
                center_x + radius * 0.35,
                center_y,
                fill="#f3d5ad",
                outline="",
            )
            self.create_polygon(
                center_x - radius * 0.5,
                center_y + radius * 0.8,
                center_x - radius * 0.35,
                center_y,
                center_x + radius * 0.35,
                center_y,
                center_x + radius * 0.5,
                center_y + radius * 0.8,
                fill="#8558a5",
                outline="",
            )
        else:
            self.create_rectangle(
                center_x - radius,
                center_y - radius * 0.65,
                center_x + radius,
                center_y + radius * 0.65,
                fill="#d59a3e",
                outline="#f6d16e",
                width=2,
            )
            self.create_line(
                center_x - radius,
                center_y,
                center_x + radius,
                center_y,
                fill="#76502e",
                width=2,
            )
            self.create_rectangle(
                center_x - 2,
                center_y - 2,
                center_x + 2,
                center_y + 3,
                fill="#fff0a8",
                outline="",
            )

    def _draw_legend(self, width: int, height: int) -> None:
        items = (
            ("You", "#3979d4"),
            ("Scout", "#6da353"),
            ("Guide", "#b87fd1"),
            ("Chest", "#d59a3e"),
        )
        item_width = 72
        start_x = max(8, (width - item_width * len(items)) / 2)
        y = height - 15
        for index, (label, color) in enumerate(items):
            x = start_x + index * item_width
            self.create_oval(x, y - 5, x + 10, y + 5, fill=color, outline="")
            self.create_text(
                x + 14,
                y,
                text=label,
                fill="#d1dce5",
                anchor="w",
                font=("TkDefaultFont", 9),
            )


class MicrophoneButton(tk.Canvas):
    """Small keyboard-accessible microphone control for the field report."""

    def __init__(self, parent: tk.Widget, command: Callable[[], None]) -> None:
        super().__init__(
            parent,
            width=32,
            height=32,
            background=BACKGROUND,
            highlightthickness=0,
            cursor="hand2",
            takefocus=True,
        )
        self.command = command
        self.hovered = False
        self.bind("<Button-1>", self._activate)
        self.bind("<Return>", self._activate)
        self.bind("<space>", self._activate)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<FocusIn>", self._draw)
        self.bind("<FocusOut>", self._draw)
        self._draw()

    def _activate(self, _event: tk.Event) -> str:
        self.command()
        return "break"

    def _on_enter(self, _event: tk.Event) -> None:
        self.hovered = True
        self._draw()

    def _on_leave(self, _event: tk.Event) -> None:
        self.hovered = False
        self._draw()

    def _draw(self, _event: tk.Event | None = None) -> None:
        self.delete("all")
        fill = "#26384a" if self.hovered else BACKGROUND
        outline = GOLD if self.focus_get() == self else "#526274"
        self.create_rectangle(1, 1, 31, 31, fill=fill, outline=outline)
        self.create_oval(12, 6, 20, 19, outline=GOLD, width=2)
        self.create_arc(
            9, 10, 23, 24, start=180, extent=180, style="arc", outline=GOLD, width=2
        )
        self.create_line(16, 24, 16, 27, fill=GOLD, width=2)
        self.create_line(12, 27, 20, 27, fill=GOLD, width=2)


class StartScreen(ttk.Frame):
    """Game-themed screen with live character and exploration details."""

    def __init__(
        self,
        parent: tk.Widget,
        state: AdventureScreenState,
        on_explore: Callable[[], None],
        on_open_terminal: Callable[[], None],
        on_narrate: Callable[[], None],
    ) -> None:
        configure_styles()
        super().__init__(parent, style="Game.TFrame")
        self.state = state
        self.on_explore = on_explore
        self.on_open_terminal = on_open_terminal
        self.on_narrate = on_narrate
        self.columnconfigure(0, minsize=190)
        self.columnconfigure(1, weight=1, minsize=390)
        self.columnconfigure(2, minsize=190)
        self.rowconfigure(1, weight=1)

        self._build_header()
        self._build_character_panel()
        self._build_map_panel()
        self._build_adventure_panel()
        self._build_story_and_actions()

    def _build_header(self) -> None:
        header = ttk.Frame(self, style="Game.TFrame")
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="ASHEN TRAIL", style="Game.TLabel", font=(
            "TkDefaultFont", 21, "bold"
        )).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text=f"CAMPAIGN 01  |  {self.state.biome.upper()}",
            style="HeaderMuted.TLabel",
        ).grid(row=0, column=1, sticky="e", padx=(8, 16))
        ttk.Label(
            header,
            text=f"COINS  {self.state.player.coins}",
            style="HeaderGold.TLabel",
        ).grid(row=0, column=2, sticky="e")
        MicrophoneButton(header, self.on_narrate).grid(
            row=0, column=3, sticky="e", padx=(12, 0)
        )

    def _build_character_panel(self) -> None:
        player = ttk.LabelFrame(
            self, text="YOUR ADVENTURER", padding=12, style="Card.TLabelframe"
        )
        player.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        player.columnconfigure(0, weight=1)

        portrait = tk.Canvas(
            player,
            height=112,
            background="#26384a",
            highlightthickness=1,
            highlightbackground="#586d80",
        )
        portrait.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self._draw_portrait(portrait)
        ttk.Label(
            player, text=self.state.player.name.upper(), style="Title.TLabel"
        ).grid(row=1, column=0, sticky="w")
        ttk.Label(
            player,
            text=f"Wanderer  |  Level {self.state.player.level}",
            style="Muted.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(2, 10))

        self._add_stat(
            player,
            3,
            "HEALTH",
            f"{self.state.player.health} / 100",
            "Game.Horizontal.TProgressbar",
            max(0, self.state.player.health) / 100,
        )
        self._add_stat(
            player,
            5,
            "STRENGTH",
            f"{self.state.player.strength} / 20",
            "XP.Horizontal.TProgressbar",
            self.state.player.strength / 20,
        )
        ttk.Label(player, text="EQUIPPED", style="Gold.TLabel").grid(
            row=7, column=0, sticky="w", pady=(10, 4)
        )
        ttk.Label(
            player,
            text=", ".join(self.state.player.inventory) or "No items yet",
            style="Card.TLabel",
            wraplength=160,
        ).grid(row=8, column=0, sticky="w")

    def _draw_portrait(self, canvas: tk.Canvas) -> None:
        canvas.bind(
            "<Configure>",
            lambda _event: self._paint_portrait(canvas),
        )
        self._paint_portrait(canvas)

    @staticmethod
    def _paint_portrait(canvas: tk.Canvas) -> None:
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        center_x = width / 2
        canvas.create_oval(
            center_x - 31, 12, center_x + 31, 74, fill="#dfbf8c", outline="#f3d37a", width=2
        )
        canvas.create_polygon(
            center_x - 31, 40, center_x - 21, 12, center_x + 22, 12,
            center_x + 31, 40, center_x + 21, 31, center_x - 20, 31,
            fill="#586b8c",
        )
        for offset in (-10, 10):
            canvas.create_oval(
                center_x + offset - 2, 37, center_x + offset + 2, 41, fill="#17202a"
            )
        canvas.create_arc(
            center_x - 10, 43, center_x + 10, 57, start=200, extent=140,
            style="arc", outline="#6e3b32", width=2,
        )
        canvas.create_polygon(
            center_x - 45, height - 5, center_x - 36, 68,
            center_x - 15, 58, center_x + 15, 58,
            center_x + 37, 68, center_x + 45, height - 5,
            fill="#3c6570", outline="#8bb2a8",
        )
        canvas.create_line(
            center_x - 34, 78, center_x + 34, 78, fill="#d7bd73", width=3
        )

    @staticmethod
    def _add_stat(
        parent: ttk.LabelFrame,
        row: int,
        title: str,
        value: str,
        style: str,
        progress: float,
    ) -> None:
        line = ttk.Frame(parent, style="Card.TFrame")
        line.grid(row=row, column=0, sticky="ew", pady=(0, 3))
        line.columnconfigure(0, weight=1)
        ttk.Label(line, text=title, style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(line, text=value, style="Muted.TLabel").grid(row=0, column=1, sticky="e")
        ttk.Progressbar(
            parent,
            maximum=1,
            value=progress,
            style=style,
        ).grid(row=row + 1, column=0, sticky="ew", pady=(0, 8))

    def _build_map_panel(self) -> None:
        world = ttk.LabelFrame(
            self, text="WORLD MAP", padding=10, style="Card.TLabelframe"
        )
        world.grid(row=1, column=1, sticky="nsew", padx=6)
        world.columnconfigure(0, weight=1)
        world.rowconfigure(1, weight=1)

        heading = ttk.Frame(world, style="Card.TFrame")
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        heading.columnconfigure(0, weight=1)
        ttk.Label(
            heading, text=self.state.location.title(), style="Title.TLabel"
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            heading,
            text=(
                f"{self.state.biome}  /  "
                f"Area {max(1, self.state.locations_explored)}"
                f" of {self.state.route_length}"
            ),
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        AdventureMap(
            world,
            self.state.biome,
            self.state.locations_explored,
        ).grid(
            row=1, column=0, sticky="nsew"
        )

    def _build_adventure_panel(self) -> None:
        log = ttk.LabelFrame(
            self, text="ADVENTURE LOG", padding=12, style="Card.TLabelframe"
        )
        log.grid(row=1, column=2, sticky="nsew", padx=(6, 0))
        log.columnconfigure(0, weight=1)

        ttk.Label(log, text="NEXT ENCOUNTER", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(log, text=self.state.next_encounter, style="Title.TLabel").grid(
            row=1, column=0, sticky="w", pady=(5, 2)
        )
        ttk.Label(
            log,
            text="The route's next challenge.",
            style="Card.TLabel",
            wraplength=160,
        ).grid(row=2, column=0, sticky="w")
        ttk.Progressbar(
            log,
            maximum=1,
            value=self.state.locations_explored / self.state.route_length,
            style="XP.Horizontal.TProgressbar",
        ).grid(row=3, column=0, sticky="ew", pady=(8, 14))

        ttk.Separator(log, style="Card.TSeparator").grid(
            row=4, column=0, sticky="ew", pady=4
        )
        ttk.Label(log, text="ROUTE LOCATIONS", style="Muted.TLabel").grid(
            row=5, column=0, sticky="w", pady=(8, 2)
        )
        ttk.Label(
            log,
            text=f"{self.state.locations_explored} / {self.state.route_length} explored",
            style="Card.TLabel",
        ).grid(
            row=6, column=0, sticky="w"
        )
        ttk.Separator(log, style="Card.TSeparator").grid(
            row=7, column=0, sticky="ew", pady=10
        )
        ttk.Label(log, text="CURRENT BIOME", style="Muted.TLabel").grid(
            row=8, column=0, sticky="w"
        )
        ttk.Label(
            log, text=self.state.biome, style="Gold.TLabel", wraplength=160
        ).grid(row=9, column=0, sticky="w", pady=(5, 2))
        ttk.Separator(log, style="Card.TSeparator").grid(
            row=10, column=0, sticky="ew", pady=10
        )
        ttk.Label(
            log,
            text=f"Health: {self.state.player.health}  |  Coins: {self.state.player.coins}",
            style="Muted.TLabel",
            wraplength=160,
        ).grid(row=11, column=0, sticky="w")

    def _build_story_and_actions(self) -> None:
        footer = ttk.Frame(self, style="Card.TFrame", padding=12)
        footer.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        footer.columnconfigure(0, weight=1)

        ttk.Label(footer, text="FIELD REPORT", style="Gold.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            footer,
            text=self.state.story,
            style="Card.TLabel",
            wraplength=520,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(5, 8))
        ttk.Label(
            footer, text="What will you do?", style="Muted.TLabel"
        ).grid(row=2, column=0, sticky="w")

        actions = ttk.Frame(footer, style="Card.TFrame")
        actions.grid(row=1, column=1, rowspan=2, sticky="e", padx=(16, 0))
        for column, (action, style, opens_terminal) in enumerate(
            (
                ("Explore", "Explore.TButton", False),
                ("Inventory", "Action.TButton", False),
                ("Save", "Action.TButton", False),
                ("Open Terminal", "Terminal.TButton", True),
            )
        ):
            if action == "Explore":
                button = ttk.Button(
                    actions,
                    text=action,
                    style=style,
                    command=self.on_explore,
                    state=(
                        "normal"
                        if self.state.player.health > 0
                        and self.state.locations_explored < self.state.route_length
                        else "disabled"
                    ),
                )
            elif opens_terminal:
                button = ttk.Button(
                    actions,
                    text=action,
                    style=style,
                    command=self.on_open_terminal,
                )
            else:
                button = ttk.Button(
                    actions,
                    text=action,
                    state="disabled",
                    style=style,
                )
            button.grid(row=0, column=column, padx=(0, 6), sticky="ew")
            actions.columnconfigure(column, weight=1)
