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
import itertools

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
SQL_PATH = "/home/admin/zencord.sqlite3"
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

class Squad(commands.Cog):
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

    squad = app_commands.Group(name="squad", description="Squad commands")

    @squad.command(name="set", description="Set your squad.")
    @app_commands.autocomplete(agent1=autocomplete, agent2=autocomplete, agent3=autocomplete)
    async def set(self, i:discord.Interaction, agent1: str, agent2: str, agent3: str):
        await i.response.defer(thinking=True)
        if any(a == b for a, b in itertools.combinations([agent1, agent2, agent3], 2)):
            await i.followup.send("Your squad cannot have same agent more than once.")
            return

        cursor.execute("SELECT 1 FROM squads WHERE user_id = ? LIMIT 1;", (i.user.id,))

        if cursor.fetchone() is None:
            try:
                cursor.execute(
                    """INSERT INTO squads (
                        user_id, agent1, agent2, agent3
                    )
                    VALUES (
                        ?, ?, ?, ?
                    );""",
                (i.user.id, agent1, agent2, agent3,))

                conn.commit()

                await i.followup.send(
                    "Your squad has been created:\n"
                    f"1. {EMOJIS.get(agent1)} {agent1}\n"
                    f"2. {EMOJIS.get(agent2)} {agent2}\n"
                    f"3. {EMOJIS.get(agent3)} {agent3}\n"
                    )
            except Exception as e:
                await i.followup.send("Something went wrong: " + str(e))
        else:
            try:
                cursor.execute(
                    """
                    UPDATE squads SET
                    agent1 = ?,
                    agent2 = ?,
                    agent3 = ?
                    WHERE user_id = ?;
                    """,(agent1, agent2, agent3, i.user.id,))

                conn.commit()
                await i.followup.send(
                    "Your squad has been updated:\n"
                    f"1. {EMOJIS.get(agent1)} {agent1}\n"
                    f"2. {EMOJIS.get(agent2)} {agent2}\n"
                    f"3. {EMOJIS.get(agent3)} {agent3}\n"
                    )
            except Exception as e:
                await i.followup.send("Something went wrong: " + str(e))
    
    @squad.command(name="view", description="View your or another proxy's squad.")
    @app_commands.describe(proxy="The proxy you'll look for.")
    async def view(self, i: discord.Interaction, proxy: discord.Member = None):
        await i.response.defer(thinking=True)
        if proxy is None:
            proxy = i.user

        cursor.execute("SELECT 1 FROM squads WHERE user_id = ? LIMIT 1;", (proxy.id,))

        if cursor.fetchone() is None:
            await i.followup.send(EMOJIS.get("Avatar") + " This user does not have an Inter-Knot account yet.")
            return

        cursor.execute("SELECT * FROM squads WHERE user_id = ?;",(proxy.id,))
        results = cursor.fetchone()

        e = discord.Embed(title="Proxy Squad", color=discord.Color.blue())

        for j in results[2:5]:
            cursor.execute("SELECT * FROM user_characters WHERE character_name= ? AND user_id = ?;", (j, proxy.id))
            char_perks = cursor.fetchone()

            perks = f"{EMOJIS.get('EXP')} {char_perks[5]} | {EMOJIS.get('NECF')} {char_perks[3]} | {EMOJIS.get('W-Engine')} {char_perks[6]}"

            e.add_field(name=f"{EMOJIS.get(j)} **{j}**", value=perks, inline=False)

        e.set_thumbnail(url=proxy.display_avatar.with_size(256).with_format("png").url)
        await i.followup.send(embed=e)


async def setup(bot):
    await bot.add_cog(Squad(bot))
