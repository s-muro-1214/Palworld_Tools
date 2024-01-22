import os
from dotenv import load_dotenv
from mcrcon import MCRcon

load_dotenv()


def get_active_user_count():
    with MCRcon("127.0.0.1", os.getenv('RCON_PASSWD'), int(os.getenv('RCON_PORT'))) as mcr:
        try:
            res = mcr.command("ShowPlayers")
            return res.count("\n") - 1
        except MCRcon.MCRconException as e:
            return 0


def broadcast_message(message: str):
    with MCRcon("127.0.0.1", os.getenv('RCON_PASSWD'), int(os.getenv('RCON_PORT'))) as mcr:
        try:
            res = mcr.command(f"Broadcast {message}")
            print(res)
        except MCRcon.MCRconException as e:
            pass
    

if __name__ == "__main__":
    broadcast_message("test_message")
