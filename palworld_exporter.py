import time
import os
from dotenv import load_dotenv
from mcrcon import MCRcon
from prometheus_client import start_http_server, Gauge


load_dotenv()


palworld_active_users_count = Gauge("palworld_active_users_count", "The number of active users in palworld server.")


def update_active_users_count(mcr):
    for _ in range(3):
        try:
            res = mcr.command("ShowPlayers")
            palworld_active_users_count.set(res.count("\n") - 1)
            break
        except:
            palworld_active_users_count.set(0)
            mcr.connect()


if __name__ == "__main__":
    start_http_server(int(os.getenv('EXPORTER_PORT')))

    with MCRcon("127.0.0.1", os.getenv('RCON_PASSWD'), int(os.getenv('RCON_PORT'))) as mcr:
        while True:
            update_active_users_count(mcr)
            time.sleep(10)

