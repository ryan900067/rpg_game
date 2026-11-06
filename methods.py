import random

lives = 3


def formatted(value: str) -> str:
    """Normalize text for case-insensitive comparisons."""
    return value.strip().lower()


class ListError(ValueError):
    """Raised when chest items and their weights have different lengths."""


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
list_of_monsters = [Skeleton, Crystal_Dragon, Prime_Kyle_Walker, Green_Dragon]

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
    """Validate the path options and return numbered available paths."""
    if not isinstance(path, set) or any(type(n) is not int for n in path):
        raise TypeError("Paths must be provided as a set of integers.")
    if len(path) <= 1 or type(path_amount) is not int or path_amount < 2:
        raise ValueError("At least two paths are required.")
    return set(range(1, path_amount + 1))


def shop(price: float, selected_item: str):
    """Ask whether to buy an offered item and return purchase details."""
    if price < 0:
        raise ValueError("Price cannot be negative.")
    answer = formatted(input(f"Buy {selected_item} for {price} coins? (y/n): "))
    if answer == "y":
        return {"item": selected_item, "price": float(price)}
    if answer == "n":
        print("Continuing...")
        return None
    print("Please answer y or n.")
    return None


def save_character(character, file_name: str) -> None:
    """Append a character's attributes to a UTF-8 text file."""
    if not file_name.strip():
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
