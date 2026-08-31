import os
import json
import sqlite3
from datetime import datetime, timezone
import discord
from discord import app_commands
from discord.ext import commands
import random
import dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
JSON_PATH = os.path.join(root_dir, "signal.json")
SQL_PATH = os.path.join(root_dir, "zencord.sqlite3")
ENV_PATH = os.path.join(root_dir, ".env")

conn = sqlite3.connect(SQL_PATH)
cursor = conn.cursor()

dotenv.load_dotenv(ENV_PATH)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

banners = [item["banner_name"] for item in data]

STD_S_RANK_POOL = [
    "Nekomata",
    "Soldier 11",
    "Rina",
    "Koleda Belobog",
    "Von Lycaon",
    "Grace Howard",
    "Tsukishiro Yanagi",
    "Caesar King",
    "Zhu Yuan",
]

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


class SignalSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    signal = app_commands.Group(name="signal", description="Signal Search commands")

    @signal.command(name="list", description="List active banners")
    async def list_banners(self, i: discord.Interaction):
        await i.response.defer(thinking=True)

        embed = discord.Embed(
            title="Active Signal Search Banners", color=discord.Color.blue()
        )
        for banner_item in data:
            dt = datetime.fromisoformat(banner_item["ends_at"])
            unix_time = int(dt.timestamp())
            formatting = f"<t:{unix_time}:F>"
            embed.add_field(
                name=banner_item["banner_name"],
                value=(
                    f"**Special Character:** {banner_item['banner_character']}\n"
                    f"**Banner ends:** {formatting}"
                ),
                inline=False,
            )

        await i.followup.send(embed=embed)

    @signal.command(
        name="single",
        description="Do a single signal search in limited-time character channels.",
    )
    @app_commands.choices(
        channel=[app_commands.Choice(name=r, value=r) for r in banners]
    )
    async def search(self, i: discord.Interaction, channel: app_commands.Choice[str]):
        await i.response.defer(thinking=True)

        channel_value = channel.value

        # Banner'a ait karakter adını JSON'dan bul
        banner_character = None
        for item in data:
            if item["banner_name"] == channel_value:
                banner_character = item["banner_character"].split(",")
                break

        if banner_character is None:
            await i.followup.send("Banner not found. Please contact an admin.")
            return

        # Kullanıcı kaydını kontrol et
        cursor.execute(
            "SELECT encrypted_master_tape FROM users WHERE user_id=?", (i.user.id,)
        )
        result = cursor.fetchone()

        if result is None:
            await i.followup.send(
                "No registry found under your user ID. Please use `/start` to begin your journey!\n"
            )
            return

        amount = result[0]

        if amount <= 0:
            await i.followup.send("You don't have enough encrypted master tapes.")
            return

        # Tape düş
        new_amount = amount - 1
        cursor.execute(
            "UPDATE users SET encrypted_master_tape = ? WHERE user_id = ?",
            (new_amount, i.user.id),
        )
        conn.commit()

        # Signal search kaydını al
        # Sütunlar: id, user_id, char_win, weng_win, char_pity, weng_pity
        cursor.execute(
            "SELECT * FROM signal_search WHERE user_id = ?",
            (i.user.id,),
        )
        info = cursor.fetchone()

        if info is None:
            await i.followup.send(
                "No signal search record found for you. Please use `/start` first."
            )
            return

        # index: 0=id, 1=user_id, 2=char_win, 3=weng_win, 4=char_pity, 5=weng_pity
        _5050win = info[2] == 1  # char_win
        pity_count = info[4]  # char_pity

        # .env değerleri
        soft_pity = int(os.getenv("CHAR_SOFT_PITY"))
        hard_pity = int(os.getenv("S_RANK_CHARACTER_MAX_PITY"))
        no_pity_s_chance = int(os.getenv("CHAR_NO_PITY_S_RANK_CHANCE"))
        soft_pity_s_chance = int(os.getenv("CHAR_SOFT_PITY_S_RANK_CHANCE"))
        a_rank_chance = int(os.getenv("CHAR_A_RANK_CHANCE"))

        if pity_count <= 0:
            pity = "hard"
        elif pity_count <= soft_pity:
            pity = "soft"
        else:
            pity = "none"

        # --- Yardımcı fonksiyonlar ---
        def pull_s_rank():
            if _5050win:
                # Garantili: banner karakteri
                cursor.execute(
                    "SELECT * FROM characters WHERE name = ?", (random.choice(banner_character),)
                )
                row = cursor.fetchone()
                won = True
            else:
                # 50/50 coinflip
                if random.randint(1, 2) == 1:
                    # 5050 kazanıldı → banner karakteri
                    cursor.execute(
                        "SELECT * FROM characters WHERE name = ?", (random.choice(banner_character),)
                    )
                    row = cursor.fetchone()
                    won = True
                else:
                    # 5050 kaybedildi → standart havuz
                    std_pick = random.choice(STD_S_RANK_POOL)
                    cursor.execute(
                        "SELECT * FROM characters WHERE name = ?", (std_pick,)
                    )
                    row = cursor.fetchone()
                    won = False
            return row, True, won  # (result, is_char, won_5050)

        def pull_a_rank():
            if random.randint(1, 2) == 1:
                cursor.execute("SELECT * FROM w_engines WHERE rarity = ?", ("A",))
                rows = cursor.fetchall()
                return (random.choice(rows) if rows else None), False
            else:
                cursor.execute("SELECT * FROM characters WHERE rarity = ?", ("A",))
                rows = cursor.fetchall()
                return (random.choice(rows) if rows else None), True

        def pull_b_rank():
            cursor.execute("SELECT * FROM w_engines WHERE rarity = ?", ("B",))
            rows = cursor.fetchall()
            return (random.choice(rows) if rows else None), False

        # --- Çekim mantığı ---
        char_result = None
        is_char = False
        is_s_rank = False
        won_5050 = None

        chance = random.randint(1, 1000)

        if pity == "hard":
            char_result, is_char, won_5050 = pull_s_rank()
            is_s_rank = True

        elif pity == "soft":
            if chance <= soft_pity_s_chance:
                char_result, is_char, won_5050 = pull_s_rank()
                is_s_rank = True
            elif chance <= soft_pity_s_chance + a_rank_chance:
                char_result, is_char = pull_a_rank()
            else:
                char_result, is_char = pull_b_rank()

        else:  # none
            if chance <= no_pity_s_chance:
                char_result, is_char, won_5050 = pull_s_rank()
                is_s_rank = True
            elif chance <= no_pity_s_chance + a_rank_chance:
                char_result, is_char = pull_a_rank()
            else:
                char_result, is_char = pull_b_rank()

        if char_result is None:
            await i.followup.send(
                "Something went wrong while resolving your pull. Please contact an admin."
            )
            return

        if is_s_rank:
            new_pity = hard_pity
            new_char_win = 0 if won_5050 else 1
        else:
            new_pity = pity_count - 1
            new_char_win = info[2]

        cursor.execute(
            "UPDATE signal_search SET char_win = ?, char_pity = ? WHERE user_id = ?",
            (new_char_win, new_pity, i.user.id),
        )
        conn.commit()

        # --- Sonucu gönder ---
        icon = f"{EMOJIS.get(char_result[1]) if is_char else EMOJIS.get("W-Engine")}"
        if is_s_rank:
            rank = f"{EMOJIS.get("S-Rank")}"
        elif char_result[2] == "A":
            rank = f"{EMOJIS.get("A-Rank")}"
        else:
            rank = f"{EMOJIS.get("B-Rank")}"
        emoji = f"{rank} {icon}"

        await i.followup.send(
            f"Signal Search successful! Here's what you got:\n"
            f"# {emoji} {char_result[1]}"
        )

        if is_char:
            cursor.execute(
                "SELECT mindscape FROM user_characters WHERE user_id = ? AND character_name = ?",
                (i.user.id, char_result[1],)
            )
            validation = cursor.fetchone()
            if validation is None:
                cursor.execute(
                    """
                    INSERT INTO user_characters(
                        user_id,
                        character_name,
                        mindscape,
                        obtained_at,
                        char_level,
                        w_engine,
                        rarity
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        i.user.id,
                        char_result[1],
                        0,
                        datetime.now(timezone.utc).isoformat(),
                        1,
                        None,
                        "S" if is_s_rank else "A" if char_result[2] == "A" else "B",
                    ),
                )
            else:
                cursor.execute(
                    "SELECT mindscape FROM user_characters WHERE user_id = ? AND character_name = ?",
                    (
                        i.user.id,
                        char_result[1],
                    ),
                )
                old_mindscape = cursor.fetchone()[0]
                if old_mindscape == 6:
                    cursor.execute("UPDATE users SET encrypted_master_tape = encrypted_master_tape + ? WHERE user_id = ?",(3 if is_s_rank else 1 if char_result[2] == "A" else 0, i.user.id,))

                new_mindscape = min(validation[0] + 1, 6)  # zaten çektiğimiz için direkt kullan
                cursor.execute(
                    "UPDATE user_characters SET mindscape = ? WHERE user_id = ? AND character_name = ?",
                    (new_mindscape, i.user.id, char_result[1],)
                )
            conn.commit()
        else:
            cursor.execute(
                "SELECT refinement FROM user_w_engines WHERE user_id = ? AND engine_name = ?",
                (i.user.id, char_result[1],),
            )
            validation = cursor.fetchone()
            if validation is None:
                cursor.execute(
                    """
                    INSERT INTO user_w_engines(
                        user_id,
                        engine_name,
                        refinement,
                        obtained_at,
                        weng_level,
                        rarity
                    )
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        i.user.id,
                        char_result[1],
                        0,
                        datetime.now(timezone.utc).isoformat(),
                        1,
                        "S" if is_s_rank else "A" if char_result[2] == "A" else "B",
                    ),
                )
            else:
                new_refinement = min(validation[0] + 1, 5)  # direkt kullan
                cursor.execute(
                    "UPDATE user_w_engines SET refinement = ? WHERE user_id = ? AND engine_name = ?",
                    (new_refinement, i.user.id, char_result[1],)
                )
            conn.commit()

    @signal.command(
    name="multi",
    description="Do 10 signal searches at once in limited-time character channels.",
    )
    @app_commands.choices(
        channel=[app_commands.Choice(name=r, value=r) for r in banners]
    )
    async def search_multi(self, i: discord.Interaction, channel: app_commands.Choice[str]):
        await i.response.defer(thinking=True)

        channel_value = channel.value

        # Banner'a ait karakter adını JSON'dan bul
        banner_character = None
        for item in data:
            if item["banner_name"] == channel_value:
                banner_character = item["banner_character"].split(",")
                break

        if banner_character is None:
            await i.followup.send("Banner not found. Please contact an admin.")
            return

        # Signal search kaydını kontrol et (tape düşmeden önce!)
        cursor.execute(
            "SELECT * FROM signal_search WHERE user_id = ?",
            (i.user.id,),
        )
        info = cursor.fetchone()

        if info is None:
            await i.followup.send(
                "No signal search record found for you. Please use `/start` first."
            )
            return

        # Kullanıcı kaydını kontrol et
        cursor.execute(
            "SELECT encrypted_master_tape FROM users WHERE user_id=?", (i.user.id,)
        )
        result = cursor.fetchone()

        if result is None:
            await i.followup.send(
                "No registry found under your user ID. Please use `/start` to begin your journey!\n"
            )
            return

        amount = result[0]

        if amount < 10:
            await i.followup.send(
                f"You don't have enough encrypted master tapes. You need 10 but you have {amount}."
            )
            return

        # 10 tape düş
        new_amount = amount - 10
        cursor.execute(
            "UPDATE users SET encrypted_master_tape = ? WHERE user_id = ?",
            (new_amount, i.user.id),
        )
        conn.commit()

        # index: 0=id, 1=user_id, 2=char_win, 3=weng_win, 4=char_pity, 5=weng_pity
        _5050win = info[2] == 1
        pity_count = info[4]
        current_char_win = info[2]

        # .env değerleri
        soft_pity = int(os.getenv("CHAR_SOFT_PITY"))
        hard_pity = int(os.getenv("S_RANK_CHARACTER_MAX_PITY"))
        no_pity_s_chance = int(os.getenv("CHAR_NO_PITY_S_RANK_CHANCE"))
        soft_pity_s_chance = int(os.getenv("CHAR_SOFT_PITY_S_RANK_CHANCE"))
        a_rank_chance = int(os.getenv("CHAR_A_RANK_CHANCE"))

        # --- Yardımcı fonksiyonlar ---
        def pull_s_rank():
            nonlocal _5050win, current_char_win
            if _5050win:
                cursor.execute(
                    "SELECT * FROM characters WHERE name = ?", (random.choice(banner_character),)
                )
                row = cursor.fetchone()
                won = True
            else:
                if random.randint(1, 2) == 1:
                    cursor.execute(
                        "SELECT * FROM characters WHERE name = ?", (random.choice(banner_character),)
                    )
                    row = cursor.fetchone()
                    won = True
                else:
                    std_pick = random.choice(STD_S_RANK_POOL)
                    cursor.execute(
                        "SELECT * FROM characters WHERE name = ?", (std_pick,)
                    )
                    row = cursor.fetchone()
                    won = False

            # 5050 ve char_win güncelle
            if won:
                _5050win = False
                current_char_win = 0
            else:
                _5050win = True
                current_char_win = 1

            return row, True, won

        def pull_a_rank():
            if random.randint(1, 2) == 1:
                cursor.execute("SELECT * FROM w_engines WHERE rarity = ?", ("A",))
                rows = cursor.fetchall()
                return (random.choice(rows) if rows else None), False
            else:
                cursor.execute("SELECT * FROM characters WHERE rarity = ?", ("A",))
                rows = cursor.fetchall()
                return (random.choice(rows) if rows else None), True

        def pull_b_rank():
            cursor.execute("SELECT * FROM w_engines WHERE rarity = ?", ("B",))
            rows = cursor.fetchall()
            return (random.choice(rows) if rows else None), False

        # --- 10 çekim döngüsü ---
        results = []

        for pull_num in range(10):
            char_result = None
            is_char = False
            is_s_rank = False
            won_5050 = None

            # Pity kontrolü
            if pity_count <= 0:
                pity = "hard"
            elif pity_count <= soft_pity:
                pity = "soft"
            else:
                pity = "none"

            chance = random.randint(1, 1000)

            if pity == "hard":
                char_result, is_char, won_5050 = pull_s_rank()
                is_s_rank = True

            elif pity == "soft":
                if chance <= soft_pity_s_chance:
                    char_result, is_char, won_5050 = pull_s_rank()
                    is_s_rank = True
                elif chance <= soft_pity_s_chance + a_rank_chance:
                    char_result, is_char = pull_a_rank()
                else:
                    char_result, is_char = pull_b_rank()

            else:  # none
                if chance <= no_pity_s_chance:
                    char_result, is_char, won_5050 = pull_s_rank()
                    is_s_rank = True
                elif chance <= no_pity_s_chance + a_rank_chance:
                    char_result, is_char = pull_a_rank()
                else:
                    char_result, is_char = pull_b_rank()

            if char_result is None:
                results.append(("❌ Error", False, False))
                pity_count -= 1
                continue

            # Pity güncelle
            if is_s_rank:
                pity_count = hard_pity
            else:
                pity_count -= 1

            results.append((char_result, is_char, is_s_rank))

        # --- DB güncelle (tek seferde) ---
        cursor.execute(
            "UPDATE signal_search SET char_win = ?, char_pity = ? WHERE user_id = ?",
            (current_char_win, pity_count, i.user.id),
        )
        conn.commit()

        # --- Sonuçları formatla ---
        lines = []
        for idx, (pull_result, is_char, is_s_rank) in enumerate(results, 1):
            if pull_result == "❌ Error":
                lines.append(f"`{idx}.` ❌ Error")
                continue

            # İkon belirle
            if is_char:
                icon = EMOJIS.get(pull_result[1], "")
            else:
                icon = EMOJIS.get('W-Engine', "")

            # Rank belirle
            if is_s_rank:
                rank = EMOJIS.get('S-Rank', "")
            elif pull_result[2] == 'A':
                rank = EMOJIS.get('A-Rank', "")
            else:
                rank = EMOJIS.get('B-Rank', "")

            emoji = f"{rank} {icon}"
            name = pull_result[1]

            if is_s_rank:
                lines.append(f"`{idx}.` {emoji} **{name}**")
            else:
                lines.append(f"`{idx}.` {emoji} {name}")

        result_text = "\n".join(lines)

        await i.followup.send(
            f"Signal Search x10 successful! Here's what you got:\n\n{result_text}"
        )

        # --- Envanter güncelle ---
        for pull_result, is_char, is_s_rank in results:
            # Hatalı çekimleri atla
            if pull_result == "❌ Error":
                continue

            if is_char:
                cursor.execute(
                    "SELECT mindscape FROM user_characters WHERE user_id = ? AND character_name = ?",
                    (
                        i.user.id,
                        pull_result[1],
                    ),
                )
                validation = cursor.fetchone()
                if validation is None:
                    cursor.execute(
                        """
                        INSERT INTO user_characters(
                            user_id,
                            character_name,
                            mindscape,
                            obtained_at,
                            char_level,
                            w_engine,
                            rarity
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            i.user.id,
                            pull_result[1],
                            0,
                            datetime.now(timezone.utc).isoformat(),
                            1,
                            None,
                            "S" if is_s_rank else "A" if pull_result[2] == "A" else "B",
                        ),
                    )
                else:
                    new_mindscape = min(validation[0] + 1, 6)
                    cursor.execute(
                        "UPDATE user_characters SET mindscape = ? WHERE user_id = ? AND character_name = ?",
                        (
                            new_mindscape,
                            i.user.id,
                            pull_result[1],
                        ),
                    )
            else:
                cursor.execute(
                    "SELECT refinement FROM user_w_engines WHERE user_id = ? AND engine_name = ?",
                    (
                        i.user.id,
                        pull_result[1],
                    ),
                )
                validation = cursor.fetchone()
                if validation is None:
                    cursor.execute(
                        """
                        INSERT INTO user_w_engines(
                            user_id,
                            engine_name,
                            refinement,
                            obtained_at,
                            weng_level,
                            rarity
                        )
                        VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        (
                            i.user.id,
                            pull_result[1],
                            0,
                            datetime.now(timezone.utc).isoformat(),
                            1,
                            "S" if is_s_rank else "A" if pull_result[2] == "A" else "B",
                        ),
                    )
                else:
                    new_refinement = min(validation[0] + 1, 5)
                    cursor.execute(
                        "UPDATE user_w_engines SET refinement = ? WHERE user_id = ? AND engine_name = ?",
                        (
                            new_refinement,
                            i.user.id,
                            pull_result[1],
                        ),
                    )

        conn.commit()


async def setup(bot):
    await bot.add_cog(SignalSearch(bot))
