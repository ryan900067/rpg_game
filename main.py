import ast
from functools import wraps
import random

import methods
import pandas as pd


possible_commands = (
    "access inventory", "save character", "load character", "check stats", "access attribute",
    "create new character", "continue", "exit"
)


class InvalidInputError(ValueError):
    """Raised when the player enters an unsupported choice."""


SPECIAL_ATTACKS = {
    "Poison": {"price": 150, "aftershock_damage": 5},
}
CAMPAIGN_ENCOUNTERS = 8


def special_attack(name: str):
    """Decorate an attack with an owned special attack's effect."""
    if name not in SPECIAL_ATTACKS:
        raise ValueError(f"Unknown special attack: {name}")

    def decorate(attack):
        @wraps(attack)
        def wrapped(player, target):
            remaining_health = attack(player, target)
            attack_data = SPECIAL_ATTACKS[name]
            if name in player.inventory and target.health > 0:
                damage = attack_data["aftershock_damage"]
                target.take_damage(damage)
                print(f"{target.name} takes {damage} poison aftershock damage.")
            return target.health if name in player.inventory else remaining_health

        return wrapped

    return decorate


class VideoGame:
    """Player character and combat statistics."""

    MAX_LEVEL = 20
    MAX_HEALTH = 100
    MAX_STRENGTH = 20
    LEVEL_UP_COINS=250
    POISON_AFTERSHOCK_DAMAGE=5
    LEVEL_UP_ATTACK_BONUS = 2
    LEVEL_UP_DEFENSE_BONUS = 2
    LEVEL_UP_STRENGTH_BONUS = 1

    def __init__(self, health=100, strength=10, speed=10, name="Player",
                 coins=0, attack_power=10, defense=5):
        self.health = max(1, min(self.MAX_HEALTH, int(health)))
        self.strength = int(strength)
        if not 0 <= self.strength <= self.MAX_STRENGTH:
            raise ValueError(f"Strength must be between 0 and {self.MAX_STRENGTH}.")
        self.speed = int(speed)
        self.level = 1
        self.name = name.strip() or "Player"
        self.coins = max(0, int(coins))
        self.attack_power = float(attack_power)
        self.defense = float(defense)
        self.inventory = []
     

    def level_up(self) -> bool:
        """Advance one level, grant coins, and restore health; return whether it succeeded."""
        if self.level >= self.MAX_LEVEL:
            print(f"{self.name} is already at the maximum level ({self.MAX_LEVEL}).")
            return False

        self.level += 1
        self.coins += self.LEVEL_UP_COINS
        self.attack_power += self.LEVEL_UP_ATTACK_BONUS
        self.defense += self.LEVEL_UP_DEFENSE_BONUS
        self.strength = min(
            self.MAX_STRENGTH, self.strength + self.LEVEL_UP_STRENGTH_BONUS
        )
        self.health = self.MAX_HEALTH
        print(
            f"{self.name} reached level {self.level}! "
            f"Gained {self.LEVEL_UP_COINS} coins, improved combat stats, "
            f"and restored health to {self.MAX_HEALTH}."
        )
        return True

    def take_damage(self, amount: float) -> int:
        damage = max(0, amount - self.defense)
        self.health = max(0, self.health - damage)
        print(f"{self.name} takes {damage:g} damage.")
        return self.health

    @special_attack("Poison")
    def attack(self, target) -> int:
        damage = self.attack_power + self.strength * 0.25
        remaining_health = target.take_damage(damage)
        print(f"{self.name} hits {target.name} for {damage:g} damage.")
        return remaining_health

    def __str__(self):
        return (f"Name: {self.name}\nHealth: {self.health}\nStrength: {self.strength}\n"
                f"Speed: {self.speed}\nLevel: {self.level}\nCoins: {self.coins}\n"
                f"Attack power: {self.attack_power:g}\nDefense: {self.defense:g}")


def create_character_instance() -> VideoGame:
    """Prompt for character details and return a configured character."""
    while True:
        try:
            name = input("Enter character name: ").strip()
            strength = int(input(f"Enter strength (0-{VideoGame.MAX_STRENGTH}): "))
            if not name:
                raise ValueError("Name cannot be empty.")
            if not 0 <= strength <= VideoGame.MAX_STRENGTH:
                raise ValueError(
                    f"Strength must be between 0 and {VideoGame.MAX_STRENGTH}."
                )
            speed = int(input("Enter speed: "))
            if speed < 0:
                raise ValueError("Speed cannot be negative.")
            return VideoGame(name=name, strength=strength, speed=speed)
        except ValueError as error:
            print(f"Invalid character details: {error}")
            if methods.formatted(input("Try again? (y/n): ")) != "y":
                raise SystemExit("Character creation cancelled.")
        finally:
            print("Character creation attempt finished.")


def load_character_instance(file_name: str) -> VideoGame:
    """Load the latest character saved by methods.save_character()."""
    if not file_name.strip():
        raise ValueError("File name cannot be empty.")
    path = file_name if file_name.endswith(".txt") else f"{file_name}.txt"
    with open(path, "r", encoding="utf-8") as file:
        saved_lines = [line.strip() for line in file if line.strip()]
    if not saved_lines:
        raise ValueError("The save file is empty.")

    class_name, separator, saved_data = saved_lines[-1].partition(": ")
    if not separator or class_name != "VideoGame":
        raise ValueError("The latest entry is not a valid saved character.")
    try:
        data = ast.literal_eval(saved_data)
    except (SyntaxError, ValueError) as error:
        raise ValueError("The latest save entry is invalid.") from error
    if not isinstance(data, dict):
        raise ValueError("The save file does not contain character data.")

    character = VideoGame(
        health=data.get("health", 100),
        strength=data.get("strength", 10),
        speed=data.get("speed", 10),
        name=data.get("name", "Player"),
        coins=data.get("coins", 0),
        attack_power=data.get("attack_power", 10),
        defense=data.get("defense", 5),
    )
    level = int(data.get("level", 1))
    if not 1 <= level <= VideoGame.MAX_LEVEL:
        raise ValueError(f"Saved level must be between 1 and {VideoGame.MAX_LEVEL}.")
    inventory = data.get("inventory", [])
    if not isinstance(inventory, list):
        raise ValueError("Saved inventory must be a list.")
    character.level = level
    character.inventory = inventory
    print(f"Loaded character {character.name} from {path}.")
    return character


def ask_yes_no(prompt: str) -> bool:
    """Prompt until the player enters y or n."""
    while True:
        answer = methods.formatted(input(prompt))
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter y or n.")


def fight(player: VideoGame, monster: methods.Monster) -> bool:
    """Run a turn-based encounter; return True if the player wins."""
    print(f"A {monster.name} appears!")
    print(f"Monster AI: {monster.ai_personality}")
    player_max_health = VideoGame.MAX_HEALTH
    monster_max_health = max(1, monster.health)
    bar_width = 20
    last_actions = {"player": "Ready", "monster": "Waiting"}

    def display_status(round_number: int) -> None:
        fighters = []
        for side, name, health, max_health in (
            ("Player", player.name, player.health, player_max_health),
            ("Monster", monster.name, monster.health, monster_max_health),
        ):
            health_ratio = max(0, min(health / max_health, 1))
            filled = round(health_ratio * bar_width)
            condition = (
                "Defeated" if health <= 0
                else "Critical" if health_ratio <= 0.25
                else "Wounded" if health_ratio <= 0.6
                else "Healthy"
            )
            fighters.append({
                "Fighter": name,
                "Side": side,
                "Health": f"{health:g}/{max_health:g}",
                "HP": f"[{'#' * filled}{'-' * (bar_width - filled)}]",
                "Status": condition,
                "Last action": last_actions[side.lower()],
            })

        status = pd.DataFrame(
            fighters,
            columns=("Fighter", "Side", "Health", "HP", "Status", "Last action"),
        )
        print(f"\nRound {round_number} — Combat status")
        print(status.to_string(index=False))

    round_number = 1
    display_status(round_number)

    while player.health > 0 and monster.health > 0:
        monster_health_before = monster.health

        # Player attack sequence
        player.attack(monster)
        player_damage = monster_health_before - monster.health
        last_actions["player"] = f"Dealt {player_damage:g} damage"

        if monster.health > 0:
            player_health_before = player.health

            monster_decision = methods.decide_monster_attack(monster, player)
            damage = monster_decision["damage"]
            if monster_decision["kind"] == "special":
                print(f"{monster.name} uses {monster_decision['name']}!")
            else:
                print(f"{monster.name} uses {monster_decision['message']}")

            player.take_damage(damage)
            player_damage_taken = player_health_before - player.health
            last_actions["monster"] = f"Dealt {player_damage_taken:g} damage"
            last_actions["player"] = (
                f"Dealt {player_damage:g}; took {player_damage_taken:g} damage"
            )

        display_status(round_number)
        round_number += 1

    if player.health > 0:
        print(f"You defeated the {monster.name}!")
        player.level_up()
        return True

    print("You were defeated.")
    methods.lives -= 1
    return False

    def display_status(round_number: int) -> None:
        fighters = []
        for side, name, health, max_health in (
            ("Player", player.name, player.health, player_max_health),
            ("Monster", monster.name, monster.health, monster_max_health),
        ):
            health_ratio = max(0, min(health / max_health, 1))
            filled = round(health_ratio * bar_width)
            condition = (
                "Defeated" if health <= 0
                else "Critical" if health_ratio <= 0.25
                else "Wounded" if health_ratio <= 0.6
                else "Healthy"
            )
            fighters.append({
                "Fighter": name,
                "Side": side,
                "Health": f"{health:g}/{max_health:g}",
                "HP": f"[{'#' * filled}{'-' * (bar_width - filled)}]",
                "Status": condition,
                "Last action": last_actions[side.lower()],
            })

        status = pd.DataFrame(
            fighters,
            columns=("Fighter", "Side", "Health", "HP", "Status", "Last action"),
        )
        print(f"\nRound {round_number} — Combat status")
        print(status.to_string(index=False))

    round_number = 1
    display_status(round_number)
    while player.health > 0 and monster.health > 0:
        monster_health_before = monster.health
        player.attack(monster)
        player_damage = monster_health_before - monster.health
        last_actions["player"] = f"Dealt {player_damage:g} damage"
        if monster.health > 0:
            player_health_before = player.health
            player.take_damage(monster.attack())
            player_damage_taken = player_health_before - player.health
            last_actions["monster"] = f"Dealt {player_damage_taken:g} damage"
            last_actions["player"] = (
                f"Dealt {player_damage:g}; took {player_damage_taken:g} damage"
            )
        display_status(round_number)
        round_number += 1
    if player.health > 0:
        print(f"You defeated the {monster.name}!")
        player.level_up()
        return True
    print("You were defeated.")
    methods.lives -= 1
    return False


def apply_reward(player: VideoGame, reward: str) -> None:
    """Apply a supported chest or shop reward."""
    if reward.endswith("G") and reward[:-1].isdigit():
        amount = int(reward[:-1])
        player.coins += amount
        print(f"You gained {amount} coins.")
    elif reward.upper() == "HP":
        player.health = min(
            VideoGame.MAX_HEALTH, player.health + random.randint(10, 25)
        )
        print(f"Health restored to {player.health}.")
    elif reward.upper() == "STRENGTH":
        strength_increase = min(5, VideoGame.MAX_STRENGTH - player.strength)
        player.strength += strength_increase
        if strength_increase:
            print(f"Strength increased by {strength_increase}.")
        else:
            print(f"Strength is already at the maximum ({VideoGame.MAX_STRENGTH}).")
    elif reward == "X2Stats":
        player.attack_power *= 2
        print("Attack power doubled.")
    elif reward in {str(boost) for boost in methods.permanent_boosts.values()}:
        multiplier = float(reward)
        player.attack_power *= multiplier
        print(f"Attack power permanently increased by {multiplier - 1:.0%}.")
    else:
        print(f"Reward {reward!r} is not implemented yet.")


def visit_shop(player: VideoGame) -> None:
    """Offer a random item and apply the purchase if affordable."""
    available_items = methods.possible_shop_items
    if "Poison" not in player.inventory:
        available_items += ("Poison",)
    item = random.choice(available_items)
    price = (
        SPECIAL_ATTACKS[item]["price"]
        if item in SPECIAL_ATTACKS
        else random.randint(100, 200)
    )
    purchase = methods.shop(price, item)
    if purchase is None:
        return
    if player.coins < price:
        print("You don't have enough coins.")
        return
    player.coins -= price
    if item in SPECIAL_ATTACKS:
        player.inventory.append(item)
        print(f"Learned the {item} special attack.")
    else:
        apply_reward(player, item)
    print(f"Purchased {item} for {price} coins.")


def run_encounter(player: VideoGame, monster: methods.Monster) -> bool:
    """Handle the player's choice to fight or flee; return whether they survived."""
    choice = methods.formatted(input(f"A {monster.name} blocks the way. Fight or flee? "))
    if choice == "flee":
        if methods.flee_attempt(methods.flee_probabilities, monster.name):
            return True
        elif fight(player, monster):
            return True
        else:
            return False
    elif choice == "fight":
        if fight(player, monster):
            visit_shop(player)
            return True
        else:
            return False
    else:
        raise InvalidInputError("Enter 'fight' or 'flee'.")
    return False


def game_is_active(player: VideoGame) -> bool:
    """Return whether the player can continue the adventure."""
    return methods.lives > 0 and player.health > 0


def offer_chest(player: VideoGame, chest_name: str) -> None:
    """Offer a chest and apply its reward if the player opens it."""
    chest, probability = methods.chest_dict[chest_name]
    display_name = "wooden" if chest_name == "wood" else chest_name
    if ask_yes_no(f"Open the {display_name} chest? (y/n): "):
        apply_reward(player, methods.open_chest(chest, probability))


def offer_random_chest(player: VideoGame) -> None:
    """Offer a randomly spawned chest, if one appears after the encounter."""
    chest_name = methods.roll_chest_name()
    if chest_name is None:
        print("No chest appears nearby this time.")
        return
    display_name = "wooden" if chest_name == "wood" else chest_name
    print(f"You discover a {display_name} chest!")
    offer_chest(player, chest_name)


def run_exploration(player: VideoGame, destination: str) -> VideoGame:
    """Offer a random exploration event between encounters."""
    event = methods.roll_exploration_event()
    if event is None:
        print(f"\nThe trail to {destination.title()} is quiet.")
        return player

    print(f"\nOn the way to {destination.title()}...")
    scene = f"{event['scene']} on the road to {destination.title()}"
    print(methods.generate_narrative(
        scene, tone="adventurous fantasy", player_name=player.name
    ))
    if not ask_yes_no(event["prompt"]):
        print("You leave the discovery behind and continue onward.")
        return player

    if event["kind"] == "spring":
        healing = random.randint(20, 35)
        player.health = min(VideoGame.MAX_HEALTH, player.health + healing)
        print(f"You rest at the spring and recover health to {player.health}.")
    elif event["kind"] == "cache":
        if random.random() < 0.7:
            apply_reward(player, random.choice(("100G", "200G", "500G")))
        else:
            damage = random.randint(8, 18)
            print("A hidden snare springs from the cache!")
            player.take_damage(damage)
    elif event["kind"] == "traveler":
        reward = random.choice(("HP", "100G", "Strength"))
        print("The traveler thanks you with a small reward.")
        apply_reward(player, reward)
    elif event["kind"] == "shrine":
        if random.random() < 0.5:
            player.attack_power += 2
            print("The rune sharpens your attacks. Attack power increased by 2.")
        else:
            player.defense += 1
            print("The rune hardens your resolve. Defense increased by 1.")
    elif event["kind"] == "shortcut":
        if random.random() < 0.5:
            apply_reward(player, "250G")
        else:
            damage = random.randint(10, 25)
            print("The unstable path gives way beneath you!")
            player.take_damage(damage)
    else:
        raise ValueError(f"Unknown exploration event: {event['kind']}")

    return player


def show_map(
    map_name: str,
    *,
    player_name: str = "the hero",
    monster_name: str | None = None,
    show_npcs: bool = True,
) -> methods.GameMap:
    """Introduce a map with narrative and optionally display its NPCs."""
    game_map = methods.create_map(map_name)
    print(f"\nYou arrive at {game_map.name}.")
    scene = f"the {game_map.name.lower()}"
    if monster_name:
        scene += f", with {monster_name} blocking the way"
    print(methods.generate_narrative(scene, player_name=player_name))
    if show_npcs:
        show_npcs_on_map(game_map, map_name)
    return game_map


def show_npcs_on_map(game_map: methods.GameMap, map_name: str) -> None:
    """Show the local NPCs outside of an active battle."""
    print("\nPeople nearby:")
    for npc in game_map.npcs:
        print(f"  - {methods.describe_npc(npc, map_name)}")


def run_adventure_stage(
    player: VideoGame,
    monster_name: str,
    map_name: str,
) -> tuple[VideoGame, bool]:
    """Run an encounter followed by a chance chest and optional rest stop."""
    game_map = show_map(
        map_name, player_name=player.name, monster_name=monster_name, show_npcs=False
    )
    if not run_encounter(player, methods.create_monster(monster_name)):
        return player, False
    if not game_is_active(player):
        return player, False

    show_npcs_on_map(game_map, map_name)
    offer_random_chest(player)
    if not game_is_active(player):
        return player, False

    if ask_yes_no(f"Rest at {game_map.name}? (y/n): "):
        player = run_menu(player)
    return player, game_is_active(player)


def create_adventure_stages(route: int) -> list[tuple[str, str]]:
    """Build a longer route with a randomized, non-repeating set of monsters."""
    route_monsters = {
        1: ("Skeleton", "Green Dragon"),
        2: ("Crystal Dragon", "Red Dragon"),
    }
    if route not in route_monsters:
        raise ValueError("Route must be 1 or 2.")

    required_monsters = route_monsters[route]
    candidates = [
        monster.name
        for monster in methods.list_of_monsters
        if monster.name not in (*required_monsters, "Prime Kyle Walker")
    ]
    selected_monsters = list(required_monsters)
    selected_monsters.extend(
        random.sample(candidates, CAMPAIGN_ENCOUNTERS - len(selected_monsters))
    )
    random.shuffle(selected_monsters)

    stages = []
    for monster_name in selected_monsters:
        possible_maps = [
            map_name
            for map_name, monster_names in methods.MAP_MONSTERS.items()
            if monster_name in monster_names and map_name != "stadium"
        ]
        if not possible_maps:
            raise ValueError(f"No map is configured for {monster_name}.")
        stages.append((monster_name, random.choice(possible_maps)))
    return stages


def run_menu(player: VideoGame) -> VideoGame:
    """Run the rest-stop menu and return the active character."""
    while methods.lives > 0 and player.health > 0:
        print("Available commands:", ", ".join(possible_commands))
        command = methods.formatted(input("Command: "))
        if command == "continue":
            print("Continuing your adventure...")
            break
        if command == "exit":
            break
        if command == "check stats":
            print(player)
        elif command == "save character":
            methods.save_character(player, input("File name (without .txt): "))
        elif command == "load character":
            try:
                player = load_character_instance(input("File name (with or without .txt): "))
            except (OSError, TypeError, ValueError) as error:
                print(f"Could not load character: {error}")
        elif command == "access attribute":
            methods.access_attribute(input("Attribute name: ").strip().lower(), player)
        elif command == "access inventory":
            methods.access_inventory(player)
        elif command == "create new character":
            player = create_character_instance()
        else:
            print("Unknown command. Choose one from the list.")
    return player


def main() -> None:
    """Start the RPG adventure."""
    player = create_character_instance()
    print(f"Welcome, {player.name}!")

    print("Path 1: The forest route, haunted by Skeletons and a Green Dragon.")
    print("Path 2: The cave route, guarded by a Crystal Dragon and a Red Dragon.")

    while True:
        try:
            chosen_path = int(input("Choose path 1 or 2: "))
            if chosen_path == 1:
                break
            elif chosen_path == 2:
                break
            else:
                print("Choose either path 1 or path 2.")
        except ValueError:
            print("Choose either path 1 or path 2.")

    adventure_stages = create_adventure_stages(chosen_path)
    monster_order = [monster_name for monster_name, _ in adventure_stages]
    monster_order.append("Prime Kyle Walker")
    print()
    print(methods.generate_story(player.name, monster_order))
    print()

    adventure_active = True
    for index, stage in enumerate(adventure_stages):
        if not adventure_active:
            break
        monster_name, map_name = stage
        player, adventure_active = run_adventure_stage(
            player, monster_name, map_name
        )
        if adventure_active:
            next_map = (
                adventure_stages[index + 1][1]
                if index + 1 < len(adventure_stages)
                else "stadium"
            )
            player = run_exploration(player, next_map)
            adventure_active = game_is_active(player)

    if adventure_active:
        print("You reach the stadium for the final boss fight against Prime Kyle Walker.")
        stadium = show_map(
            "stadium", player_name=player.name, monster_name="Prime Kyle Walker",
            show_npcs=False,
        )
        if fight(player, methods.create_monster("Prime Kyle Walker")):
            print("You defeated the final boss!")
            show_npcs_on_map(stadium, "stadium")
            offer_random_chest(player)

    if not game_is_active(player):
        print("Game over.")
    print("Final character stats:")
    print(player)
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
