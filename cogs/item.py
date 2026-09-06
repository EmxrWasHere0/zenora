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
    "Dialyn": "<:dialyn:1539671015624540220>",
    "Asaba Harumasa": "<:harumasa:1539671017423634502>",
    "Sigrid de L'Azur": "<:sigrid:1539671019042635936>",
    "Ukinami Yuzuha": "<:yuzuha:1539671020883935294>",
}


# Shop Buttons
class ShopItem(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="160 Polychromes",
        style=discord.ButtonStyle.blurple,
        emoji="<:polychrome:1536789473923178610>",
    )
    async def poly_button(self, i: discord.Interaction, button: discord.ui.Button):

        await i.response.defer()

        cursor.execute("SELECT polychrome FROM users WHERE user_id = ?", (i.user.id,))
        poly_amount = cursor.fetchone()[0]

        if poly_amount >= 160:
            cursor.execute(
                "UPDATE users SET polychrome = polychrome - 160, encrypted_master_tape = encrypted_master_tape + 1 WHERE user_id = ?",
                (i.user.id,),
            )
            conn.commit()

            await i.channel.send(
                "You purchased 1 <:tape:1523951287085961216> **Encrypted Master Tape** for 160 <:polychrome:1536789473923178610> **Polychromes**.",
                reference=i.message,
            )
        else:
            await i.channel.send(
                "You don't have enough <:polychrome:1536789473923178610> **Polychromes** to buy this.",
                reference=i.message,
            )

    @discord.ui.button(
        label="50K Dennies",
        style=discord.ButtonStyle.blurple,
        emoji="<:denny:1536789469699506247>",
    )
    async def denny_button(self, i: discord.Interaction, button: discord.ui.Button):

        await i.response.defer()

        cursor.execute("SELECT denny FROM users WHERE user_id = ?", (i.user.id,))
        denny_amount = cursor.fetchone()[0]

        if denny_amount >= 50000:
            cursor.execute(
                "UPDATE users SET denny = denny - 50000, encrypted_master_tape = encrypted_master_tape + 1 WHERE user_id = ?",
                (i.user.id,),
            )
            conn.commit()

            await i.channel.send(
                "You purchased 1 <:tape:1523951287085961216> **Encrypted Master Tape** for 50K <:denny:1536789469699506247> **Dennies**.",
                reference=i.message,
            )
        else:
            await i.channel.send(
                "You don't have enough <:denny:1536789469699506247> **Dennies** to buy this.",
                reference=i.message,
            )


class Item(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def autocomplete_characters(
        self, i: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:

        cursor.execute(
            "SELECT character_name FROM user_characters WHERE user_id = ?", (i.user.id,)
        )
        chars = cursor.fetchall()

        return [
            app_commands.Choice(name=row[0], value=row[0])
            for row in chars
            if current.lower() in row[0].lower()
        ][:25]

    async def autocomplete_engines(
        self, i: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:

        cursor.execute(
            "SELECT engine_name FROM user_w_engines WHERE user_id = ?", (i.user.id,)
        )
        chars = cursor.fetchall()

        return [
            app_commands.Choice(name=row[0], value=row[0])
            for row in chars
            if current.lower() in row[0].lower()
        ][:25]

    item = app_commands.Group(name="item", description="Item commands")

    @item.command(name="store", description="Have a look at the Store.")
    async def shop(self, i: discord.Interaction):
        await i.response.defer(thinking=True)

        # Check if user has an account
        cursor.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (i.user.id,))

        if cursor.fetchone() is None:
            await i.followup.send(
                f"<:avatar:1536781562677563534> {i.user.mention} doesn't have a Proxy account yet."
            )
            return

        e = discord.Embed(title="<:store:1537459401601065061> Store")

        e.add_field(
            name="<:tape:1523951287085961216> Encrypted Master Tape",
            value="Use of the options to buy it.",
        )

        await i.followup.send(embed=e, view=ShopItem())

    @item.command(name="equip", description="Equip a W-Engine for an agent")
    @app_commands.autocomplete(
        w_engine=autocomplete_engines, agent=autocomplete_characters
    )
    async def equip(i: discord.Interaction, w_engine: str, agent: str):
        await i.response.defer(thinking=True)

        cursor.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (i.user.id,))

        if cursor.fetchone() is None:
            await i.followup.send(
                f"<:avatar:1536781562677563534> {i.user.mention} doesn't have a Proxy account yet."
            )
            return

        cursor.execute(
            "UPDATE user_characters SET w_engine = ? WHERE user_id = ? AND character_name = ?;",
            (
                w_engine,
                i.user.id,
                agent,
            ),
        )
        conn.commit()

        await i.followup.send(
            f"Successfully set {EMOJIS.get(agent)} **{agent}**'s W-Engine as {EMOJIS.get("W-Engine")} **{w_engine}**"
        )


async def setup(bot):
    await bot.add_cog(Item(bot))
