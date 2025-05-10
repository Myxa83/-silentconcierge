from dotenv import load_dotenv
import os
from datetime import datetime
import pytz  # Додано для часових поясів

# Завантаження .env або Secrets
load_dotenv()

import discord
from discord import Embed
from discord.ext import commands
import random

# --- DEBUG: перевірка токена ---
TOKEN = os.getenv("TOKEN")
print("DEBUG TOKEN:", TOKEN)

# --- Інтенції ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# --- Створення бота ---
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Конфіг ---
OWNER_ID = 279395551198445568  # 🔺 Заміни на свій Discord ID
raid_data = {
    'slots': 0,
    'taken': 0,
    'is_closed': False,
    'channel_id': None,
    'message_id': None
}

# --- Подія при вході нового учасника ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1324854638276509828)
    if channel:
        welcome_messages = [
            "📢 Важливе оголошення! В нашій секті… ой, тобто на сервері, новий учасник — {mention}! Тепер ти один із нас! 😜",
            "🔥 МОМЕНТАЛЬНИЙ ЛЕВЕЛ-АП! {mention} прокачав сервер до +100 до карми!",
            "⚠️ ОБЕРЕЖНО! Новий вибуховий елемент у чаті – {mention}!",
            "‼️НЕГАЙНО!!! Тут {mention} наближається!!!",
            "🎤 Пані та панове, зустрічайте – {mention}! 👏",
            "💀 КОД ЧОРНОГО ВІТРІЛА АКТИВОВАНО! {mention} на палубі!",
            "⚠️ КРИТИЧНИЙ ВИБУХ КРУТОСТІ! {mention} активував ульту!",
            "📣 Докладаю! {mention} залетів на базу з двох ніг!",
            "🌌 Всесвіт почув молитви – {mention} тут! 🧓"
        ]

        msg_text = random.choice(welcome_messages).format(mention=member.mention)

        embed = Embed(
            title="# 👋 Ласкаво просимо!",
            description="### " + msg_text,
            color=0x00ffcc
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        embed.set_image(url="https://i.imgur.com/Mt7OfAO.jpeg")
        embed.add_field(name="🕵️‍♂️ Шепотіть:", value="```diff\nFalgestar```", inline=True)
        embed.set_footer(text="Silent Cove")

        await channel.send(embed=embed)

# --- Команда !debug ---
@bot.command()
async def debug(ctx):
    await ctx.send("✅ Бот активний і працює.")

# --- Команда !довідка ---
@bot.command(name="довідка")
async def help_command(ctx):
    embed = discord.Embed(
        title="# 📜 Доступні команди",
        description="### Ось список команд, які можна використовувати:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!найм <дата> <час найму> <час старту> <сервер> <нік> <кількість>:", value="### Створює повідомлення про найм.", inline=False)
    embed.add_field(name="!add [кількість]:", value="### Додає вказану кількість учасників до найму (за замовчуванням 1).", inline=False)
    embed.add_field(name="!remove:", value="### Видаляє одного учасника з найму.", inline=False)
    embed.add_field(name="!закрити:", value="### Закриває найм і змінює статус повідомлення.", inline=False)
    embed.add_field(name="!debug:", value="### Перевіряє, чи активний бот.", inline=False)
    embed.add_field(name="!hello:", value="### Бот привітає вас у відповідь.", inline=False)
    await ctx.send(embed=embed)

# --- Команда !hello ---
@bot.command()
async def hello(ctx):
    await ctx.send(f"Привіт, {ctx.author.name}! Я тут, як завжди")

# --- Команда !add ---
@bot.command(name="add")
async def add_slot(ctx, count: int = 1):
    if raid_data['is_closed']:
        await ctx.send("❌ Найм вже закрито.")
        return

    if raid_data['taken'] + count > raid_data['slots']:
        await ctx.send("❌ Недостатньо вільних місць.")
        return

    raid_data['taken'] += count

    # оновлення повідомлення
    channel = bot.get_channel(raid_data['channel_id'])
    message = await channel.fetch_message(raid_data['message_id'])

    embed = message.embeds[0]
    embed.set_field_at(index=6, name="🧮 Залишилось:", value=str(raid_data['slots'] - raid_data['taken']), inline=True)
    await message.edit(embed=embed)

    await ctx.send(f"✅ Додано {count} учасника(ів) до найму.")
