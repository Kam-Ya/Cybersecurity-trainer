from __future__ import annotations

import asyncio
import string
from dataclasses import dataclass, field
from getpass import getpass
from typing import Optional, Sequence, Set, Tuple

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour


# ─────────────────────────────────────────────
#  Policy & Result dataclasses (unchanged API)
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class PasswordPolicy:
    """
    - allowed_chars: characters the user may use
    - max_len / min_len: length bounds
    - hide_input: mask CLI input via getpass
    - require_confirm: force double-entry
    """
    allowed_chars: Set[str]
    max_len: int
    min_len: int = 1
    hide_input: bool = True
    require_confirm: bool = True


@dataclass(frozen=True)
class PasswordResult:
    password: str
    length: int


# ─────────────────────────────────────────────
#  Pure helpers (no agent coupling)
# ─────────────────────────────────────────────

def policy_from_charset(
    charset: Sequence[str] | str,
    max_len: int,
    *,
    min_len: int = 1,
    hide_input: bool = True,
    require_confirm: bool = True,
) -> PasswordPolicy:
    return PasswordPolicy(
        allowed_chars=set(charset),
        max_len=max_len,
        min_len=min_len,
        hide_input=hide_input,
        require_confirm=require_confirm,
    )


def _read_line(prompt: str, hide: bool) -> str:
    return getpass(prompt) if hide else input(prompt)


def _validate_password(pw: str, policy: PasswordPolicy) -> Tuple[bool, str]:
    if not pw:
        return False, "Password cannot be empty."
    if len(pw) < policy.min_len:
        return False, f"Password too short (min {policy.min_len})."
    if len(pw) > policy.max_len:
        return False, f"Password too long (max {policy.max_len})."
    bad = sorted({ch for ch in pw if ch not in policy.allowed_chars})
    if bad:
        shown = "".join(bad[:12]) + ("…" if len(bad) > 12 else "")
        return False, f"Contains invalid characters: {shown}"
    return True, ""


def prompt_password(
    policy: PasswordPolicy,
    *,
    prompt1: str = "Enter password: ",
    prompt2: str = "Re-enter password: ",
    allow_cancel: bool = True,
    print_errors: bool = True,
) -> Optional[PasswordResult]:
    """
    Synchronous CLI password prompt. Validates against policy.
    Returns PasswordResult on success, None on Ctrl+C (if allow_cancel=True).
    Raises ValueError for invalid policy config.
    """
    if policy.min_len < 0 or policy.max_len < 0:
        raise ValueError("min_len and max_len must be non-negative.")
    if policy.min_len > policy.max_len:
        raise ValueError("min_len cannot exceed max_len.")
    if not policy.allowed_chars:
        raise ValueError("allowed_chars cannot be empty.")

    if allow_cancel:
        print("(Ctrl+C to cancel)\n")

    while True:
        try:
            pw1 = _read_line(prompt1, policy.hide_input)
            if policy.require_confirm:
                pw2 = _read_line(prompt2, policy.hide_input)
                if pw1 != pw2:
                    if print_errors:
                        print("Passwords did not match.\n")
                    continue

            ok, msg = _validate_password(pw1, policy)
            if not ok:
                if print_errors:
                    print(f"{msg}\n")
                continue

            return PasswordResult(password=pw1, length=len(pw1))

        except KeyboardInterrupt:
            if allow_cancel:
                print("\nCancelled.\n")
                return None
            raise


# ─────────────────────────────────────────────
#  SPADE agent integration
# ─────────────────────────────────────────────

class PasswordInputAgent(Agent):
    """
    Agent that collects a validated password from the CLI before
    entering its main behaviour loop.

    After startup, the result is stored at:
        agent.password_result  -> PasswordResult | None
    """

    def __init__(
        self,
        jid: str,
        password: str,
        policy: PasswordPolicy,
        *,
        prompt1: str = "Enter password: ",
        prompt2: str = "Re-enter password: ",
        allow_cancel: bool = True,
    ):
        super().__init__(jid, password)
        self.policy = policy
        self._prompt1 = prompt1
        self._prompt2 = prompt2
        self._allow_cancel = allow_cancel
        self.password_result: Optional[PasswordResult] = None

    # ------------------------------------------------------------------
    class CollectPasswordBehaviour(OneShotBehaviour):
        """
        Runs once on agent start.
        Offloads the blocking CLI prompt to a thread so the event loop
        isn't blocked, then stores the result on the agent.
        """

        async def run(self):
            agent: PasswordInputAgent = self.agent
            loop = asyncio.get_event_loop()

            # Run the blocking prompt in a thread executor
            result: Optional[PasswordResult] = await loop.run_in_executor(
                None,
                lambda: prompt_password(
                    agent.policy,
                    prompt1=agent._prompt1,
                    prompt2=agent._prompt2,
                    allow_cancel=agent._allow_cancel,
                ),
            )

            agent.password_result = result

            if result is None:
                print("[Agent] Password entry cancelled. Stopping.")
                await agent.stop()
            else:
                print(f"[Agent] Password accepted (length={result.length}).")
                # Hand off to whatever behaviour uses the password
                agent.add_behaviour(agent.build_main_behaviour())

    # ------------------------------------------------------------------

    def build_main_behaviour(self) -> spade.behaviour.CyclicBehaviour:
        """
        Override this in a subclass to return the behaviour that runs
        after a valid password is collected.

        Default: a no-op that immediately kills the agent.
        """
        class _Noop(spade.behaviour.OneShotBehaviour):
            async def run(self):
                print(f"[Agent] Password ready. Do work here.")
                await self.agent.stop()
        return _Noop()

    async def setup(self):
        print(f"[Agent] {self.jid} starting — will prompt for password.")
        self.add_behaviour(self.CollectPasswordBehaviour())


# ─────────────────────────────────────────────
#  Example subclass: verify a stored hash
# ─────────────────────────────────────────────

import hashlib

class AuthAgent(PasswordInputAgent):
    """
    Extends PasswordInputAgent to check the collected password
    against a stored SHA-256 hash.
    """

    def __init__(self, jid: str, jid_pass: str, policy: PasswordPolicy, stored_hash: str):
        super().__init__(jid, jid_pass, policy)
        self.stored_hash = stored_hash

    def build_main_behaviour(self):
        class _VerifyBehaviour(spade.behaviour.OneShotBehaviour):
            async def run(self):
                pw = self.agent.password_result.password
                digest = hashlib.sha256(pw.encode()).hexdigest()
                if digest == self.agent.stored_hash:
                    print("[AuthAgent] Authentication SUCCESSFUL.")
                else:
                    print("[AuthAgent] Authentication FAILED.")
                await self.agent.stop()
        return _VerifyBehaviour()


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

async def main():
    policy = policy_from_charset(
        charset=string.ascii_letters + string.digits + string.punctuation,
        max_len=64,
        min_len=8,
        hide_input=True,
        require_confirm=True,
    )

    # Pre-hash of "hunter2" for demo purposes
    stored = hashlib.sha256("hunter2".encode()).hexdigest()

    agent = AuthAgent("auth@localhost", "admin", policy, stored_hash=stored)
    await agent.start(auto_register=True)
    await spade.wait_until_finished(agent)
    print("Done.")


if __name__ == "__main__":
    spade.run(main())
