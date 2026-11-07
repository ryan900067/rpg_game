import random

import methods


possible_commands = (
    "save character", "check stats", "access attribute", "create new character", "exit"
)


class InvalidInputError(ValueError):
    """Raised when the player enters an unsupported choice."""


class VideoGame:
    """Player character and combat statistics."""

    MAX_LEVEL = 10
    LEVEL_UP_COINS = 100

    def __init__(self, health=100, strength=10, speed=10, level=1, name="Player",
                 coins=0, attack_power=10, defense=5):
        self.health = max(1, min(100, int(health)))
        self.strength = int(strength)
        self.speed = int(speed)
        self.level = max(1, min(self.MAX_LEVEL, int(level)))
        self.name = name.strip() or "Player"
        self.coins = max(0, int(coins))
        self.attack_power = float(attack_power)
        self.defense = float(defense)

    def level_up(self) -> bool:
        """Advance one level, grant coins, and restore health; return whether it succeeded."""
        if self.level >= self.MAX_LEVEL:
            print(f"{self.name} is already at the maximum level ({self.MAX_LEVEL}).")
            return False

        self.level += 1
        self.coins += self.LEVEL_UP_COINS
        self.health = 100
        print(
            f"{self.name} reached level {self.level}! "
            f"Gained {self.LEVEL_UP_COINS} coins and restored health to 100."
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
            level = int(input("Enter level (1–10): "))
            strength = int(input("Enter strength: "))
            speed = int(input("Enter speed: "))
            if not name:
                raise ValueError("Name cannot be empty.")
            if not 1 <= level <= 10:
                raise ValueError("Level must be between 1 and 10.")
            if strength < 0 or speed < 0:
                raise ValueError("Strength and speed cannot be negative.")
            return VideoGame(name=name, level=level, strength=strength, speed=speed)
        except ValueError as error:
            print(f"Invalid character details: {error}")
            if methods.formatted(input("Try again? (y/n): ")) != "y":
                raise SystemExit("Character creation cancelled.")
        finally:
            print("Character creation attempt finished.")


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
    while player.health > 0 and monster.health > 0:
        player.attack(monster)
        if monster.health > 0:
            player.take_damage(monster.attack())
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
        player.health = min(100, player.health + random.randint(10, 25))
        print(f"Health restored to {player.health}.")
    elif reward.upper() == "STRENGTH":
        player.strength += 5
        print("Strength increased by 5.")
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


def run_encounter(player: VideoGame, monster: methods.Monster) -> None:
    """Handle the player's choice to fight or flee."""
    choice = methods.formatted(input(f"A {monster.name} blocks the way. Fight or flee? "))
    if choice == "flee":
        if not methods.flee_attempt(methods.flee_probabilities, monster.name):
            fight(player, monster)
    elif choice == "fight":
        if fight(player, monster):
            visit_shop(player)
    else:
        raise InvalidInputError("Enter 'fight' or 'flee'.")


def run_menu(player: VideoGame) -> VideoGame:
    """Run the rest-stop menu and return the active character."""
    while methods.lives > 0 and player.health > 0:
        print("Available commands:", ", ".join(possible_commands))
        command = methods.formatted(input("Command: "))
        if command == "exit":
            break
        if command == "check stats":
            print(player)
        elif command == "save character":
            methods.save_character(player, input("File name (without .txt): "))
        elif command == "access attribute":
            methods.access_attribute(input("Attribute name: ").strip().lower(), player)
        elif command == "create new character":
            player = create_character_instance()
        else:
            print("Unknown command. Choose one from the list.")
    return player


def main() -> None:
    """Start the RPG adventure."""
    player = create_character_instance()
    print(f"Welcome, {player.name}! You venture through a vast forest.")

    path_encounters = {
        1: methods.Skeleton,
        2: methods.Crystal_Dragon,
    }
    print("Path 1: A forest clearing where skeletons gather.")
    print("Path 2: A cave where a crystal dragon guards a chest.")

    while True:
        try:
            chosen_path = int(input("Choose path 1 or 2: "))
            monster = path_encounters[chosen_path]
            break
        except (ValueError, KeyError):
            print("Choose either path 1 or path 2.")

    run_encounter(player, monster)

    if methods.lives > 0 and player.health > 0:
        if ask_yes_no("Open the wooden chest? (y/n): "):
            apply_reward(player, methods.open_chest(methods.wood_chest, methods.wood_prob))

    if methods.lives > 0 and player.health > 0:
        if ask_yes_no("Rest at the boulder? (y/n): "):
            player = run_menu(player)
        else:
            print("You continue toward the stadium and encounter Prime Kyle Walker.")
            run_encounter(player, methods.Prime_Kyle_Walker)

    if methods.lives <= 0 or player.health <= 0:
        print("Game over.")
    print("Final character stats:")
    print(player)
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
