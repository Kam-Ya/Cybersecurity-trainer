import spade
import string
from userInput import policy_from_charset, prompt_password
from playerAgent import Player
from game.manager import GameManager
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))



async def main():
    # Build a player with a default policy
    policy = policy_from_charset(
        charset=string.ascii_lowercase + string.ascii_uppercase,
        max_len=5,
        min_len=1,
        hide_input=False,
        require_confirm=False,
    )
    player  = Player(policy=policy)
    manager = GameManager(player)
    await manager.loop()


if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=True)
