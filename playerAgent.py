from __future__ import annotations
from typing import List, Optional
from userInput import PasswordPolicy, PasswordResult


class Player:
    """
    Tracks a player's score and password history during a cracking session.

    - points:   cumulative score
    - mult:     score multiplier applied to time-based point calculation
    - prevPass: ordered history of previously submitted passwords
    - policy:   the PasswordPolicy assigned to this player's session
    """

    def __init__(
        self,
        policy: PasswordPolicy,
        points: int = 0,
        mult: float = 0.75,
    ):
        self.__points: int = points
        self.__mult: float = mult
        self.__prevPass: List[str] = []
        self.__policy: PasswordPolicy = policy

    # ── Password history ──────────────────────────────────────────────

    def setPrev(self, word: str) -> None:
        """Append a password attempt to history."""
        self.__prevPass.append(word)

    def getPrev(self) -> Optional[str]:
        """Return the most recent password attempt, or None if history is empty."""
        if not self.__prevPass:
            return None
        return self.__prevPass[-1]

    def getHistory(self) -> List[str]:
        """Return the full password attempt history."""
        return list(self.__prevPass)

    # ── Points ────────────────────────────────────────────────────────

    def getPoints(self) -> int:
        return self.__points

    def setPoints(self, points: int) -> None:
        self.__points = points

    def addPoints(self, points: int) -> None:
        """Add to existing points rather than overwriting."""
        self.__points += points

    # ── Multiplier ────────────────────────────────────────────────────

    def getMult(self) -> float:
        return self.__mult

    def setMult(self, mult: float) -> None:
        self.__mult = mult

    # ── Scoring ───────────────────────────────────────────────────────

    def calcPoints(self, time_ms: int) -> float:
        """
        Calculate points earned for a guess completed in time_ms milliseconds.
        Faster guesses earn more points; slower guesses earn fewer.
        """
        if time_ms <= 0:
            return 0.0
        return (1 / time_ms) * self.__mult * 10_000

    # ── Policy ────────────────────────────────────────────────────────

    def getPolicy(self) -> PasswordPolicy:
        return self.__policy

    def setPolicy(self, policy: PasswordPolicy) -> None:
        self.__policy = policy

    # ── Result integration ────────────────────────────────────────────

    def applyResult(self, result: PasswordResult, time_ms: int) -> float:
        """
        Convenience method: record a PasswordResult from userinput,
        add calculated points, and return the points earned this round.
        """
        self.setPrev(result.password)
        earned = self.calcPoints(time_ms)
        self.addPoints(int(earned))
        return earned

    # ── Display ───────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Player(points={self.__points}, mult={self.__mult}, "
            f"history={self.__prevPass})"
        )
