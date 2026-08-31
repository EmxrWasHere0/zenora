from discord.ext import commands
import discord
from discord import app_commands
import dotenv
import os
import platform
import subprocess
import sqlite3

conn = sqlite3.connect("/home/admin/zencord.sqlite3")
cursor = conn.cursor()

dotenv.load_dotenv(".env")

VERSION = "0.2.60b"
CODENAME = "beckford"
STATE = "RELEASE"

dotenv.load_dotenv(".env")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="prettylongassprefix", intents=intents)


@bot.event
async def setup_hook():
    print("Loading Extensions...")
    await bot.load_extension("cogs.signal")
    await bot.load_extension("cogs.start")
    await bot.load_extension("cogs.profile")
    await bot.load_extension("cogs.daily")
    await bot.load_extension("cogs.item")
    await bot.load_extension("cogs.squad")
    await bot.load_extension("cogs.zzz")
    await bot.load_extension("cogs.update")
    print("Loaded.")

    print("Syncronizing slash commands")
    await bot.tree.sync()
    print("Syncronized")

    print("Ready")


@bot.tree.command(name="credits", description="Show credits.")
async def credits(i: discord.Interaction):
    await i.response.send_message(
        "## Zenora Credits:\n"
        "Developer: **EmxrDev**\n"
        "Belongs to: **Hyphen Software & AI/ML Development Team**\n"
        "Built on: **Python**\n"
        f"Build version: **{VERSION}.{CODENAME}.{STATE}**\n"
        "**--- System Information ---**\n"
        f"OS: **{platform.system()}**\n"
        f"Python Version: **{platform.python_version()}**\n"
        f"Python Compiler: **{platform.python_compiler()}**\n"
        f"CPU Architecture: **{platform.machine()}**\n"
        f"Hostname: **{platform.node()}**"
    )

@bot.tree.command(name="ping", description="Test bot's connection status")
async def ping(i: discord.Interaction):

    await i.response.defer(thinking=True)

    result = subprocess.check_output(
                ["ip", "route", "get", "8.8.8.8"],
                text=True
            )

    parts = result.split()

    intf = parts[parts.index("dev") + 1]

    if intf.startswith(("wlan", "wifi")):
        intf_type = "[Wi-Fi]"
    elif intf.startswith(("eth", "usb", "eno")):
        intf_type = "[Ethernet/USB Tethering]"
    elif intf.startswith(("rmnet", "ccmni")):
        intf_type = "[Mobile Data]"
    elif intf.startswith(("tun", "utun", "tap")):
        intf_type = "[Tunnel/VPN]"
    else:
        intf_type = "[Unknown]"

    await i.followup.send(
            "## Connectivity Status\n"
            f"Ping: **{round(bot.latency * 1000)}ms**\n"
            f"Connection Interface: **{intf}** {intf_type}"
            )

@bot.tree.command(name="sqlite", description="Execute an SQLite3 query [OWNER COMMAND]")
@app_commands.describe(query="The query that will be executed", variables="Variables to fill out '?'s on the query")
async def sqlite(i: discord.Interaction, query: str, variables: str):
    await i.response.defer(thinking=True)

    if i.user.id != int(os.getenv("OWNER_ID")):
        await i.followup.send("You cannot run this command unless you're the owner.")
        return

    define = variables.split(",")
    values = []

    for j in define:
        try:
            appendable = int(j)
        except ValueError:
            appendable = j

        values.append(appendable)

        try:
            cursor.execute(query, tuple(values))
        except Exception as e:
            await i.followup.send(f"An error occured while executing SQLite3 query:\n{e}")
            return

        try:
            result = cursor.fetchall()
            conn.commit()
        except sqlite3.Error as e:
            result = [e.sqlite_errorcode, e.sqlite_errorname]
            await i.followup.send(f"Your query ran successfully, but errors occured:\nError Code: **{result[0]}**\nError Name: **{result[1]}**")
            return

        await i.followup.send(f"Query successfully ran. Here is the output:\n```{result}```")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    custom_activity = discord.CustomActivity(
        name=f"v{VERSION} | /start"
    )
    await bot.change_presence(status=discord.Status.online, activity=custom_activity)


bot.run(os.getenv("BOT_TOKEN"))
