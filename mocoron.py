import asyncio
import discord
import os
import psutil
import subprocess
import palworld_utils
from discord import app_commands
from dotenv import load_dotenv


load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents = intents)
tree = app_commands.CommandTree(client)


# 5分ごとにサーバーの稼働状態を更新する
@client.event
async def on_ready():
    await tree.sync()

    while True:
        await client.change_presence(activity = discord.Activity(name = f"サーバーは{get_status()}だよ", type = discord.ActivityType.playing))
        await asyncio.sleep(300)


# help
@tree.command(name = "help", description = "コマンドリスト")
async def help(interaction: discord.Interaction):
    if not has_expect_role(interaction.user.roles):
        await interaction.response.send_message("実行に必要なロールが付与されていません")
        return

    embed = discord.Embed(title="ヘルプ", description="スラッシュコマンドの説明", color=0xff9300)
    embed.add_field(name="/help", value="これを表示する", inline=True)
    embed.add_field(name="/status", value="サーバーの稼働状態を取得する", inline=True)
    embed.add_field(name="/start", value="サーバーを起動する", inline=False)
    embed.add_field(name="/stop", value="サーバーを停止する。60秒後に停止(引数で変更可能)", inline=False)
    embed.add_field(name="/restart", value="サーバーを再起動する。60秒後に再起動(引数で変更可能)", inline=False)

    await interaction.response.send_message(embed=embed)


# ステータス確認
@tree.command(name = "status", description = "サーバーの状態確認")
async def status(interaction: discord.Interaction):
    if not has_expect_role(interaction.user.roles):
        await interaction.response.send_message("実行に必要なロールが付与されていません")
        return

    cpu = psutil.cpu_percent(interval=0.1, percpu=False)
    mem = psutil.virtual_memory()

    free = round(mem.free / 1000000000, 1)
    used = round(mem.used / 1000000000, 1)
    available = round(mem.available / 1000000000, 1)

    colorcode = 0x99ff66
    if not is_server_running():
        colorcode = 0xff6699

    embed = discord.Embed(title="サーバー稼働状態", description="各種リソースとパルワールドサーバーの状態", color=colorcode)
    embed.add_field(name="CPU[%]", value=cpu, inline=True)
    embed.add_field(name="Mem Free[GB]", value=free, inline=False)
    embed.add_field(name="Mem Used[GB]", value=used, inline=False)
    embed.add_field(name="Mem Available[GB]", value=available, inline=False)
    embed.add_field(name="パルワールドサーバー", value=get_status(), inline=True)
    embed.add_field(name="現在のログイン人数", value=palworld_utils.get_active_user_count(), inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=180.0)


# サーバー起動
@tree.command(name = "start", description = "サーバーを起動する")
async def start(interaction: discord.Interaction):
    if not has_expect_role(interaction.user.roles):
        await interaction.response.send_message(content="実行に必要なロールが付与されていません")
        return

    if is_server_running():
        await interaction.response.send_message(content="すでにサーバーが起動しています")
    else:
        try:
            await interaction.response.send_message(content="サーバーを起動します")
            subprocess.run("systemctl start palworld-dedicated".split(), check=True)
        except subprocess.CalledProcessError as e:
            await interaction.edit_original_response(content="サーバーの起動に失敗しました")


# サーバー停止
@tree.command(name = "stop", description = "サーバーを停止する")
@app_commands.rename(wait_sec = "待ち時間")
@app_commands.describe(wait_sec = "サーバー停止コマンド実行までの待機時間を[秒]単位で指定します")
async def start(interaction: discord.Interaction, wait_sec: int = 60):
    if not has_expect_role(interaction.user.roles):
        await interaction.response.send_message(content="実行に必要なロールが付与されていません")
        return

    if not is_server_running():
        await interaction.response.send_message(content="すでにサーバーが停止しています")
    else:
        try:
            await interaction.response.send_message(content=f"{wait_sec}秒後にサーバーを停止します")
            palworld_utils.broadcast_message(f"Stop_Server_After_{wait_sec}Sec")
            await asyncio.sleep(wait_sec)
            subprocess.run("systemctl stop palworld-dedicated".split(), check=True)
        except subprocess.CalledProcessError as e:
            await interaction.edit_original_response(content="サーバーの停止に失敗しました")


# サーバー再起動
@tree.command(name = "restart", description = "サーバーを再起動する")
@app_commands.rename(wait_sec = "待ち時間")
@app_commands.describe(wait_sec = "サーバー再起動コマンド実行までの待機時間を[秒]単位で指定します")
async def start(interaction: discord.Interaction, wait_sec: int = 60):
    if not has_expect_role(interaction.user.roles):
        await interaction.response.send_message(content="実行に必要なロールが付与されていません")
        return

    try:
        await interaction.response.send_message(content=f"{wait_sec}秒後にサーバーを再起動します")
        palworld_utils.broadcast_message(f"Restart_Server_After_{wait_sec}Sec")
        await asyncio.sleep(wait_sec)
        subprocess.run("systemctl restart palworld-dedicated".split(), check=True)
        await interaction.edit_original_response(content="サーバーを再起動しました")
    except subprocess.CalledProcessError as e:
        await interaction.edit_original_response(content="サーバーの再起動に失敗しました")


## 以下アドミン権限専用

@tree.command(name = "broadcast", description = "Broadcastメッセージを送信する")
@app_commands.describe(message = "送信するメッセージ内容。英語のみ、スペース不可")
async def start(interaction: discord.Interaction, message: str):
    if not is_admin(interaction.user.id):
        await interaction.response.send_message(content="実行に必要な権限がありません")
        return

    await interaction.response.defer(ephemeral=True, thinking=True)
    palworld_utils.broadcast_message(message)
    await interaction.followup.send(content=f"{message} を送信しました", ephemeral=True)


## 以下もろもろの関数

def has_expect_role(roles):
    for role in roles:
        if role.id == int(os.getenv('PAL_ROLE')):
            return True

    return False


def is_admin(id):
    return id == int(os.getenv('PAL_ADMIN_ID'))


def get_status():
    if is_server_running():
        return "稼働中"
    else:
        return "停止中"


def is_server_running():
    return subprocess.run("systemctl is-active palworld-dedicated".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0


if __name__ == "__main__":
    client.run(os.getenv('DISCORD_TOKEN'))


