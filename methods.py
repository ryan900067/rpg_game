import json
import os
import random
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

try:
    from groq import Groq
except Exception:  # allows the game to run without the package installed
    Groq = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


lives = 5
GROQ_MODEL = "llama-3.3-70b-versatile"

NPC_PERSONALITIES = {
    "forest clearing": {
        "Eldra the Herbalist": "gentle, wise, and medicinal",
        "Bram the Trapper": "practical, sharp, and survival-focused",
        "Pip the Scout": "nervous but observant",
        "Moss the Forager": "earthy, calm, and patient",
        "Tamsin the Ranger": "disciplined and stoic",
        "Old Rowan": "mysterious and prophetic",
        "Clover the Merchant": "calculating and charming",
        "Wren the Storyteller": "dramatic and poetic",
    },
    "crystal cave": {
        "Neris the Geologist": "precise, analytical, and curious",
        "Durn the Miner": "brutal, blunt, and practical",
        "Ayla the Torchbearer": "brave and reassuring",
        "Glim the Hermit": "quiet and eccentric",
        "Vey the Cartographer": "methodical and exacting",
        "Orin the Smith": "strong-willed and dependable",
        "Sable the Crystal Keeper": "secretive and mystical",
        "Kett the Guide": "friendly and adventure-loving",
    },
    "roadside camp": {
        "Captain Marlow": "commanding and battle-hardened",
        "Ivo the Cook": "warm and lively",
        "Sera the Healer": "empathetic and calm",
        "Dax the Guard": "strict and watchful",
        "Nell the Courier": "quick-thinking and restless",
        "Rook the Gambler": "confident and risky",
        "Pella the Merchant": "sharp and opportunistic",
        "Tobin the Stablehand": "grounded and steady",
    },
    "shoreline": {
        "Maris the Fisher": "laid-back and observant",
        "Coral the Diver": "bold and fearless",
        "Finn the Netmaker": "patient and cunning",
        "Bex the Boatwright": "craftsman-like and practical",
        "Tide the Naturalist": "thoughtful and spiritual",
        "Luma the Pearl Trader": "smooth, charming, and shrewd",
        "Gale the Sailor": "reckless but charismatic",
        "Niko the Lookout": "alert and tense",
    },
    "harbor": {
        "Harbormaster Voss": "stern and disciplined",
        "Etta the Navigator": "cool-headed and strategic",
        "Jory the Dockworker": "gruff but dependable",
        "Mina the Shipwright": "precise and technical",
        "Calder the Boatswain": "aggressive and direct",
        "Rin the Tidecaller": "mystic and intense",
        "Boro the Fishmonger": "witty and blunt",
        "Willa the Pilot": "energetic and fearless",
    },
    "stadium": {
        "Announcer Vale": "loud and hype-driven",
        "Coach Rhea": "motivational and tactical",
        "Medic Sol": "professional and cautious",
        "Referee Kade": "strict and impartial",
        "Scout Brin": "energetic and eager",
        "Vendor Tully": "greedy but friendly",
        "Fan Jun": "chaotic and excited",
        "Trainer Oona": "disciplined and sharp",
    },
}

MONSTER_SPECIAL_ATTACKS = {
    "Skeleton": {"Bone Crash": {"damage_factor": 1.4, "chance": 0.35}},
    "Green Dragon": {"Flame Burst": {"damage_factor": 1.7, "chance": 0.45}},
    "Crystal Dragon": {"Prismatic Beam": {"damage_factor": 1.8, "chance": 0.5}},
    "Red Dragon": {"Firestorm": {"damage_factor": 1.75, "chance": 0.5}},
    "Headless Horseman": {"Soul Rend": {"damage_factor": 1.9, "chance": 0.4}},
    "Leviathan": {"Tidal Crush": {"damage_factor": 2.0, "chance": 0.55}},
    "Megalodon": {"Abyssal Bite": {"damage_factor": 1.9, "chance": 0.45}},
    "Prime Kyle Walker": {"Titan Breaker": {"damage_factor": 2.2, "chance": 0.6}},
}

MONSTER_PERSONALITIES = {
    "Skeleton": "cruel, bone-grinding, and opportunistic",
    "Green Dragon": "arrogant, cunning, and predatory",
    "Crystal Dragon": "ancient, cold, and calculating",
    "Red Dragon": "reckless, furious, and explosive",
    "Headless Horseman": "grim, relentless, and haunted",
    "Leviathan": "massive, patient, and overwhelming",
    "Megalodon": "feral, savage, and instinct-driven",
    "Prime Kyle Walker": "confident, ruthless, and battle-smart",
}


def formatted(value: str) -> str:
    """Normalize text for case-insensitive comparisons."""
    if value is None:
        raise TypeError("Input cannot be None.")
    return str(value).strip().lower()


class ListError(ValueError):
    """Raised when chest items and their weights have different lengths."""


@dataclass(frozen=True)
class GameMap:
    name: str
    npcs: tuple[str, ...]


@dataclass
class NPCProfile:
    name: str
    map_name: str
    role: str
    personality: str


def get_groq_client():
    """Return a configured Groq client or None if unavailable."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or Groq is None:
        return None
    return Groq(api_key=api_key)


def get_npc_profile(npc_name: str, map_name: str) -> NPCProfile:
    """Return a structured profile for an NPC; use Groq if available."""
    normalized_name = npc_name.strip()
    normalized_map = formatted(map_name)
    base_personality = NPC_PERSONALITIES.get(normalized_map, {}).get(normalized_name)
    if base_personality is None:
        # fallback if the NPC is not in the exact map data
        base_personality = "mysterious and unpredictable"

    role = "traveler"
    if "merchant" in normalized_name.lower() or "trader" in normalized_name.lower():
        role = "merchant"
    elif "guard" in normalized_name.lower() or "captain" in normalized_name.lower():
        role = "guardian"
    elif "healer" in normalized_name.lower() or "doctor" in normalized_name.lower():
        role = "healer"
    elif "smith" in normalized_name.lower() or "forge" in normalized_name.lower():
        role = "blacksmith"
    elif "dragon" in normalized_name.lower():
        role = "monster"
    elif "scout" in normalized_name.lower() or "ranger" in normalized_name.lower():
        role = "scout"

    prompt = (
        f"Create a short, vivid, single-sentence personality for {normalized_name}, "
        f"who is a {role} in {normalized_map}. Keep it in first-person style, "
        f"and make it feel like a believable fantasy NPC. "
        f"Example tone: 'I build homes with my hands and I never trust liars.'"
    )

    client = get_groq_client()
    if client is not None:
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You write vivid fantasy NPC personalities."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=80,
            )
            text = response.choices[0].message.content.strip()
            if text:
                personality = text
        except Exception:
            pass

    return NPCProfile(
        name=normalized_name,
        map_name=normalized_map,
        role=role,
        personality=personality if "personality" in locals() else base_personality,
    )


def describe_npc(npc_name: str, map_name: str) -> str:
    """Return a short, flavorful description with a personality-driven voice."""
    npc = get_npc_profile(npc_name, map_name)
    return f"{npc.name}: {npc.personality}"


def get_monster_special_attack(monster_name: str):
    """Return a special attack name and its definition if available."""
    parsed = formatted(monster_name)
    attack_table = MONSTER_SPECIAL_ATTACKS.get(parsed, {})
    if not attack_table:
        return None
    attack_name, details = random.choice(list(attack_table.items()))
    return {"name": attack_name, "details": details}


def decide_monster_attack(monster, player, *, use_groq: bool = True):
    """Choose a monster action dynamically, with Groq fallback."""
    monster_name = monster.name
    choice = {
        "kind": "basic",
        "damage": float(monster.attack_power),
        "message": f"{monster_name} lunges at you.",
    }

    special = get_monster_special_attack(monster_name)
    if special and monster.health <= monster.max_health * 0.6:
        if random.random() <= special["details"]["chance"]:
            choice = {
                "kind": "special",
                "name": special["name"],
                "damage": float(monster.attack_power * special["details"]["damage_factor"]),
                "message": f"{monster_name} unleashes {special['name']}!",
            }

    client = get_groq_client() if use_groq else None
    if client is not None:
        try:
            prompt = (
                f"You are the tactical brain for the monster {monster_name}. "
                f"The player stats are health={player.health}, strength={player.strength}, "
                f"attack_power={player.attack_power}, defense={player.defense}. "
                f"The monster health is {monster.health} and max health is {monster.max_health}. "
                f"Pick the smartest move in one sentence, with an action name and a value "
                f"like: 'special attack: Firestorm 25 damage' or 'basic attack: 18 damage'."
            )
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You choose the next best move for a monster."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=60,
            )
            text = response.choices[0].message.content.strip()
            if text:
                choice["message"] = text
                lower = text.lower()

                if "special" in lower and special:
                    choice["kind"] = "special"
                    choice["name"] = special["name"]
                    choice["damage"] = max(1, float(monster.attack_power * special["details"]["damage_factor"]))
                elif "basic" in lower or "attack" in lower:
                    choice["kind"] = "basic"
                    choice["damage"] = float(monster.attack_power)
        except Exception:
            pass

    return choice


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
}

MAP_MONSTERS = {
    "forest clearing": ("Skeleton", "Green Dragon"),
    "crystal cave": ("Crystal Dragon", "Red Dragon"),
    "roadside camp": ("Headless Horseman", "Skeleton"),
    "shoreline": ("Leviathan", "Megalodon"),
    "harbor": ("Green Dragon", "Red Dragon"),
    "stadium": ("Prime Kyle Walker", "Skeleton"),
}


def create_map(name: str) -> GameMap:
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
    def __init__(self, name: str, health: int, strength: int, speed: int,
                 dodge_rate: float, attack_power: float = 0):
        self.name = name
        self.health = health
        self.max_health = health
        self.strength = strength
        self.speed = speed
        self.dodge_rate = dodge_rate
        self.attack_power = attack_power
        self.special_attacks = MONSTER_SPECIAL_ATTACKS.get(name, {})
        self.ai_personality = MONSTER_PERSONALITIES.get(name, "cunning and ruthless")

    def take_damage(self, amount: float) -> int:
        self.health = max(0, self.health - max(0, amount))
        return self.health

    def take_normal_damage(self, amount: float) -> int:
        return self.take_damage(amount)

    def take_damage1(self, amount: float) -> int:
        return self.take_damage(amount)

    def attack(self) -> float:
        decision = decide_monster_attack(self, None, use_groq=False)
        return decision["damage"]

    def __str__(self) -> str:
        return (
            f"{self.name} — HP: {self.health}/{self.max_health}, "
            f"strength: {self.strength}, speed: {self.speed}, "
            f"ai: {self.ai_personality}"
        )


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


def open_chest(chest: list, probability: list) -> str:
    if not isinstance(chest, list) or not isinstance(probability, list):
        raise TypeError("Chest and probabilities must both be lists.")
    if len(chest) != len(probability):
        raise ListError("The probabilities and items are not equal.")
    if not chest:
        raise ValueError("The chest is empty.")
    if any(weight < 0 for weight in probability):
        raise ValueError("Probabilities cannot be negative.")
    if any(weight == 0 for weight in probability):
        raise ValueError("At least one probability must be greater than zero.")
    item = random.choices(chest, weights=probability, k=1)[0]
    print(f"You got {item}")
    return item


def flee_attempt(probability_table: dict, monster_name: str) -> bool:
    if monster_name not in probability_table:
        raise KeyError(f"Unknown monster: {monster_name}")
    chance = probability_table[monster_name]
    if not 0 <= chance <= 1:
        raise ValueError("Flee chance must be between 0, 1.")
    if random.random() < chance:
        print(f"You successfully fled from {monster_name}!")
        return True
    global lives
    lives -= 1
    print(f"You failed to flee from {monster_name}. Lives remaining: {lives}")
    return False


def choose_path(path: set, path_amount: int) -> set:
    if not isinstance(path, set) or any((type(n) is not int) for n in path):
        raise TypeError("Paths must be provided as a set of integers.")
    if len(path) < 2 or not isinstance(path_amount, int) or isinstance(path_amount, bool) or path_amount < 2:
        raise ValueError("At least two paths are required.")
    if any(n < 1 or n > path_amount for n in path):
        raise ValueError("Paths must be numbered between 1 and path_amount.")
    return path


def shop(price: float, selected_item: str, input_fn: Callable[[str], str] | None = None):
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
    if not isinstance(file_name, str) or not file_name.strip():
        raise ValueError("File name cannot be empty.")
    with open(f"{file_name}.txt", "a", encoding="utf-8") as file:
        file.write(f"{character.__class__.__name__}: {character.__dict__}\n")
    print("Character successfully saved.")


def access_attribute(attribute_name: str, character):
    if attribute_name not in attributes:
        raise ValueError("This attribute does not exist.")
    key = attribute_name.replace(" ", "_")
    if not hasattr(character, key):
        raise AttributeError(f"The character has no {attribute_name!r} attribute.")
    value = getattr(character, key)
    print(f"{attribute_name}: {value}")
    return value


def access_inventory(character):
    inventory = pd.DataFrame({"Item": character.inventory})
    print(inventory.to_string(index=False))
    return inventory
