
from __future__ import annotations

from dataclasses import dataclass
from getpass import getpass
from typing import Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class PasswordPolicy:
    """
    Policy provided by the caller.

    - allowed_chars: the set of characters the user is allowed to use
    - max_len: maximum password length
    - min_len: minimum password length
    - hide_input: if True, use getpass so input isn't echoed in the CLI
    - require_confirm: if True, user must enter the same password twice
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


def _read_line(prompt: str, hide: bool) -> str:
    return getpass(prompt) if hide else input(prompt)


def _validate_password(pw: str, policy: PasswordPolicy) -> Tuple[bool, str]:
    if pw is None:
        return False, "Password cannot be empty."
    if len(pw) < policy.min_len:
        return False, f"Password too short (min {policy.min_len})."
    if len(pw) > policy.max_len:
        return False, f"Password too long (max {policy.max_len})."

    bad = sorted({ch for ch in pw if ch not in policy.allowed_chars})
    if bad:
        # show up to a few invalid characters to keep output readable
        shown = "".join(bad[:12])
        suffix = "…" if len(bad) > 12 else ""
        return False, f"Contains locked/invalid characters: {shown}{suffix}"

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
    Prompt user for a password in the CLI, validate against the caller-provided policy,
    and (optionally) require confirmation by entering it twice.

    Returns:
      - PasswordResult on success
      - None if user cancels (Ctrl+C) and allow_cancel=True

    Notes:
      - This function does NOT score passwords.
      - It does NOT implement timing-based anti-mashing; it relies on confirm-entry and validation only.
    """
    if policy.min_len < 0 or policy.max_len < 0:
        raise ValueError("min_len and max_len must be non-negative.")
    if policy.min_len == 0:
        # Allow empty only if you really want it; most modules shouldn't.
        pass
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


# Helper functions



def policy_from_charset(
    charset: Sequence[str] | str,
    max_len: int,
    *,
    min_len: int = 1,
    hide_input: bool = True,
    require_confirm: bool = True,
) -> PasswordPolicy:
    """
    Helper to build a PasswordPolicy from a string/sequence of allowed characters.
    """
    return PasswordPolicy(
        allowed_chars=set(charset),
        max_len=max_len,
        min_len=min_len,
        hide_input=hide_input,
        require_confirm=require_confirm,
    )