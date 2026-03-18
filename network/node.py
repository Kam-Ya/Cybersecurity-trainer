from __future__ import annotations
import random
from typing import List, Optional


class Node:

    def __init__(self, name: str = "Node"):
        self.__infected: bool          = False
        self.__connections: List[Node] = []
        self.name: str                 = name
        self.text: str                 = f"I am {self.name}!"

    # ── Connections ───────────────────────────────────────────────────

    def connect(self, other: Node) -> None:
        if other not in self.__connections:
            self.__connections.append(other)
        if self not in other.__connections:
            other.__connections.append(self)

    def getConnections(self) -> List[Node]:
        return list(self.__connections)

    # ── Infection ─────────────────────────────────────────────────────

    def infect(self) -> None:
        self.__infected = True
        self.name = f"Evil {self.name}"       # ← rename to "Evil ..."
        self.text = f"I am {self.name}!"      # ← text reflects new name

    def isInfected(self) -> bool:
        return self.__infected

    def propagate(self) -> None:
        if not self.__connections:
            return
        clean = [n for n in self.__connections if not n.isInfected()]
        if not clean:
            print("[Node] No clean neighbours to infect.")
            return
        target = random.choice(clean)
        target.infect()
        print(f"[Node] Malware spread to {target.name}!")

    def find(self, index: int) -> Optional[Node]:
        if 0 <= index < len(self.__connections):
            return self.__connections[index]
        return None

    # ── Display ───────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Node(name={self.name}, infected={self.__infected}, "
            f"connections={len(self.__connections)})"
        )
