import random

lives = 3


def formatted(value: str) -> str:
    """Normalize user input for comparison."""
    return value.strip().lower()


class ListError(ValueError):
    """Raised when a chest's probabilities do not match its item list."""

    pass


attributes = (
    "health",
    "strength",
    "speed",
    "name",
    "level",
    "coins",
    "attack power",
    "defense",
)

probabilities_used = False

permanent_boosts = {
    "Tier 1": 1.15,
    "Tier 2": 1.30,
    "Tier 3": 1.40,
}

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
    """Simple monster model used in encounters."""

    def __init__(self, name: str, health: int, strength: int, speed: int, dodge_rate: float, attack_power: float = 0.0):
        self.name = name
        self.health = health
        self.strength = strength
        self.speed = speed
        self.dodge_rate = dodge_rate
        self.attack_power = attack_power

    def take_damage(self, amount: float) -> int:
        self.health = max(0, self.health - amount)
        return self.health

    def take_normal_damage(self, amount: float) -> int:
        return self.take_damage(amount)

    def take_damage1(self, amount: float) -> int:
        return self.take_damage(amount)

    def attack(self) -> float:
        return self.attack_power

    def __str__(self) -> str:
        return (
            f"Monster: {self.name} | Health: {self.health} | Strength: {self.strength} "
            f"| Speed: {self.speed} | Dodge rate: {self.dodge_rate}"
        )


Skeleton = Monster("Skeleton", 50, 10, 20, 0.05)
Crystal_Dragon = Monster("Crystal Dragon", 150, 25, 5, 0.07)
Prime_Kyle_Walker = Monster("Prime Kyle Walker", 90, 30, 20, 0.20)
Green_Dragon = Monster("Green Dragon", 105, 20, 10, 0.10)
list_of_monsters = [Skeleton, Crystal_Dragon, Prime_Kyle_Walker, Green_Dragon]


# List of drop rates of each chest
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
    """Randomly choose an item from a chest using weighted probabilities."""
    if not isinstance(chest, list) or not isinstance(probability, list):
        raise TypeError("Chest and probability must both be lists.")
    if len(chest) != len(probability):
        raise ListError("The probabilities and items are not equal.")
    if not chest:
        raise ValueError("The chest is empty.")

    selected_item = random.choices(chest, weights=probability, k=1)[0]
    print(f"You got {selected_item}")
    return selected_item


def flee_attempt(flee_probabilities: dict, monster_name: str) -> bool:
    """Attempt to escape from a monster based on its flee chance."""
    if monster_name not in flee_probabilities:
        raise KeyError(f"{monster_name} is not in the flee probability table.")

    if random.random() < flee_probabilities[monster_name]:
        print(f"You have successfully fled from {monster_name}!")
        return True

    print(f"You tried to run from {monster_name} and failed miserably.")
    global lives
    lives -= 1
    return False


def choose_path(path: set, path_amount: int) -> set:
    """Validate the provided path set and return the available path numbers."""
    if not isinstance(path, set):
        raise TypeError("Set of paths is not correct.")
    if len(path) <= 1:
        raise ValueError("The number of paths has to be greater than 1.")
    if any(not isinstance(number, int) for number in path):
        raise TypeError("All path values must be integers.")
    if not isinstance(path_amount, int) or path_amount < 1:
        raise ValueError("path_amount must be a positive integer.")

    return set(range(1, path_amount + 1))


def shop(price: float, selected_item: str):
    """Ask whether the player wants to buy an item at the supplied price."""
    answer = formatted(input(f"Would you like to buy {selected_item} for {price}? "))
    if answer == "y":
        print(f"Shop Item: {selected_item}\nPrice: {price}")
        return {"item": selected_item, "price": float(price)}
    if answer == "n":
        print("Continuing...")
        return None

    print("Invalid answer")
    return None


def save_character(character, file_name: str):
    """Append a character's state to a text file."""
    with open(f"{file_name}.txt", "a", encoding="utf-8") as file:
        file.write(f"{character.__class__.__name__}: {character.__dict__}\n")
    print("File writing done. Character successfully saved.")


def access_attribute(attribute_name: str, character):
    """Display and return a supported character attribute."""
    if attribute_name not in attributes:
        raise IndexError("This attribute does not exist.")

    # The display label "attack power" maps to the Python attribute attack_power.
    attribute_key = attribute_name.replace(" ", "_")
    if not hasattr(character, attribute_key):
        raise AttributeError(f"The character has no {attribute_name!r} attribute.")

    value = getattr(character, attribute_key)
    print(f"{attribute_name}: {value}")
    return value
