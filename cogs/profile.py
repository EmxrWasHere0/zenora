from discord import app_commands
import discord
from discord.ext import commands
import aiohttp

import sqlite3
from datetime import datetime
import os
import dotenv
from typing import List
from io import BytesIO
from datetime import datetime, timedelta, timezone

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
SQL_PATH = "~/zencord.sqlite3"
ENV_PATH = os.path.join(root_dir, ".env")
BG_PATH = os.path.join(root_dir, "profile-bg.png")
FONT = os.path.join(root_dir, "zzz.ttf")

conn = sqlite3.connect(SQL_PATH)
cursor = conn.cursor()

dotenv.load_dotenv(".env")

EMOJIS = {
    "Anby Demara": "<:anby:1523943689842458746>",
    "Anton Ivanov": "<:anton:1523943848085029016>",
    "Ben Bigger": "<:ben:1523944277426704385>",
    "Billy Kid": "<:billy:1523944417709522975>",
    "Corin Wickes": "<:corin:1523944555823632475>",
    "Lucy": "<:luciana:1523944697624662036>",
    "Nicole Demara": "<:nicole:1523944819884556379>",
    "Piper Wheel": "<:piper:1523944972338987140>",
    "Soukaku": "<:soukaku:1523945069533462669>",
    "Seth Lowell": "<:seth:1523945177222217838>",
    "Von Lycaon": "<:von:1523945819344994374>",
    "Soldier 11": "<:soldier:1523945821136093357>",
    "Rina": "<:rina:1523945822478274581>",
    "Nekomata": "<:nekomata:1523945824516706395>",
    "Koleda Belobog": "<:koleda:1523945826005549096>",
    "Grace Howard": "<:grace:1523945828065087508>",
    "S-Rank": "<:srank:1523946787675836608>",
    "A-Rank": "<:arank:1523946790796263464>",
    "B-Rank": "<:brank:1523950456043339788>",
    "RB-Rank": "<:rbrank:1523968596844478555>",
    "Materials": "<:materials:1536781556377722890>",
    "Inter-Knot": "<:interknot:1536781558143258664>",
    "Agents": "<:agents:1536781560651710466>",
    "Avatar": "<:avatar:1536781562677563534>",
    "Fairy": "<:fairy:1536781565156270250>",
    "50/50": "<:fiftyfifty:1536782287318949958>",
    "Win": "<:win:1536782289118167180>",
    "Tape": "<:tape:1523951287085961216>",
    "W-Engine": "<:wengine:1523943127377772574>",
    "yabi": "<a:yabi:1530238446788939806>",
    "Aria": "<:aria:1530801787899216062>",
    "Remielle Dan": "<:remielle:1530801820476375070>",
    "Evelyn Chevalier": "<:evelyn:1530801853674029136>",
    "Caesar King": "<:caesar:1530801909210943659>",
    "Tsukishiro Yanagi": "<:tsukishiro:1530801939577700362>",
    "Zhu Yuan": "<:zhu:1530801963523117246>",
    "EXP": "<:exp:1536784801238089808>",
    "NECF": "<:necf:1536789467212550264>",
    "Denny": "<:denny:1536789469699506247>",
    "Battery": "<:battery:1536789471654322247>",
    "Polychrome": "<:polychrome:1536789473923178610>",
    "Search": "<:search:1536791450585538610>",
    "Pulchra Fellini": "<:pulchra:1537342670307991562>",
}


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Auto-Complete method
    async def autocomplete(self, i: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:

        cursor.execute(
            "SELECT character_name FROM user_characters WHERE user_id = ?",
            (i.user.id,)
        )
        chars = cursor.fetchall()

        return [
            app_commands.Choice(name=row[0], value=row[0])
            for row in chars
            if current.lower() in row[0].lower()
        ][:25]

    profile = app_commands.Group(name="profile", description="Profile commands")

    @profile.command(
        name="proxy", description="View your or another proxy's Inter-Knot account."
    )
    @app_commands.describe(user = "Proxy you will sarch for.")
    async def proxy(self, i: discord.Interaction, user: discord.Member = None):

        await i.response.defer(thinking=True)

        if user == None:
            user = i.user

        # Check if user has an account
        cursor.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (user.id,))

        if cursor.fetchone() is None:
            await i.followup.send(
                f"{EMOJIS.get('Avatar')} {user.mention} doesn't have a Proxy account yet."
            )
            return

        # Agents Owned
        cursor.execute(
            "SELECT COUNT(*) FROM user_characters WHERE user_id = ?", (user.id,)
        )
        agents = cursor.fetchone()[0]

        # Inter-Knot Level
        cursor.execute(
            "SELECT inter_knot_level FROM users WHERE user_id = ?", (user.id,)
        )
        interknot_level = cursor.fetchone()[0]

        # Account Created At
        cursor.execute("SELECT created_at FROM users WHERE user_id = ?", (user.id,))
        acc_created = cursor.fetchone()[0]
        dt = datetime.fromisoformat(acc_created)
        unix_time = int(dt.timestamp())
        formatting = f"<t:{unix_time}:F>"

        # S-Ranks
        cursor.execute(
            "SELECT COUNT(*) from user_characters WHERE rarity = ? AND user_id = ?",
            (
                "S",
                user.id,
            ),
        )
        s_chars = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) from user_w_engines WHERE rarity = ? AND user_id = ?",
            (
                "S",
                user.id,
            ),
        )
        s_engs = cursor.fetchone()[0]

        s_ranks = s_chars + s_engs

        # A-Ranks
        cursor.execute(
            "SELECT COUNT(*) from user_characters WHERE rarity = ? AND user_id = ?",
            (
                "A",
                user.id,
            ),
        )
        a_chars = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) from user_w_engines WHERE rarity = ? AND user_id = ?",
            (
                "A",
                user.id,
            ),
        )
        a_engs = cursor.fetchone()[0]

        a_ranks = a_chars + a_engs

        # B-Ranks
        cursor.execute(
            "SELECT COUNT(*) from user_w_engines WHERE rarity = ? AND user_id = ?",
            (
                "B",
                user.id,
            ),
        )
        b_engs = cursor.fetchone()[0]

        # Materials
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
        materials = cursor.fetchone()

        # Signal Searches
        cursor.execute("SELECT * FROM signal_search WHERE user_id = ?", (user.id,))
        searches = cursor.fetchone()

        if searches[2] == 1:
            character_status = "Yes (Agents)"
        else:
            character_status = "No (Agents)"

        if searches[3] == 1:
            w_engine_status = "Yes (W-Engines)"
        else:
            w_engine_status = "No (W-Engines)"

        # Embed Definition
        e = discord.Embed(color=0x3498DB, title="Proxy Profile")

        # Proxy Section
        e.add_field(
            name=f"**{EMOJIS.get('Fairy')} Proxy**", value="\u200b", inline=False
        )
        e.add_field(
            name=f"{EMOJIS.get('Avatar')} Username", value=user.name, inline=True
        )
        e.add_field(
            name=f"{EMOJIS.get('Inter-Knot')} Inter-Knot Level",
            value=interknot_level,
            inline=True,
        )
        e.add_field(
            name=f"{EMOJIS.get('EXP')} Account Created At",
            value=formatting,
            inline=True,
        )

        # Characters Section
        e.add_field(
            name=f"**{EMOJIS.get('Agents')} Agents**", value="\u200b", inline=False
        )
        e.add_field(
            name=f"{EMOJIS.get('S-Rank')} S-Ranks Owned", value=s_ranks, inline=True
        )
        e.add_field(
            name=f"{EMOJIS.get('A-Rank')} A-Ranks Owned", value=a_ranks, inline=True
        )
        e.add_field(
            name=f"{EMOJIS.get('B-Rank')} B-Ranks Owned", value=b_engs, inline=True
        )

        # Materials Section (Using inline=True for pairs makes grid neat, but 5 items is uneven.
        # Changing inline=False for a cleaner list format is recommended here)
        e.add_field(
            name=f"**{EMOJIS.get('Materials')} Materials**",
            value="\u200b",
            inline=False,
        )
        e.add_field(
            name=f"{EMOJIS.get('Tape')} Encrypted Master Tapes",
            value=materials[1],
            inline=True,
        )
        e.add_field(
            name=f"{EMOJIS.get('Denny')} Dennies", value=materials[3], inline=True
        )
        e.add_field(
            name=f"{EMOJIS.get('Polychrome')} Polychromes",
            value=materials[4],
            inline=True,
        )
        e.add_field(
            name=f"{EMOJIS.get('NECF')} City Fund Level",
            value=materials[5],
            inline=True,
        )
        e.add_field(
            name=f"{EMOJIS.get('Battery')} Batteries", value=materials[6], inline=True
        )

        # Signal Search Section (Set to inline=False because values contain newlines \n)
        e.add_field(
            name=f"**{EMOJIS.get('Search')} Signal Search Index**",
            value="\u200b",
            inline=False,
        )
        e.add_field(
            name=f"{EMOJIS.get('50/50')} 50/50 Guarantees",
            value=f"{character_status}\n{w_engine_status}",
            inline=False,
        )
        e.add_field(
            name=f"{EMOJIS.get('Win')} Pity Status",
            value=f"{searches[4]} (Agents)\n{searches[5]} (W-Engines)",
            inline=False,
        )

        avatar_url = user.display_avatar.with_size(256).with_format("png").url
        e.set_thumbnail(url=avatar_url)

        await i.followup.send(embed=e)

    @profile.command(name="agent", description="View an agent of yours' information.")
    @app_commands.autocomplete(agent=autocomplete)
    async def agent(self, i:discord.Interaction, agent: str):

        await i.response.defer(thinking=True)

        cursor.execute("SELECT * FROM user_characters WHERE user_id = ? AND character_name = ?",(i.user.id, agent,))
        agent_info = cursor.fetchone()
        if agent_info is None:
            await i.followup.send("❌ This agent is not on your account.")
            return

        agent_name = agent_info[2]

        e = discord.Embed(title=f"{EMOJIS.get(agent_name)} Agent Info", color=discord.Color.blue())

        e.add_field(name=f"{EMOJIS.get('Agents')} Agent Name", value=agent_name)
        e.add_field(name=f"{EMOJIS.get('EXP')} Agent Level", value=agent_info[5])
        e.add_field(name=f"{EMOJIS.get('Search')} Obtained At", value=f"<t:{int(datetime.fromisoformat(agent_info[4]).timestamp())}:F>")
        e.add_field(name=f"{EMOJIS.get('NECF')} Mindscape", value=agent_info[3])
        e.add_field(name=f"{EMOJIS.get('W-Engine')} W-Engine", value=agent_info[6])

        await i.followup.send(embed=e)


async def setup(bot):
    await bot.add_cog(Profile(bot))
