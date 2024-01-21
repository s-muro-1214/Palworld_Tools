import json
import os
import sys
from dotenv import load_dotenv
from urllib.request import Request, urlopen

load_dotenv()


def post_discord(message: str, webhook_url: str):
    headers = {
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot(Izuna) Python-urllib"
            }

    data = {"content": message}

    request = Request(
            webhook_url,
            data=json.dumps(data).encode(),
            headers=headers
            )

    with urlopen(request) as res:
        assert res.getcode() == 204


if __name__ == "__main__":
    args = sys.argv
    message = f"### PalWorld Dedicated Server Update \r * Version: {args[1]} -> {args[2]}"

    post_discord(message, os.getenv("DISCORD_WEBHOOK"))

