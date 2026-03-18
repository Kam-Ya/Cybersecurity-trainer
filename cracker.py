from __future__ import annotations
import itertools
import string
import asyncio
import spade

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, FSMBehaviour, State
from spade.message import Message
from spade.template import Template
from userInput import PasswordPolicy

# === CONFIG ===
TARGET_JID    = "target@localhost"
TARGET_PASS   = "admin"
ATTACKER_JID  = "attacker@localhost"
ATTACKER_PASS = "admin"

# === FSM States ===
STATE_GUESS = "GUESS"
STATE_WAIT  = "WAIT"
STATE_DONE  = "DONE"


# === TARGET SERVICE AGENT ===
class TargetServiceAgent(Agent):

    def __init__(self, jid: str, password: str, target_password: str):
        super().__init__(jid, password)
        self.target_password = target_password

    class AuthBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("[Target] AuthBehaviour started. Password is hidden.")

        async def run(self):
            msg = await self.receive(timeout=5)
            if not msg:
                return
            if msg.get_metadata("type") != "password_guess":
                return

            guess = msg.body
            print(f"[Target] Received guess: {guess}")

            reply = Message(to=str(msg.sender))
            reply.set_metadata("performative", "inform")
            reply.set_metadata("type", "auth_result")
            reply.body = "success" if guess == self.agent.target_password else "fail"

            if reply.body == "success":
                print(f"[Target] Correct password found: {guess}")

            await self.send(reply)

    async def setup(self):
        print(f"[Target] Agent {self.jid} starting...")
        template = Template()
        template.set_metadata("type", "password_guess")
        self.add_behaviour(self.AuthBehaviour(), template)


# === BRUTE FORCER AGENT (FSM) ===
class BruteForcerAgent(Agent):

    def __init__(self, jid: str, password: str, policy: PasswordPolicy):
        super().__init__(jid, password)
        self.policy        = policy
        self.guesses       = None
        self.current_guess = None

    class GuessState(State):
        async def run(self):
            try:
                tup   = next(self.agent.guesses)
                guess = "".join(tup)
            except StopIteration:
                print("[Attacker] Exhausted keyspace without success.")
                self.set_next_state(STATE_DONE)
                return

            self.agent.current_guess = guess
            print(f"[Attacker] Trying: {guess}")

            msg = Message(to=TARGET_JID)
            msg.set_metadata("performative", "request")
            msg.set_metadata("type", "password_guess")
            msg.body = guess
            await self.send(msg)

            self.set_next_state(STATE_WAIT)

    class WaitState(State):
        async def run(self):
            reply = await self.receive(timeout=5)
            if reply and reply.get_metadata("type") == "auth_result":
                if reply.body == "success":
                    print(f"[Attacker] SUCCESS! Password is: {self.agent.current_guess}")
                    self.set_next_state(STATE_DONE)
                    return
            else:
                print("[Attacker] No reply or unexpected message; retrying.")

            await asyncio.sleep(0.1)
            self.set_next_state(STATE_GUESS)

    class DoneState(State):
        async def run(self):
            print("[Attacker] FSM complete. Stopping agent.")
            await self.agent.stop()

    async def setup(self):
        print(f"[Attacker] Agent {self.jid} starting...")

        charset      = sorted(self.policy.allowed_chars)
        self.guesses = itertools.product(charset, repeat=self.policy.max_len)

        fsm = FSMBehaviour()
        fsm.add_state(name=STATE_GUESS, state=self.GuessState(), initial=True)
        fsm.add_state(name=STATE_WAIT,  state=self.WaitState())
        fsm.add_state(name=STATE_DONE,  state=self.DoneState())

        fsm.add_transition(source=STATE_GUESS, dest=STATE_WAIT)
        fsm.add_transition(source=STATE_WAIT,  dest=STATE_GUESS)
        fsm.add_transition(source=STATE_WAIT,  dest=STATE_DONE)
        fsm.add_transition(source=STATE_GUESS, dest=STATE_DONE)

        template = Template()
        template.set_metadata("type", "auth_result")
        self.add_behaviour(fsm, template)


# === Standalone demo (no agents) ===
def brute_force_demo(target_password: str) -> None:
    """Synchronous brute force — no XMPP, just iterates and prints."""
    charset = string.ascii_lowercase + string.ascii_uppercase
    for tup in itertools.product(charset, repeat=len(target_password)):
        guess = "".join(tup)
        if guess == target_password:
            print(f"[Demo] Cracked: {guess}")
            return
    print("[Demo] Password not found in keyspace.")
