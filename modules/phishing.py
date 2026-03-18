from __future__ import annotations
import asyncio
import random
import spade

from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from modules.base import GameModule
from playerAgent import Player
from network.message import PhishingMessage

# FSM States
STATE_SEND   = "SEND"
STATE_RESULT = "RESULT"
STATE_DONE   = "DONE"

# Difficulty settings — (num_messages, phishing_probability, max_victims)
DIFFICULTY = {
    "easy":   (5,  0.4, 3),
    "medium": (8,  0.6, 2),
    "hard":   (12, 0.75, 1),
}


# ── Phishing Agent (SPADE) ────────────────────────────────────────────

class PhishingAgent(Agent):
    """
    Generates phishing and legitimate messages probabilistically
    and stores them for the game module to read.
    """

    def __init__(self, jid: str, password: str, count: int, phish_prob: float):
        super().__init__(jid, password)
        self.count      = count
        self.phish_prob = phish_prob
        self.messages: list[PhishingMessage] = []
        self.ready      = asyncio.Event()

    class GenerateBehaviour(State):
        async def run(self):
            agent: PhishingAgent = self.agent
            loop = asyncio.get_event_loop()

            # Offload generation to executor (keeps event loop free)
            def _generate():
                return [
                    PhishingMessage.generate(agent.phish_prob)
                    for _ in range(agent.count)
                ]

            agent.messages = await loop.run_in_executor(None, _generate)
            agent.ready.set()
            self.set_next_state(STATE_DONE)

    class DoneState(State):
        async def run(self):
            await self.agent.stop()

    async def setup(self):
        fsm = FSMBehaviour()
        fsm.add_state(name=STATE_SEND, state=self.GenerateBehaviour(), initial=True)
        fsm.add_state(name=STATE_DONE, state=self.DoneState())
        fsm.add_transition(source=STATE_SEND, dest=STATE_DONE)
        self.add_behaviour(fsm)


# ── Phishing Module ───────────────────────────────────────────────────

class PhishingModule(GameModule):
    name        = "Phishing Attack"
    description = "Identify phishing emails before victims click them."

    PHISHING_JID  = "phisher@localhost"
    PHISHING_PASS = "admin"

    def __init__(self, player: Player):
        super().__init__(player)

    async def run(self) -> int:
        difficulty = self._get_difficulty()
        count, phish_prob, max_victims = DIFFICULTY[difficulty]

        # ── Launch PhishingAgent to generate messages ──────────────────
        agent = PhishingAgent(
            self.PHISHING_JID,
            self.PHISHING_PASS,
            count=count,
            phish_prob=phish_prob,
        )
        await agent.start(auto_register=True)
        await agent.ready.wait()          # block until messages are generated
        messages = agent.messages
        await agent.stop()

        # ── Game loop ──────────────────────────────────────────────────
        print(f"\n=== {self.name} === [{difficulty.upper()}]")
        print(f"Review {count} messages. Max victims allowed: {max_victims}\n")

        earned  = 0
        victims = 0

        for i, msg in enumerate(messages, start=1):
            print(f"\n--- Message {i}/{count} ---")
            msg.display()

            flag = input("\nIs this phishing? (Y/N): ").strip().upper()

            if msg.is_phishing and flag == "Y":
                pts = 150
                self.player.addPoints(pts)
                earned += pts
                print(f"[+] Correct! Phishing caught. +{pts} pts | Total: {self.player.getPoints()}")

            elif not msg.is_phishing and flag == "Y":
                pts = 75
                self.player.addPoints(-pts)
                earned -= pts
                print(f"[-] False positive! Legitimate email flagged. -{pts} pts | Total: {self.player.getPoints()}")

            elif msg.is_phishing and flag == "N":
                victims += 1
                print(f"[!] Phishing missed! A victim clicked. ({victims}/{max_victims} victims)")
                if victims >= max_victims:
                    print("\n[!!] Too many victims clicked. Round over!")
                    break

            else:
                print(f"[✓] Correct — legitimate email ignored.")

        print(f"\n[+] Phishing round complete. Points earned: {earned} | Total: {self.player.getPoints()}")
        return earned

    # ── Helpers ───────────────────────────────────────────────────────

    def _get_difficulty(self) -> str:
        print("\nSelect difficulty:")
        for i, key in enumerate(DIFFICULTY, start=1):
            count, prob, victims = DIFFICULTY[key]
            print(f"  {i}. {key.capitalize()} — {count} messages, {int(prob*100)}% phishing, {victims} victim(s) allowed")
        while True:
            raw = input("Choice (1/2/3): ").strip()
            mapping = {"1": "easy", "2": "medium", "3": "hard"}
            if raw in mapping:
                return mapping[raw]
            print("Please enter 1, 2, or 3.")
