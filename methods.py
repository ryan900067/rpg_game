from collections.abc import Callable
from dataclasses import dataclass
import random
import main
import pandas as pd

lives = 5


def formatted(value: str) -> str:
    """Normalize text for case-insensitive comparisons."""
    if value is None:
        raise TypeError("Input cannot be None.")
    return str(value).strip().lower()


class ListError(ValueError):
    """Raised when chest items and their weights have different lengths."""


@dataclass(frozen=True)
class GameMap:
    """A game location and its immutable NPC roster."""

    name: str
    npcs: tuple[str, ...]


MAP_NPCS = {
    "forest clearing": (
        "Eldra the Herbalist", "Bram the Trapper", "Pip the Scout", "Moss the Forager",
        "Tamsin the Ranger", "Old Rowan", "Clover the Merchant", "Wren the Storyteller",
    ),
    "crystal cave": (
        "Neris the Geologist", "Durn the Miner", "Ayla the Torchbearer", "Glim the Hermit",
        "Vey the Cartographer", "Orin the Smith", "Sable the Crystal Keeper", "Kett the Guide",
    ),
    "roadside camp": (
        "Captain Marlow", "Ivo the Cook", "Sera the Healer", "Dax the Guard",
        "Nell the Courier", "Rook the Gambler", "Pella the Merchant", "Tobin the Stablehand",
    ),
    "shoreline": (
        "Maris the Fisher", "Coral the Diver", "Finn the Netmaker", "Bex the Boatwright",
        "Tide the Naturalist", "Luma the Pearl Trader", "Gale the Sailor", "Niko the Lookout",
    ),
    "harbor": (
        "Harbormaster Voss", "Etta the Navigator", "Jory the Dockworker", "Mina the Shipwright",
        "Calder the Boatswain", "Rin the Tidecaller", "Boro the Fishmonger", "Willa the Pilot",
    ),


     "stadium": (
        "Announcer Vale", "Coach Rhea", "Medic Sol", "Referee Kade",
        "Scout Brin", "Vendor Tully", "Fan Jun", "Trainer Oona",
    ),
    "volcano summit": (
        "Lava Rock Zombie", "Magma Golem", "Firefly Keeper", "Ashen Scout",
    ),
}

MAP_MONSTERS={
    "forest clearing": ("Skeleton", "Green Dragon"),
    "crystal cave": ("Crystal Dragon", "Red Dragon"),
    "roadside camp": ("Headless Horseman", "Skeleton"),
    "shoreline": ("Leviathan", "Megalodon"),
    "harbor": ("Green Dragon", "Red Dragon"),
    "stadium": ("Prime Kyle Walker", "Skeleton"),
}


def create_map(name: str) -> GameMap:
    """Instantiate a known map with its fixed NPC roster."""
    if not isinstance(name, str):
        raise TypeError("Map name must be a string.")
    key = formatted(name)
    if key not in MAP_NPCS:
        raise ValueError(f"Unknown map: {name}")
    return GameMap(name=key.title(), npcs=MAP_NPCS[key])


attributes = (
    "health", "strength", "speed", "name", "level", "coins", "attack power", "defense"
)
permanent_boosts = {"Tier 1": 1.15, "Tier 2": 1.30, "Tier 3": 1.40}
possible_shop_items = ("HP", "Strength", "X2Stats")
flee_probabilities = {
    "Skeleton": 0.8,
    "Red Dragon": 0.75,
    "Headless Horseman": 0.10,
    "Crystal Dragon": 0.4,
    "Prime Kyle Walker": 0.0,
    "Green Dragon": 0.60,
    "Leviathan": 0.10,
    "Megalodon": 0.20,
}


class Monster:
    """A combat opponent."""

    def __init__(self, name: str, health: int, strength: int, speed: int,
                 dodge_rate: float, attack_power: float = 0):
        self.name = name
        self.health = health
        self.strength = strength
        self.speed = speed
        self.dodge_rate = dodge_rate
        self.attack_power = attack_power

    def take_damage(self, amount: float) -> int:
        self.health = max(0, self.health - max(0, amount))
        return self.health

    def take_normal_damage(self, amount: float) -> int:
        return self.take_damage(amount)

    def take_damage1(self, amount: float) -> int:
        return self.take_damage(amount)

    def attack(self) -> float:
        return self.attack_power

    def __str__(self) -> str:
        return f"{self.name} — HP: {self.health}, strength: {self.strength}, speed: {self.speed}"


Skeleton = Monster("Skeleton", 50, 10, 20, 0.05, 10)
Crystal_Dragon = Monster("Crystal Dragon", 150, 25, 5, 0.07, 25)
Prime_Kyle_Walker = Monster("Prime Kyle Walker", 90, 30, 20, 0.20, 30)
Green_Dragon = Monster("Green Dragon", 105, 20, 10, 0.10, 20)
Red_Dragon = Monster("Red Dragon", 120, 25, 15, 0.10, 25)
Headless_Horseman = Monster("Headless Horseman", 130, 30, 25, 0.15, 30)
Leviathan = Monster("Leviathan", 200, 35, 10, 0.10, 35)
Megalodon = Monster("Megalodon", 180, 30, 25, 0.20, 30)
list_of_monsters = [
    Skeleton,
    Crystal_Dragon,
    Prime_Kyle_Walker,
    Green_Dragon,
    Red_Dragon,
    Headless_Horseman,
    Leviathan,
    Megalodon,
]


def create_monster(name: str) -> Monster:
    """Return a fresh instance of a monster in the adventure roster."""
    for monster in list_of_monsters:
        if monster.name == name:
            return Monster(
                monster.name,
                monster.health,
                monster.strength,
                monster.speed,
                monster.dodge_rate,
                monster.attack_power,
            )
    raise ValueError(f"Unknown monster: {name}")


wood_chest = ["100G", "200G", "500G", "HP"]
wood_prob = [0.60, 0.20, 0.13, 0.07]
silver_chest = ["250G", "500G", "1000G", "HP", "STRENGTH", "X2Stats"]
silver_prob = [0.199, 0.50, 0.15, 0.10, 0.05, 0.001]
gold_chest = ["1000G", "2500G", "5000G", "HP", "STRENGTH", "X2Stats", str(permanent_boosts["Tier 1"])]
gold_prob = [0.10, 0.20, 0.20, 0.20, 0.15, 0.10, 0.05]
chest_dict = {
    "wood": (wood_chest, wood_prob),
    "silver": (silver_chest, silver_prob),
    "gold": (gold_chest, gold_prob),
}


def open_chest(chest: list, probability: list) -> str:
    """Select, print, and return a weighted chest reward."""
    if not isinstance(chest, list) or not isinstance(probability, list):
        raise TypeError("Chest and probabilities must both be lists.")
    if len(chest) != len(probability):
        raise ListError("The probabilities and items are not equal.")
    if not chest:
        raise ValueError("The chest is empty.")
    if any(weight < 0 for weight in probability):
        raise ValueError("Probabilities cannot be negative.")
    if any(weight == 0 for weight in probability):
        # zero-weight entries are valid, but an all-zero selection would fail; reject as invalid input.
        raise ValueError("At least one probability must be greater than zero.")
    item = random.choices(chest, weights=probability, k=1)[0]
    print(f"You got {item}")
    return item


def flee_attempt(probability_table: dict, monster_name: str) -> bool:
    """Attempt to flee; a failed escape costs one life."""
    if monster_name not in probability_table:
        raise KeyError(f"Unknown monster: {monster_name}")
    chance = probability_table[monster_name]
    if not 0 <= chance <= 1:
        raise ValueError("Flee chance must be between 0 and 1.")
    if random.random() < chance:
        print(f"You successfully fled from {monster_name}!")
        return True
    global lives
    lives -= 1
    print(f"You failed to flee from {monster_name}. Lives remaining: {lives}")
    return False


def choose_path(path: set, path_amount: int) -> set:
    """Validate the path options and return the valid available paths."""
    if not isinstance(path, set) or any((type(n) is not int) for n in path):
        raise TypeError("Paths must be provided as a set of integers.")
    if len(path) < 2 or not isinstance(path_amount, int) or isinstance(path_amount, bool) or path_amount < 2:
        raise ValueError("At least two paths are required.")
    if any(n < 1 or n > path_amount for n in path):
        raise ValueError("Paths must be numbered between 1 and path_amount.")
    return path


def shop(
    price: float,
    selected_item: str,
    input_fn: Callable[[str], str] | None = None,
):
    """Ask whether to buy an offered item and return purchase details."""
    if price < 0:
        raise ValueError("Price cannot be negative.")
    read_input = input if input_fn is None else input_fn
    answer = formatted(read_input(f"Buy {selected_item} for {price} coins? (y/n): "))
    if answer == "y":
        return {"item": selected_item, "price": float(price)}
    if answer == "n":
        print("Continuing...")
        return None
    print("Please answer y or n.")
    return None


def save_character(character, file_name: str) -> None:
    """Append a character's attributes to a UTF-8 text file."""
    if not isinstance(file_name, str) or not file_name.strip():
        raise ValueError("File name cannot be empty.")
    with open(f"{file_name}.txt", "a", encoding="utf-8") as file:
        file.write(f"{character.__class__.__name__}: {character.__dict__}\n")
    print("Character successfully saved.")


def access_attribute(attribute_name: str, character):
    """Display and return a supported character attribute."""
    if attribute_name not in attributes:
        raise ValueError("This attribute does not exist.")
    key = attribute_name.replace(" ", "_")
    if not hasattr(character, key):
        raise AttributeError(f"The character has no {attribute_name!r} attribute.")
    value = getattr(character, key)
    print(f"{attribute_name}: {value}")
    return value


def access_inventory(character):
    """Display and return the character's inventory as a pandas DataFrame."""
    inventory = pd.DataFrame({"Item": character.inventory})
    print(inventory.to_string(index=False))
    return inventory
