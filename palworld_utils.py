import os
import subprocess
from dotenv import load_dotenv

load_dotenv()


def get_active_user_count():
    port = os.getenv('RCON_PORT')
    passwd = os.getenv('RCON_PASSWD')
    output = subprocess.run(f"ARRCON -H 127.0.0.1 -P {port} -p {passwd} Showplayers".split(), capture_output=True, text=True).stdout

    return len(output.split('\n')) - 3

