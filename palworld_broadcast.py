import os
import sys
from dotenv import load_dotenv
from mcrcon import MCRcon

load_dotenv()


def broadcast_message(message: str):
    try:
        with MCRcon("127.0.0.1", os.getenv('RCON_PASSWD'), int(os.getenv('RCON_PORT'))) as mcr:
            try:
                res = mcr.command(f"Broadcast {message}")
                print(res)
            except:
                pass
    except ConnectionRefusedError:
        pass


if __name__ == "__main_":
    args = sys.argv
    broadcast_message(args[1])
