from __future__ import annotations
from typing import List, Type
from modules.base import GameModule
from modules import MODULE_REGISTRY
from playerAgent import Player


class GameManager:
    def __init__(self, player: Player):
        self.player  = player
        self.modules: List[Type[GameModule]] = MODULE_REGISTRY

    def show_menu(self) -> Type[GameModule] | None:
        print("\n╔══════════════════════════╗")
        print("║   CyberTrainer  🛡️        ║")
        print("╠══════════════════════════╣")
        for i, mod in enumerate(self.modules, start=1):
            print(f"  {i}. {mod.name}")
            print(f"     {mod.description}")
        print("  0. Quit")
        print("╚══════════════════════════╝")

        choice = input("\nSelect a module: ").strip()
        if choice == "0" or choice.lower() == "q":
            return None
        try:
            idx = int(choice) - 1
            return self.modules[idx]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return self.show_menu()

    async def loop(self) -> None:
        """Main game loop — keeps presenting the menu until the player quits."""
        print(f"\nWelcome, {self.player}!")
        while True:
            mod_class = self.show_menu()
            if mod_class is None:
                print(f"\nFinal score: {self.player.getPoints()} pts. Goodbye!")
                break
            module = mod_class(self.player)
            await module.run()
