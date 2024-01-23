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
        await asyncio.sleep(30)


# インタラクション処理
@client.event
async def on_interaction(interaction: discord.Interaction):
    try:
        if interaction.data["component_type"] == 2:
            await on_button_click(interaction)
    except KeyError:
        pass


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
@tree.command(name = "status", description = "サーバー状態の確認")
async def status(interaction: discord.Interaction):
    await get_server_status(interaction)


async def get_server_status(interaction: discord.Interaction):
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
    embed.add_field(name="CPU[%]", value=cpu, inline=False)
    embed.add_field(name="Mem Free[GB]", value=free, inline=True)
    embed.add_field(name="Mem Used[GB]", value=used, inline=True)
    embed.add_field(name="Mem Available[GB]", value=available, inline=True)
    embed.add_field(name="パルワールドサーバー", value=get_status(), inline=False)
    embed.add_field(name="現在のログイン人数", value=palworld_utils.get_active_user_count(), inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=180.0)


# ログインしているユーザ一覧の取得
@tree.command(name = "active_users", description = "現在のアクティブユーザー一覧を取得する")
async def active_users(interaction: discord.Interaction):
    await get_active_users(interaction)


async def get_active_users(interaction: discord.Interaction):
    if not has_expect_role(interaction.user.roles):
        await interaction.response.send_message(content="実行に必要なロールが付与されていません")
        return

    await interaction.response.send_message(content="未実装だよ", ephemeral=True)


# サーバー起動
@tree.command(name = "start", description = "サーバーを起動する")
async def start(interaction: discord.Interaction):
    await start_server(interaction)


async def start_server(interaction: discord.Interaction):
    if not has_expect_role(interaction.user.roles):
        await interaction.response.send_message(content="実行に必要なロールが付与されていません")
        return

    if is_server_running():
        await interaction.response.send_message(content="すでにサーバーが起動しています")
    else:
        try:
            await interaction.response.send_message(content="サーバーを起動します")
            subprocess.run("systemctl start palworld-dedicated".split(), check=True)
            await interaction.edit_original_response(content="サーバーを起動しました")
        except subprocess.CalledProcessError as e:
            await interaction.edit_original_response(content="サーバーの起動に失敗しました")


# サーバー停止
@tree.command(name = "stop", description = "サーバーを停止する")
@app_commands.rename(wait_sec = "待ち時間")
@app_commands.describe(wait_sec = "サーバー停止コマンド実行までの待機時間を[秒]単位で指定します")
async def stop(interaction: discord.Interaction, wait_sec: int = 60):
    await stop_server(interaction, wait_sec)


async def stop_server(interaction: discord.Interaction, wait_sec: int = 60):
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
            await interaction.edit_original_response(content="サーバーを停止しました")
        except subprocess.CalledProcessError as e:
            await interaction.edit_original_response(content="サーバーの停止に失敗しました")


# サーバー再起動
@tree.command(name = "restart", description = "サーバーを再起動する")
@app_commands.rename(wait_sec = "待ち時間")
@app_commands.describe(wait_sec = "サーバー再起動コマンド実行までの待機時間を[秒]単位で指定します")
async def restart(interaction: discord.Interaction, wait_sec: int = 60):
    await restart_server(interaction, wait_sec)


async def restart_server(interaction: discord.Interaction, wait_sec: int = 60):
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
async def broadcast(interaction: discord.Interaction, message: str):
    if not is_admin(interaction.user.id):
        await interaction.response.send_message(content="実行に必要な権限がありません")
        return

    await interaction.response.defer(ephemeral=True, thinking=True)
    palworld_utils.broadcast_message(message)
    await interaction.followup.send(content=f"{message} を送信しました", ephemeral=True)


@tree.command(name = "create_buttons", description = "コマンド実行用ボタンを作る")
async def create_buttons(interaction: discord.Interaction):
    if not is_admin(interaction.user.id):
        await interaction.response.send_message(content="実行に必要な権限がありません")
        return

    description = "`/status` 現在のサーバー稼働状況を確認する\n"\
            "`/active_users` 現在ログインしているユーザー名を表示する\n"\
            "`/start` サーバーを起動する\n"\
            "`/stop` サーバーを停止する(引数で停止までの待ち時間を指定可能)\n"\
            "`/restart` サーバーを再起動する(引数で再起動までの待ち時間を指定可能)"
    embed = discord.Embed(title="モコロンBotコマンド一覧", description=description, color=0x979c9f)

    button_status = discord.ui.Button(label="/status", style=discord.ButtonStyle.primary, custom_id="status")
    button_users = discord.ui.Button(label="/active_users", style=discord.ButtonStyle.primary, custom_id="active_users")
    button_start = discord.ui.Button(label="/start", style=discord.ButtonStyle.success, custom_id="start")
    button_stop = discord.ui.Button(label="/stop", style=discord.ButtonStyle.danger, custom_id="stop")
    button_restart = discord.ui.Button(label="/restart", style=discord.ButtonStyle.danger, custom_id="restart")

    view = discord.ui.View()
    view.add_item(button_status)
    view.add_item(button_users)
    view.add_item(button_start)
    view.add_item(button_stop)
    view.add_item(button_restart)

    await interaction.response.send_message(embed=embed, view=view)


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


async def on_button_click(interaction: discord.Interaction):
    custom_id = interaction.data["custom_id"]
    if custom_id == "status":
        await get_server_status(interaction)
    elif custom_id == "active_users":
        await get_active_users(interaction)
    elif custom_id == "start":
        await start_server(interaction)
    elif custom_id == "stop":
        await interaction.response.send_modal(Wait_Sec_Modal(stop_server))
    elif custom_id == "restart":
        await interaction.response.send_modal(Wait_Sec_Modal(restart_server))


class Wait_Sec_Modal(discord.ui.Modal):
    ans = discord.ui.TextInput(
            label="コマンド実行までの待機時間を入力",
            style=discord.TextStyle.short,
            default=60,
            required=True
    )

    def __init__(self, func):
        super().__init__(title="待機時間[sec]", timeout=None)
        self.func = func

    async def on_submit(self, interaction: discord.Interaction):
        wait_sec = self.ans.value
        try:
            value = int(wait_sec)
            await self.func(interaction, value)
        except ValueError:
            await interaction.response.send_message("")


## メイン

if __name__ == "__main__":
    client.run(os.getenv('DISCORD_TOKEN'))


