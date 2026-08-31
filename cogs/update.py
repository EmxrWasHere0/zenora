````python
import io
import os
import shutil
import zipfile
import asyncio
from pathlib import Path

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


class GitHubUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # =========================
        # GITHUB AYARLARI
        # =========================

        self.repo = "EmxrWasHere0/zenora"
        self.branch = "main"

        # GitHub reposunun tamamının bulunduğu klasör
        self.target_dir = Path(".")

        # Botu başlatan script
        self.start_script = Path("./start.sh")

    # =========================
    # UPDATE COMMAND
    # =========================

    @app_commands.command(
        name="update",
        description="Updates the bot [OWNER COMMAND]"
    )
    @app_commands.checks.is_owner()
    @app_commands.checks.cooldown(1, 30.0)
    async def update(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        zip_url = (
            f"https://github.com/{self.repo}/archive/"
            f"refs/heads/{self.branch}.zip"
        )

        # Geçici klasör
        temp_dir = Path(
            f".github_update_{os.getpid()}"
        )

        try:
            # =========================
            # GITHUB'DAN ZIP İNDİR
            # =========================

            async with aiohttp.ClientSession() as session:

                async with session.get(zip_url) as response:

                    if response.status != 200:
                        await interaction.followup.send(
                            f"❌ Could not fetch files.\n"
                            f"HTTP status: `{response.status}`",
                            ephemeral=True
                        )
                        return

                    data = await response.read()

            # =========================
            # TEMP KLASÖR
            # =========================

            if temp_dir.exists():
                shutil.rmtree(temp_dir)

            temp_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            # =========================
            # ZIP'İ AÇ
            # =========================

            with zipfile.ZipFile(
                io.BytesIO(data)
            ) as archive:

                members = archive.infolist()

                if not members:
                    await interaction.followup.send(
                        "❌ GitHub repo is empty.",
                        ephemeral=True
                    )
                    return

                # GitHub ZIP'leri genellikle:
                #
                # Repo-main/
                # ├── bot.py
                # ├── cogs/
                # └── ...
                #
                root_folder = members[0].filename.split("/")[0]

                for member in members:

                    member_path = Path(member.filename)

                    try:
                        relative_path = (
                            member_path.relative_to(
                                root_folder
                            )
                        )

                    except ValueError:
                        continue

                    destination = (
                        temp_dir / relative_path
                    )

                    # Path traversal protection
                    try:
                        destination.resolve().relative_to(
                            temp_dir.resolve()
                        )
                    except ValueError:
                        continue

                    if member.is_dir():

                        destination.mkdir(
                            parents=True,
                            exist_ok=True
                        )

                    else:

                        destination.parent.mkdir(
                            parents=True,
                            exist_ok=True
                        )

                        with archive.open(member) as source:

                            with open(
                                destination,
                                "wb"
                            ) as target:

                                shutil.copyfileobj(
                                    source,
                                    target
                                )

            # =========================
            # GÜNCELLEME
            # =========================

            await interaction.edit_original_response(
                content="📦 Download completed, update in progress..."
            )

            # GitHub'dan gelen dosyaları
            # mevcut klasörün üzerine kopyala.
            #
            # .git, venv, cache gibi şeylere
            # dokunmuyoruz.

            ignored = {
                ".git",
                ".github",
                "__pycache__",
                ".venv",
                "venv"
            }

            for source in temp_dir.iterdir():

                if source.name in ignored:
                    continue

                destination = Path(".") / source.name

                if source.is_dir():

                    if destination.exists():
                        shutil.rmtree(destination)

                    shutil.copytree(
                        source,
                        destination
                    )

                else:

                    shutil.copy2(
                        source,
                        destination
                    )

            # =========================
            # TEMP TEMİZLE
            # =========================

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )

            # =========================
            # RESTART
            # =========================

            await interaction.edit_original_response(
                content=(
                    "✅ **Update completed!**\n"
                    f"📦 `{self.repo}`\n"
                    f"🌿 `{self.branch}`\n\n"
                    "🔄 Restarting..."
                )
            )

            # Discord mesajının gönderilmesi için
            # kısa süre bekle
            await asyncio.sleep(2)

            # start.sh'yi çalıştır
            #
            # start.sh:
            # exec proxychains python3 bot.py

            os.execv(
                str(self.start_script),
                [str(self.start_script)]
            )

        except Exception as error:

            # Temp klasörü temizle
            if temp_dir.exists():
                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )

            await interaction.edit_original_response(
                content=(
                    "❌ **Update failed!**\n\n"
                    f"```py\n"
                    f"{error}"
                    f"\n```"
                )
            )

    # =========================
    # ERROR HANDLER
    # =========================

    @update.error
    async def update_error(
        self,
        interaction: discord.Interaction,
        error
    ):

        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            await interaction.response.send_message(
                "❌ No permissions.",
                ephemeral=True
            )

        elif isinstance(
            error,
            app_commands.errors.CheckFailure
        ):
            await interaction.response.send_message(
                "❌ Owner-only command.",
                ephemeral=True
            )

        elif isinstance(
            error,
            app_commands.errors.CommandOnCooldown
        ):
            await interaction.response.send_message(
                f"⏳ Wait: "
                f"`{error.retry_after:.1f}` saniye.",
                ephemeral=True
            )

        else:
            print(
                f"[UPDATE ERROR] {repr(error)}"
            )


async def setup(bot):
    await bot.add_cog(
        GitHubUpdater(bot)
    )
````
