from discord.ext import commands
from discord import app_commands
import discord
import os
import sqlite3
import dotenv

from datetime import datetime, timezone, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
SQL_PATH = "/home/admin/zencord.sqlite3"
ENV_PATH = os.path.join(root_dir, ".env")
BG_PATH = os.path.join(root_dir, "profile-bg.png")
FONT = os.path.join(root_dir, "zzz.ttf")

conn = sqlite3.connect(SQL_PATH)
cursor = conn.cursor()

dotenv.load_dotenv(ENV_PATH)  # ENV_PATH değişkenini doğrudan kullandık


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily", description="Collect your dailies.")
    async def daily(self, i: discord.Interaction):

        await i.response.defer(thinking=True)

        # Check if user has an account
        cursor.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (i.user.id,))

        if cursor.fetchone() is None:
            await i.followup.send(
                f"<:avatar:1536781562677563534> {i.user.mention} doesn't have a Proxy account yet."
            )
            return

        cursor.execute("SELECT updated_at FROM users WHERE user_id = ?", (i.user.id,))
        last_collected = cursor.fetchone()[0]

        date_currently = datetime.now(timezone.utc)

        date_formatted = datetime.fromisoformat(last_collected)

        difference = date_currently - date_formatted

        if difference.days < 1:
            next_reward = date_formatted + timedelta(days=1)
            await i.followup.send(
                f"<:exp:1536784801238089808> You already claimed your daily rewards.\nNext reward: <t:{int(next_reward.timestamp())}:F>"
            )
        else:
            # FİX 2: Kullanıcı ödülü aldığında veritabanındaki updated_at alanını da şu anki zamanla güncelliyoruz!
            now_iso = date_currently.isoformat()

            cursor.execute(
                "UPDATE users SET denny = denny + ?, polychrome = polychrome + ?, battery_charge = battery_charge + ?, updated_at = ? WHERE user_id = ?",
                (
                    int(os.getenv("DAILY_DENNIES", 0)),
                    int(os.getenv("DAILY_POLYS", 0)),
                    int(os.getenv("DAILY_BATTERY", 0)),
                    now_iso,  # Güncellenen yeni tarihi SQL'e gönderiyoruz
                    i.user.id,
                ),
            )
            conn.commit()

            # FİX 3: Çökmeyi önlemek için timedelta eklemesini metne çevirmeden önce (nesne halindeyken) yapıyoruz
            next_reward_time = date_currently + timedelta(days=1)

            await i.followup.send(
                f"<:exp:1536784801238089808> Daily Rewards claimed successfully:\n"
                f"<:denny:1536789469699506247> **{os.getenv('DAILY_DENNIES')}** Dennies\n"
                f"<:polychrome:1536789473923178610> **{os.getenv('DAILY_POLYS')}** Polychromes\n"
                f"<:battery:1536789471654322247> **{os.getenv('DAILY_BATTERY')}** Battery\n"  # Kapatılmamış markdown düzeltildi
                f"Next reward: <t:{int(next_reward_time.timestamp())}:F>"
            )


async def setup(bot):
    await bot.add_cog(Daily(bot))
