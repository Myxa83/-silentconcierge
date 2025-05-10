# --- 1. Імпорти та запуск dotenv ---
from dotenv import load_dotenv
import os
import discord
from discord import Embed
from discord.ext import commands
import random
import datetime
import pytz
import asyncio

TOKEN = os.getenv("TOKEN") or "тут_твій_токен"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🔗 Синхронізація slash-команд завершена. Logged in as {bot.user}")

async def main():
    async with bot:
        await bot.load_extension("raid")  # назва твого cog-файлу (raid.py або raid_cog.py)
        await bot.start(TOKEN)

asyncio.run(main())

# --- 2. Інтенції та створення бота ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 3. Словник для збереження даних найму ---
raid_data = {
    'slots': 0,
    'taken': 0,
    'is_closed': False,
    'channel_id': None,
    'message_id': None
}

# --- 4. Привітання нового учасника ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1324854638276509828)  # Заміни ID на свій
    if channel:
        embed = Embed(
            title="👋 Ласкаво просимо!",
            description=f"🎶 Пані та панове, зустрічайте – {member.mention}! 👏",
            color=0x00ffcc
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        embed.set_footer(text="Silent Concierge")

        await channel.send(embed=embed)

# --- 5. Команда /найм (slash) ---
from discord import app_commands

class RaidBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="найм", description="Створює найм у вказаному каналі")
    @app_commands.describe(
        date="Дата найму",
        recruit_time="Час найму",
        start_time="Час старту",
        server="Сервер",
        nickname="Нік шепотіння",
        slots="Кількість слотів",
        channel_name="Канал для найму"
    )
    async def raid_post(self, interaction: discord.Interaction, date: str, recruit_time: str, start_time: str, server: str, nickname: str, slots: int, channel_name: str):
        if not any(role.name == "Менеджмент" for role in interaction.user.roles):
            await interaction.response.send_message("⛔ У вас немає прав для цієї команди.", ephemeral=True)
            return

        raid_data['slots'] = slots
        raid_data['taken'] = 0
        raid_data['is_closed'] = False

        channel = discord.utils.get(interaction.guild.text_channels, name=channel_name)
        if not channel:
            await interaction.response.send_message(f"❌ Канал з назвою '{channel_name}' не знайдено.", ephemeral=True)
            return

        import datetime, pytz
        now = datetime.datetime.now(pytz.timezone("Europe/London"))
        recruit_timestamp = int(now.timestamp())
        start_timestamp = int((now + datetime.timedelta(hours=1)).timestamp())
        remaining = slots

        embed = discord.Embed(
            title="✨ Гільдійні боси з Ｓｉｌｅｎｔ Ｃｏｖｅ",
            description=(
                f"📅 **Дата: {date}**\n\n"
                f"📌 **Шепотіть:**\n```ansi\n\u001b[0;31m{nickname}\u001b[0m\n```\n\n"
                f"⏰ **Найм:** <t:{recruit_timestamp}:t> *(можу бути афк)* Винагорода буде роздаватись одразу, тому почекайте 5 хвилин після заходу й чекніть нагороду.**\n\n"
                f"🏝️ **Сервер: {server} *(уточніть в ПМ)* **\n\n"
                f"⏰ **Старт:** <t:{start_timestamp}:t>, після босів LoML**\n\n"
                f"🛤️ **Шлях: Хан → Бруд → Феррід → CTG на Футурума *(між босами 3–4 хв)* **\n\n"
                f"🐙 **Боси: 3 рівня**\n\n"
                f"📌 **Примітка: Якщо ви забукіровали місце в альянсі, не протискайте прийняття до відведеного часу.**\n\n"
                f"🧾 **Слотів:** {slots}    ✅ **Залишилось:** {remaining}"
            ),
            color=0x00ffcc
        )

        embed.set_image(url="https://i.imgur.com/Mt7OfAO.jpeg")
        embed.set_footer(text="Silent Concierge | Найм активний")

        msg = await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Найм створено в <#{channel.id}>", ephemeral=True)

        if msg:
            raid_data['channel_id'] = channel.id
            raid_data['message_id'] = msg.id

        async def auto_close():
            while not raid_data['is_closed']:
                await asyncio.sleep(30)
                current_time = datetime.datetime.now(pytz.timezone("Europe/London"))
                if current_time.hour == 17 and current_time.minute == 59:
                    raid_data['is_closed'] = True
                    embed.color = 0xff3333
                    embed.title = "🔒 **НАЙМ ЗАВЕРШЕНО**"
                    embed.set_footer(text="Silent Concierge | Найм завершено")
                    embed.description += "\n\n🔴 **НАЙМ ЗАКРИТО — ЧАС ЗАВЕРШЕННЯ**"
                    await msg.edit(embed=embed)
                    break

        import asyncio
        self.bot.loop.create_task(auto_close())


# --- 6. Команда !remove ---
@bot.command(name="remove")
async def remove_slot(ctx, count: int = 1):
    if raid_data['taken'] == 0:
        await ctx.send("⚠️ У наймі ще немає учасників.")
        return

    raid_data['taken'] = max(0, raid_data['taken'] - count)
    remaining = raid_data['slots'] - raid_data['taken']

    channel = bot.get_channel(raid_data['channel_id'])
    message = await channel.fetch_message(raid_data['message_id'])
    embed = message.embeds[0]

    lines = embed.description.split("\n")
    for i, line in enumerate(lines):
        if "🧾" in line:
            lines[i] = f"🧾 **Слотів:** {raid_data['slots']}    ✅ **Залишилось:** {remaining}"
            break

    embed.description = "\n".join(lines)
    await message.edit(embed=embed)
    await ctx.send(f"↩️ Видалено {count} учасника(ів) з найму.")


# --- 7. Команда !add ---
@bot.command(name="add")
async def add_slot(ctx, count: int = 1):
    if raid_data['is_closed']:
        await ctx.send("❌ Найм вже закрито.")
        return

    if raid_data['taken'] + count > raid_data['slots']:
        await ctx.send("❌ Недостатньо вільних місць.")
        return

    raid_data['taken'] += count
    remaining = raid_data['slots'] - raid_data['taken']

    channel = bot.get_channel(raid_data['channel_id'])
    message = await channel.fetch_message(raid_data['message_id'])
    embed = message.embeds[0]

    lines = embed.description.split("\n")
    for i, line in enumerate(lines):
        if "🧾" in line:
            lines[i] = f"🧾 **Слотів:** {raid_data['slots']}    ✅ **Залишилось:** {remaining}"
            break

    embed.description = "\n".join(lines)
    await message.edit(embed=embed)

    await ctx.send(f"✅ Додано {count} учасника(ів) до найму.")

    if raid_data['taken'] >= raid_data['slots']:
        embed.color = 0xff3333
        embed.title = "🔒 **НАЙМ ЗАВЕРШЕНО**"
        embed.set_footer(text="Silent Concierge | Найм завершено")
        embed.description += "\n\n🔴 **НАЙМ ЗАКРИТО — ВСІ МІСЦЯ ЗАЙНЯТО**"
        raid_data['is_closed'] = True
        await message.edit(embed=embed)


# --- 8. Команда !закрити ---
@bot.command(name="закрити")
async def close_raid(ctx):
    raid_data['is_closed'] = True
    channel = bot.get_channel(raid_data['channel_id'])
    message = await channel.fetch_message(raid_data['message_id'])
    embed = message.embeds[0]
    embed.title = "🔒 **НАЙМ ЗАВЕРШЕНО**"
    embed.color = 0xff3333
    embed.set_footer(text="Silent Concierge")
    embed.description += "\n\n🔴 **НАЙМ ЗАКРИТО — ВСІ МІСЦЯ ЗАЙНЯТО**"
    await message.edit(embed=embed)
    await ctx.send("🔒 Найм вручну закрито.")


# --- 9. Команда !скинути ---
@bot.command(name="скинути")
async def reset_raid_data(ctx):
    raid_data['slots'] = 0
    raid_data['taken'] = 0
    raid_data['is_closed'] = False
    raid_data['channel_id'] = None
    raid_data['message_id'] = None
    await ctx.send("🔄 Дані найму скинуто. Тепер ви можете створити новий найм.")


# --- 10. Команда !debug ---
@bot.command()
async def debug(ctx):
    await ctx.send("✅ Бот активний і працює.")


# --- 11. Команда !довідка ---
@bot.command(name="довідка")
async def help_command(ctx):
    embed = discord.Embed(
        title="📜 Доступні команди",
        description="Ось список команд, які ви можете використовувати:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!найм <дата> <найм> <старт> <сервер> <нік> <кількість> <канал>", value="Створює найм у вказаному каналі.", inline=False)
    embed.add_field(name="!add [кількість]", value="Додає учасників до найму (за замовчуванням 1).", inline=False)
    embed.add_field(name="!remove [кількість]", value="Видаляє учасників з найму.", inline=False)
    embed.add_field(name="!закрити", value="Закриває найм вручну.", inline=False)
    embed.add_field(name="!скинути", value="Скидає всі дані про найм.", inline=False)
    embed.add_field(name="!debug", value="Перевірка активності бота.", inline=False)
    await ctx.send(embed=embed)

# --- 11. Запуск бота ---
bot.run(TOKEN)
# Додати наприкінці файлу:
async def setup(bot):
    await bot.add_cog(RaidBot(bot))
