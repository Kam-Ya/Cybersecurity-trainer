from __future__ import annotations
import time
import spade
from modules.base import GameModule
from playerAgent import Player
from userInput import policy_from_charset, prompt_password
from cracker import TargetServiceAgent, BruteForcerAgent, TARGET_JID, TARGET_PASS, ATTACKER_JID, ATTACKER_PASS
import string


class BruteForceModule(GameModule):
    name        = "Brute Force"
    description = "Set a password and watch the attacker crack it. Earn points based on how long it holds."

    def __init__(self, player: Player):
        super().__init__(player)

    async def run(self) -> int:
        policy = policy_from_charset(
            charset=string.ascii_lowercase + string.ascii_uppercase,
            max_len=5,
            min_len=1,
            hide_input=True,
            require_confirm=False,
        )

        print(f"\n=== {self.name} ===")
        print(self.description)
        result = prompt_password(policy)
        if result is None:
            print("Cancelled.")
            return 0

        print(result)
        self.player.setPrev(result.password)

        start = time.time()

        async def _run():
            target   = TargetServiceAgent(TARGET_JID,   TARGET_PASS,  target_password=result.password)
            attacker = BruteForcerAgent(ATTACKER_JID, ATTACKER_PASS, policy=policy)
            await target.start(auto_register=True)
            await attacker.start(auto_register=True)
            await spade.wait_until_finished(attacker)
            await attacker.stop()
            await target.stop()

        await _run()

        elapsed_ms = int((time.time() - start) * 1000)
        earned     = self.player.applyResult(result, elapsed_ms)
        print(f"\n[+] Round complete. Time: {elapsed_ms}ms | Points earned: {int(earned)} | Total: {self.player.getPoints()}")
        return int(earned)
