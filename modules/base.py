from __future__ import annotations
from abc import ABC, abstractmethod
from playerAgent import Player


class GameModule(ABC):
    """
    Every game module must implement these.
    """
    name: str        # Display name in the menu
    description: str # One-line description shown to player

    def __init__(self, player: Player):
        self.player = player

    @abstractmethod
    async def run(self) -> int:
        """
        Execute the module. Returns points earned this round.
        """
        ...

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
