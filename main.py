import ast
import random

import methods
import pandas as pd


possible_commands = (
    "access inventory", "save character", "load character", "check stats", "access attribute",
    "create new character", "continue", "exit"
)


class InvalidInputError(ValueError):
    """Raised when the player enters an unsupported choice."""


class VideoGame:
    """Player character and combat statistics."""

    MAX_LEVEL = 20
    MAX_HEALTH = 100
    MAX_STRENGTH = 20
    LEVEL_UP_COINS=250

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
        self.health = self.MAX_HEALTH
        print(
            f"{self.name} reached level {self.level}! "
            f"Gained {self.LEVEL_UP_COINS} coins and restored health to {self.MAX_HEALTH}."
        )
        return True

    def take_damage(self, amount: float) -> int:
        damage = max(0, amount - self.defense)
        self.health = max(0, self.health - damage)
        print(f"{self.name} takes {damage:g} damage.")
        return self.health

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
        if answer in ("y", "n"):
            return answer == "y"
        print("Please enter y or n.")


def fight(player: VideoGame, monster: methods.Monster) -> bool:
    """Run a turn-based encounter; return True if the player wins."""
    print(f"A {monster.name} appears!")
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
    else:
        print(f"Reward {reward!r} is not implemented yet.")


def visit_shop(player: VideoGame) -> None:
    """Offer a random item and apply the purchase if affordable."""
    item = random.choice(methods.possible_shop_items)
    price = random.randint(100, 200)
    purchase = methods.shop(price, item)
    if purchase is None:
        return
    if player.coins < price:
        print("You don't have enough coins.")
        return
    player.coins -= price
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
    if ask_yes_no(f"Open the {chest_name} chest? (y/n): "):
        apply_reward(player, methods.open_chest(chest, probability))


def run_adventure_stage(
    player: VideoGame,
    monster_name: str,
    chest_name: str,
    rest_name: str,
) -> tuple[VideoGame, bool]:
    """Run an encounter followed by its optional chest and rest stop."""
    if not run_encounter(player, methods.create_monster(monster_name)):
        return player, False
    if not game_is_active(player):
        return player, False

    offer_chest(player, chest_name)
    if not game_is_active(player):
        return player, False

    if ask_yes_no(f"Rest at {rest_name}? (y/n): "):
        player = run_menu(player)
    return player, game_is_active(player)


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
    print(f"Welcome, {player.name}! You venture through a vast forest.")

    print("Path 1: A forest clearing where skeletons gather.")
    print("Path 2: A cave where a crystal dragon guards a chest.")

    while True:
        try:
            chosen_path = int(input("Choose path 1 or 2: "))
            if chosen_path == 1:
                first_monster = "Skeleton"
                break
            elif chosen_path == 2:
                first_monster = "Crystal Dragon"
                break
            else:
                print("Choose either path 1 or path 2.")
        except ValueError:
            print("Choose either path 1 or path 2.")

    player, adventure_active = run_adventure_stage(
        player, first_monster, "wood", "the boulder"
    )

    if adventure_active:
        if chosen_path == 1:
            print("You continue through the forest and face the Green Dragon.")
            player, adventure_active = run_adventure_stage(
                player, "Green Dragon", "wood", "the forest clearing"
            )
        elif chosen_path == 2:
            print("You venture deeper into the cave and face the Red Dragon.")
            player, adventure_active = run_adventure_stage(
                player, "Red Dragon", "wood", "the cave entrance"
            )
        else:
            raise InvalidInputError("Choose either path 1 or path 2.")

    if adventure_active:
        print("The Headless Horseman blocks your path.")
        player, adventure_active = run_adventure_stage(
            player, "Headless Horseman", "silver", "the roadside camp"
        )

    if adventure_active:
        print("A Megalodon emerges from the water.")
        player, adventure_active = run_adventure_stage(
            player, "Megalodon", "gold", "the shoreline"
        )

    if adventure_active:
        print("The Leviathan rises for a boss fight.")
        player, adventure_active = run_adventure_stage(
            player, "Leviathan", "gold", "the harbor"
        )

    if adventure_active:
        print("You reach the stadium for the final boss fight against Prime Kyle Walker.")
        if fight(player, methods.create_monster("Prime Kyle Walker")):
            print("You defeated the final boss!")

    if not game_is_active(player):
        print("Game over.")
    print("Final character stats:")
    print(player)
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
