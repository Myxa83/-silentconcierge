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

    channel = bot.get_channel(raid_data['channel_id'])
    message = await channel.fetch_message(raid_data['message_id'])

    embed = message.embeds[0]
    # Витягаємо старий description:
    lines = embed.description.split('\n')

    # Замінимо рядок про слоти (рядок, що починається з "🧮"):
    for i, line in enumerate(lines):
        if line.startswith("🧮"):
            lines[i] = f"🧮 **Слотів залишилось:** {raid_data['slots'] - raid_data['taken']}"
            break

    # Оновлений description:
    embed.description = '\n'.join(lines)
    await message.edit(embed=embed)

    await ctx.send(f"✅ Додано {count} учасника(ів) до найму.")
    
    # --- Команда !remove ---
@bot.command(name="remove")
async def remove_slot(ctx, count: int = 1):
    if raid_data['taken'] == 0:
        await ctx.send("⚠️ У наймі ще немає учасників.")
        return

    raid_data['taken'] = max(0, raid_data['taken'] - count)

    channel = bot.get_channel(raid_data['channel_id'])
    message = await channel.fetch_message(raid_data['message_id'])

    embed = message.embeds[0]
    lines = embed.description.split('\n')

    for i, line in enumerate(lines):
        if line.startswith("🧮"):
            lines[i] = f"🧮 **Слотів залишилось:** {raid_data['slots'] - raid_data['taken']}"
            break

    embed.description = '\n'.join(lines)
    await message.edit(embed=embed)

    await ctx.send(f"↩️ Видалено {count} учасника(ів) з найму.")
# --- Команда !найм ---
@bot.command(name="найм")
async def raid_post(ctx, date, recruit_time, start_time, server, nickname, slots: int):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("⛔ У вас немає прав для цієї команди.")
        return

    raid_data['slots'] = slots
    raid_data['taken'] = 0
    raid_data['is_closed'] = False

    embed = Embed(
        title="✨ Гільдійні боси з SilentCove",
        description=(
            f"📅 **Дата:** {date}\n"
            f"📌 **Шепотіть:** `{nickname}`\n"
            f"⏰ **Найм:** {recruit_time} *(можу бути афк)*\n"
            f"🎁 **Винагорода:** буде роздаватись одразу, тому **почекайте 5 хвилин** після заходу й **чекніть нагороду**.\n"
            f"🌍 **Сервер:** `{server}` *(уточніть в ПМ)*\n"
            f"🚀 **Старт:** {start_time}, після босів **LoML**\n"
            f"🛤️ **Шлях:** Хан ➔ Бруд ➔ Феррід ➔ CTG на Футурума *(між босами 3–4 хв)*\n"
            f"🐙 **Боси:** 3 рівня\n"
            f"🧮 **Слотів залишилось:** {slots}\n"
            f"📎 **Примітка:** Якщо ви **забукіровали місце в альянсі**, не протискайте прийняття до відведеного часу."
        ),
        color=0x00ffcc

    embed.set_footer(text="Silent Concierge | Найм активний")
    embed.set_image(url="https://i.imgur.com/Mt7OfAO.jpeg")  # 🔺 Заміни за потреби

    msg = await ctx.send(embed=embed)
    raid_data['channel_id'] = ctx.channel.id
    raid_data['message_id'] = msg.id

# --- Команда !закрити ---
@bot.command(name="закрити")
async def close_raid(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("⛔ У вас немає прав для цієї команди.")
        return

    raid_data['is_closed'] = True

    channel = bot.get_channel(raid_data['channel_id'])
    message = await channel.fetch_message(raid_data['message_id'])
    embed = message.embeds[0]
    embed.color = 0x777777  # сірий
    embed.set_field_at(index=0, name="✅ Найм завершено:", value="Всі місця зайняті або найм закрито.", inline=False)
    embed.set_footer(text="Silent Concierge | Найм завершено")
    await message.edit(embed=embed)
    await ctx.send("🔒 Найм закрито.")
# --- Запуск бота ---
bot.run(TOKEN)
