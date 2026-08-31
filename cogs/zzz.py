# cogs/zzz.py

import asyncio
import aiohttp
import discord

from discord import app_commands
from discord.ext import commands


class ZZZData:
    BASE_URL = (
        "https://raw.githubusercontent.com/"
        "EnkaNetwork/API-docs/refs/heads/master/store/zzz/"
    )

    def __init__(self, session):
        self.session = session

        self.locs = {}
        self.avatars = {}
        self.weapons = {}
        self.equipment = {}
        self.pfps = {}

        self.loaded = False

    # --------------------------------------------------
    # JSON
    # --------------------------------------------------

    async def fetch_json(self, filename):
        url = self.BASE_URL + filename

        async with self.session.get(url) as response:
            text = await response.text()

            if response.status != 200:
                raise RuntimeError(
                    f"{filename}: HTTP {response.status}"
                )

            try:
                return await response.json(
                    content_type=None
                )
            except Exception as error:
                print(
                    f"[ZZZ] JSON ERROR: {filename}"
                )
                print(text[:300])

                raise RuntimeError(
                    f"{filename} JSON parse error: {error}"
                )

    async def load(self):
        print(
            "[ZZZ] Enka ZZZ store yükleniyor..."
        )

        # Önce localization
        self.locs = await self.fetch_json(
            "locs.json"
        )

        self.avatars = await self.fetch_json(
            "avatars.json"
        )

        self.weapons = await self.fetch_json(
            "weapons.json"
        )

        self.equipment = await self.fetch_json(
            "equipments.json"
        )

        self.pfps = await self.fetch_json(
            "pfps.json"
        )

        self.loaded = True

        print(
            "[ZZZ] Store başarıyla yüklendi."
        )

        print(
            f"[ZZZ] Localization: "
            f"{len(self.locs)}"
        )

        print(
            f"[ZZZ] Avatars: "
            f"{len(self.avatars)}"
        )

        print(
            f"[ZZZ] Weapons: "
            f"{len(self.weapons)}"
        )

        print(
            f"[ZZZ] Equipment: "
            f"{len(self.equipment)}"
        )

    # --------------------------------------------------
    # LOCALIZATION
    # --------------------------------------------------

    def localize(self, value):
        """
        Her türlü TextMapHash / localization
        değerini İngilizceye çevirmeye çalışır.
        """

        if value is None:
            return None

        # Zaten direkt string ise
        if isinstance(value, str):

            # Internal identifier ise localization
            # içinde karşılığı olabilir.
            result = self.locs.get(value)

            if result is not None:
                return self._english(result)

            return value

        # Sayısal hash
        key = str(value)

        result = self.locs.get(key)

        if result is None:
            return None

        return self._english(result)

    @staticmethod
    def _english(value):
        """
        locs.json içinden SADECE İngilizce değer seçilir.
        """

        if isinstance(value, str):
            return value

        if not isinstance(value, dict):
            return None

        # Enka localization formatlarında
        # İngilizce için olası anahtarlar.
        for key in (
            "en",
            "en-US",
            "EN",
            "English",
            "english"
        ):
            result = value.get(key)

            if isinstance(result, str):
                return result

        # Eğer nested yapı varsa
        for nested in value.values():

            if isinstance(nested, dict):

                result = ZZZData._english(
                    nested
                )

                if result:
                    return result

        return None

    # --------------------------------------------------
    # GENERIC LOCALIZED FIELD
    # --------------------------------------------------

    def localized_field(
        self,
        obj,
        *keys
    ):
        """
        Bir objeden TextMapHash benzeri alanı
        bulup locs.json üzerinden İngilizceye çevirir.
        """

        if not obj:
            return None

        for key in keys:

            value = obj.get(key)

            if value is None:
                continue

            localized = self.localize(
                value
            )

            if localized:
                return localized

        return None

    # --------------------------------------------------
    # AVATAR
    # --------------------------------------------------

    def get_avatar(self, avatar_id):
        return self.avatars.get(
            str(avatar_id)
        )

    def get_avatar_name(self, avatar_id):
        avatar = self.avatars.get(str(avatar_id))

        if not avatar:
            return f"Agent {avatar_id}"

        internal_name = avatar.get("Name")

        if not internal_name:
            return f"Agent {avatar_id}"

        # locs.json["en"]["Avatar_Female..."]
        english_names = self.locs.get("en", {})

        name = english_names.get(internal_name)

        if name:
            return name

        # Bulunamazsa debug için internal adı göster
        print(
            f"[ZZZ] Localization bulunamadı: "
            f"{internal_name}"
        )

        return internal_name

    def get_avatar_icon(self, avatar_id):

        avatar = self.get_avatar(
            avatar_id
        )

        if not avatar:
            return None

        for key in (
            "IconPath",
            "iconPath",
            "Icon",
            "icon",
            "AvatarIcon",
            "avatarIcon"
        ):

            icon = avatar.get(key)

            if icon:
                return self.normalize_icon(
                    icon
                )

        return None

    # --------------------------------------------------
    # WEAPON
    # --------------------------------------------------

    def get_weapon(self, weapon_id):

        if weapon_id is None:
            return None

        return self.weapons.get(
            str(weapon_id)
        )

    def get_weapon_name(self, weapon_id):
        weapon_id = str(weapon_id)

        weapon = self.weapons.get(weapon_id)

        if not weapon:
            print(
                f"[ZZZ] Weapon ID bulunamadı: {weapon_id}"
            )
            return f"W-Engine {weapon_id}"

        print(
            f"[ZZZ] Weapon data [{weapon_id}]: "
            f"{weapon}"
        )

        localization_key = weapon.get("ItemName")

        print(
            f"[ZZZ] Weapon localization key: "
            f"{localization_key}"
        )

        if not localization_key:
            return f"W-Engine {weapon_id}"

        english = self.locs.get("en")

        if not isinstance(english, dict):
            print(
                "[ZZZ] locs.json içinde 'en' bulunamadı!"
            )
            return localization_key

        weapon_name = english.get(
            localization_key
        )

        print(
            f"[ZZZ] Localization result: "
            f"{weapon_name}"
        )

        if weapon_name:
            return weapon_name

        print(
            f"[ZZZ] locs.json key bulunamadı: "
            f"{localization_key}"
        )

        return localization_key

    def get_weapon_icon(self, weapon_id):

        weapon = self.get_weapon(
            weapon_id
        )

        if not weapon:
            return None

        for key in (
            "IconPath",
            "iconPath",
            "Icon",
            "icon"
        ):

            icon = weapon.get(key)

            if icon:
                return self.normalize_icon(
                    icon
                )

        return None

    # --------------------------------------------------
    # EQUIPMENT
    # --------------------------------------------------

    def get_equipment(self, equipment_id):

        if equipment_id is None:
            return None

        return self.equipment.get(
            str(equipment_id)
        )

    def get_equipment_name(
        self,
        equipment_id
    ):

        equipment = self.get_equipment(
            equipment_id
        )

        if not equipment:
            return f"Drive Disc {equipment_id}"

        name = self.localized_field(
            equipment,

            "NameTextMapHash",
            "nameTextMapHash",

            "DisplayNameTextMapHash",
            "displayNameTextMapHash",

            "EquipmentNameTextMapHash",
            "equipmentNameTextMapHash"
        )

        if name:
            return name

        return (
            f"Drive Disc "
            f"{equipment_id}"
        )

    # --------------------------------------------------
    # ICON
    # --------------------------------------------------

    @staticmethod
    def normalize_icon(icon):

        if not icon:
            return None

        if icon.startswith("http"):
            return icon

        icon = icon.lstrip("/")

        if icon.startswith("ui/"):
            icon = icon[3:]

        return (
            "https://enka.network/ui/"
            + icon
        )

    def get_avatar_id(self, avatar):

        table = self.pfps.get(
            str(avatar)
        )
        return table

    def get_avatar_link(self, avatar_id):

        connector = self.get_avatar_id(avatar_id)

        link = connector.get("Icon")

        return "https://enka.network" + link

class ZZZCog(commands.Cog):

    API_URL = (
        "https://enka.network/api/zzz/uid/{}"
    )

    def __init__(self, bot):

        self.bot = bot

        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent":
                    "ZZZDiscordBot/2.0"
            },
            timeout=aiohttp.ClientTimeout(
                total=15
            )
        )

        self.data = ZZZData(
            self.session
        )

    # --------------------------------------------------
    # /ZZZ
    # --------------------------------------------------

    @app_commands.command(
        name="zzz",
        description=(
            "View your Zenless Zone Zero profile - data provided by Enka.Network"
        )
    )
    @app_commands.describe(
        uid="Zenless Zone Zero UID"
    )
    async def zzz(
        self,
        interaction: discord.Interaction,
        uid: str
    ):

        uid = uid.strip()

        if not uid.isdigit():

            await interaction.response.send_message(
                "❌ UID must be numeric.",
                ephemeral=True
            )

            return

        if not 5 <= len(uid) <= 12:

            await interaction.response.send_message(
                "❌ Invalid UID.",
                ephemeral=True
            )

            return

        await interaction.response.defer()

        if not self.data.loaded:

            await interaction.followup.send(
                "❌ ZZZ data could not be loaded."
            )

            return

        # --------------------------------------------------
        # API
        # --------------------------------------------------

        try:

            async with self.session.get(
                self.API_URL.format(uid)
            ) as response:

                if response.status == 404:

                    await interaction.followup.send(
                        f"❌ Couldn't find `{uid}`."
                    )

                    return

                if response.status == 429:

                    await interaction.followup.send(
                        "⏳ Rate limited by Enka.Network."
                    )

                    return

                if response.status != 200:

                    await interaction.followup.send(
                        f"❌ Enka API error: "
                        f"`{response.status}`"
                    )

                    return

                data = await response.json(
                    content_type=None
                )

        except asyncio.TimeoutError:

            await interaction.followup.send(
                "⏱️ Enka API timeout."
            )

            return

        except aiohttp.ClientError as error:

            print(
                f"[ZZZ HTTP ERROR] {error}"
            )

            await interaction.followup.send(
                "❌ Couldn't connect to Enka API."
            )

            return

        # --------------------------------------------------
        # PLAYER
        # --------------------------------------------------

        player = data.get(
            "PlayerInfo"
        ) or {}

        social = player.get(
            "SocialDetail"
        ) or {}

        profile = social.get(
            "ProfileDetail"
        ) or {}

        signature = social.get(
            "Desc"
        )

        nickname = profile.get(
            "Nickname",
            "Unknown"
        )

        player_uid = profile.get(
            "Uid",
            uid
        )

        level = profile.get(
            "Level",
            "?"
        )

        region = data.get(
            "region",
            "?"
        )

        pfp = profile.get(
            "ProfileId",
            "?"
        )

        # --------------------------------------------------
        # EMBED
        # --------------------------------------------------

        embed = discord.Embed(
            title=f"<:zenless:1542156216611119157> {nickname}",
            description=(
                "Zenless Zone Zero Profile"
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="<:avatar:1536781562677563534> Player",
            value=(
                f"**Nickname:** `{nickname}`\n"
                f"**UID:** `{player_uid}`\n"
                f"*{signature}*"
            ),
            inline=False
        )

        embed.add_field(
            name="<:interknot:1536781558143258664> Account",
            value=(
                f"**Inter-Knot:** `{level}`\n"
                f"**Region:** `{region}`"
            ),
            inline=False
        )

        # --------------------------------------------------
        # CHARACTERS
        # --------------------------------------------------

        showcase = player.get(
            "ShowcaseDetail"
        ) or {}

        avatars = showcase.get(
            "AvatarList"
        ) or []

        if not avatars:

            embed.add_field(
                name="<:fairy:1536781565156270250> Showcase",
                value=(
                    "Couldn't find any "
                    "showcase."
                ),
                inline=False
            )

        else:

            for index, character in enumerate(
                avatars[:10]
            ):

                char_id = character.get(
                    "Id"
                )

                name = (
                    self.data.get_avatar_name(
                        char_id
                    )
                )

                level = character.get(
                    "Level",
                    "?"
                )

                mindscape = character.get(
                    "TalentLevel",
                    0
                )

                core = character.get(
                    "CoreSkillEnhancement",
                    0
                )

                if (
                    isinstance(core, int)
                    and 1 <= core <= 6
                ):
                    core = chr(
                        ord("A") + core - 1
                    )

                # ------------------------------
                # SKILLS
                # ------------------------------

                skills = character.get(
                    "SkillLevelList"
                ) or []

                skill_names = {
                    0: "Basic",
                    1: "Special",
                    2: "Dash",
                    3: "Ultimate",
                    5: "Core",
                    6: "Assist"
                }

                skill_lines = []

                if isinstance(
                    skills,
                    list
                ):

                    for skill_index, skill in enumerate(
                        skills
                    ):

                        if not isinstance(
                            skill,
                            dict
                        ):
                            continue

                        skill_level = skill.get(
                            "Level",
                            0
                        )

                        skill_name = (
                            skill_names.get(
                                skill_index,
                                f"Skill {skill_index}"
                            )
                        )

                        skill_lines.append(
                            f"{skill_name}: "
                            f"`{skill_level}`"
                        )

                skill_text = (
                    " • ".join(
                        skill_lines
                    )
                    if skill_lines
                    else "?"
                )

                # ------------------------------
                # W-ENGINE
                # ------------------------------

                weapon = character.get(
                    "Weapon"
                ) or {}

                weapon_id = weapon.get(
                    "Id"
                )

                weapon_name = (
                    self.data.get_weapon_name(
                        weapon_id
                    )
                    if weapon_id
                    else "None"
                )

                weapon_level = weapon.get(
                    "Level",
                    "?"
                )

                weapon_phase = weapon.get(
                    "UpgradeLevel",
                    0
                )

                # ------------------------------
                # CHARACTER
                # ------------------------------

                value = (
                    f"**Lv. `{level}`**\n"
                    f"Mindscape: `M{mindscape}` • "
                    f"Core: `{core}`\n\n"

                    f"<:core:1542155683946958858> **Skills**\n"
                    f"{skill_text}\n\n"

                    f"<:wengine:1523943127377772574> **{weapon_name}**\n"
                    f"Lv. `{weapon_level}` • "
                    f"Phase `{weapon_phase}`"
                )

                embed.add_field(
                    name=f"<:agents:1536781560651710466> {name}",
                    value=value[:1024],
                    inline=True
                )

                user_pfp = self.data.get_avatar_link(pfp)
                print(user_pfp)
                embed.set_thumbnail(url=user_pfp)

        # --------------------------------------------------
        # FOOTER
        # --------------------------------------------------

        ttl = data.get("ttl")

        if ttl is not None:

            embed.set_footer(
                text=(
                    "Data provided by Enka.Network • "
                    f"Cache TTL: {ttl}s"
                )
            )

        else:

            embed.set_footer(
                text="Data provided by Enka.Network"
            )

        await interaction.followup.send(
            embed=embed
        )

    # --------------------------------------------------
    # CLEANUP
    # --------------------------------------------------

    def cog_unload(self):
        asyncio.create_task(
            self.session.close()
        )


async def setup(bot):
    cog = ZZZCog(bot)

    try:
        await cog.data.load()

    except Exception as error:

        print(
            f"[ZZZ] Store yüklenemedi: "
            f"{type(error).__name__}: {error}"
        )

    await bot.add_cog(cog)
