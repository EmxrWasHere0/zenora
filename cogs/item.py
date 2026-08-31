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
SQL_PATH = os.path.join(root_dir, "zencord.sqlite3")
ENV_PATH = os.path.join(root_dir, ".env")
BG_PATH = os.path.join(root_dir, "profile-bg.png")
FONT = os.path.join(root_dir, "zzz.ttf")

conn = sqlite3.connect(SQL_PATH)
cursor = conn.cursor()

dotenv.load_dotenv(".env")


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


async def setup(bot):
    await bot.add_cog(Item(bot))
