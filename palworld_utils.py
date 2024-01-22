import os
from dotenv import load_dotenv
from mcrcon import MCRcon

load_dotenv()


def get_active_user_count():
    with MCRcon("127.0.0.1", os.getenv('RCON_PASSWD'), int(os.getenv('RCON_PORT'))) as mcr:
        try:
            response = mcr.command("ShowPlayers")
            return response.count("\n") - 1
        except MCRcon.MCRconException as e:
            return 0


def broadcast_message(message: str):
    with MCRcon("127.0.0.1", os.getenv('RCON_PASSWD'), int(os.getenv('RCON_PORT'))) as mcr:
        try:
            mcr.command(f"Broadcast {message}")
        except MCRcon.MCRconException as e:
            pass
    

if __name__ == "__main__":
    print(get_active_user_count())
