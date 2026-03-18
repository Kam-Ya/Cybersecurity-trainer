from __future__ import annotations
import random
from modules.base import GameModule
from playerAgent import Player
from network.node import Node


class NetworkModule(GameModule):
    name        = "Network Inspection"
    description = "Inspect network nodes and flag infected ones before malware spreads."

    def __init__(self, player: Player):
        super().__init__(player)
        self.nodes: list[Node] = []

    async def run(self) -> int:
        # ── Setup ──────────────────────────────────────────────────────
        inp = self._get_node_count()

        self.nodes = [Node(name=f"Node-{i}") for i in range(inp)]

        # Connect each node to the next (linear chain)
        for i in range(len(self.nodes) - 1):
            self.nodes[i].connect(self.nodes[i + 1])

        # Infect one random node to start
        random.choice(self.nodes).infect()

        # ── Game loop ──────────────────────────────────────────────────
        earned = 0
        print(f"\n=== {self.name} ===")
        print(f"{len(self.nodes)} nodes in network. Inspect and flag infected ones.\n")

        while True:
            raw = input(f"Which node to check? (0 to {len(self.nodes) - 1}, -1 to exit): ").strip()

            try:
                check = int(raw)
            except ValueError:
                print("Please enter a number.")
                continue

            if check == -1:
                break

            if check < 0 or check >= len(self.nodes):
                print(f"Invalid node. Choose 0–{len(self.nodes) - 1}.")
                continue

            target_node = self.nodes[check]
            print(f"\n[{target_node.name}] {target_node.text}")

            flag = input("Flag as infected? (Y/N): ").strip().upper()

            if target_node.isInfected() and flag == "Y":
                pts = 100
                self.player.addPoints(pts)
                earned += pts
                print(f"[+] Correct! +{pts} pts | Total: {self.player.getPoints()}")

            elif not target_node.isInfected() and flag == "Y":
                pts = 50
                self.player.addPoints(-pts)
                earned -= pts
                print(f"[-] False positive! -{pts} pts | Total: {self.player.getPoints()}")

            elif target_node.isInfected() and flag == "N":
                target_node.propagate()
                print("[!] Missed infected node — malware is spreading!")

            else:
                print(f"[✓] {target_node.name} is clean.")

        print(f"\n[+] Network round complete. Points earned: {earned} | Total: {self.player.getPoints()}")
        return earned

    # ── Helpers ────────────────────────────────────────────────────────

    def _get_node_count(self) -> int:
        while True:
            raw = input("How many nodes: ").strip()
            try:
                n = int(raw)
                if n >= 1:
                    return n
                print("Must be at least 1.")
            except ValueError:
                print("Please enter a number.")
