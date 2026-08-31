from discord import app_commands
import discord
from discord.ext import commands

import sqlite3
from datetime import datetime, timezone
import os
import dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
SQL_PATH = "~/zencord.sqlite3"
ENV_PATH = os.path.join(root_dir, ".env")

dotenv.load_dotenv(ENV_PATH)
testers = list(int(x) for x in os.getenv("TESTER_IDS").split(","))

conn = sqlite3.connect(SQL_PATH)
cursor = conn.cursor()


class Start(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="start", description="Start your Zencord journey!")
    async def start(self, i: discord.Interaction):

        await i.response.defer(thinking=True)

        # Zaten kayıtlı mı?
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (i.user.id,))

        if cursor.fetchone():
            await i.followup.send("You already have a Inter-Knot account!")
            return

        now = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            INSERT INTO users (
                user_id,
                encrypted_master_tape,
                master_tape,
                denny,
                polychrome,
                city_fund,
                battery_charge,
                inter_knot_level,
                exp,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                i.user.id,
                25,
                5,
                1000,
                100,
                0,
                160,
                1,
                0,
                now,
                now,
            ),
        )

        cursor.execute(
            """
            INSERT INTO signal_search (
                user_id,
                char_win,
                weng_win,
                char_pity,
                weng_pity
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                i.user.id,
                1,
                1,
                90,
                90,
            ),
        )

        conn.commit()

        await i.followup.send(
            f"Inter-Knot account created successfully.\n"
            f"**Welcome to New Eridu, {i.user.mention}**"
        )


async def setup(bot):
    await bot.add_cog(Start(bot))
