import os
from dotenv import load_dotenv
from mcrcon import MCRcon

load_dotenv()


def run_save_command():
    try:
        with MCRcon("127.0.0.1", os.getenv('RCON_PASSWD'), int(os.getenv('RCON_PORT'))) as mcr:
            try:
                res = mcr.command("Save")
                print(res)
            except:
                pass
    except ConnectionRefusedError:
        pass
        

def get_active_user_count():
    try:
        with MCRcon("127.0.0.1", os.getenv('RCON_PASSWD'), int(os.getenv('RCON_PORT'))) as mcr:
            try:
                res = mcr.command("ShowPlayers")
                return res.count("\n") - 1
            except:
                return 0
    except ConnectionRefusedError:
        return "取得不可(RCONが死んでる)"


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
    
