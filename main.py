from dotenv import load_dotenv
import os
from datetime import datetime

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
            "🌌 Всесвіт почув молитви – {mention} тут! 🤓"
        ]

        msg_text = random.choice(welcome_messages).format(mention=member.mention)

        embed = Embed(
            title="👋 Ласкаво просимо!",
            description=msg_text,
            color=0x00ffcc
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        embed.set_image(url="https://i.ibb.co/tbwQYFZ/bench.jpg")
        embed.set_footer(text="Silent Cove")

        await channel.send(embed=embed)

# --- Команда !debug ---
@bot.command()
async def debug(ctx):
    await ctx.send("✅ Бот активний і працює.")

# --- Команда !hello ---
@bot.command()
async def hello(ctx):
    await ctx.send(f"Привіт, {ctx.author.name}! Я тут, як завжди")

# --- Команда !найм ---
@bot.command()
async def найм(ctx, date: str, time: str, server: str, whisper: str, slots: int):
    if ctx.author.id != OWNER_ID:
        return await ctx.send("❌ Тільки організатор може створити найм.")

    try:
        dt = datetime.strptime(f"{date} {time}", "%d.%m.%Y %H:%M")
    except ValueError:
        return await ctx.send("❌ Формат: !найм 06.05.2025 18:00 Kamasylvia5 @MUSHA 15")

    raid_data['slots'] = slots
    raid_data['taken'] = 0
    raid_data['is_closed'] = False
    raid_data['channel_id'] = ctx.channel.id

    embed = discord.Embed(
        title="**Гільдійні боси з**\n**SilentCove**",
        description=f"**{date}**",
        color=discord.Color.teal()
    )
    embed.add_field(name="🔴 Шепотіть:", value=f"**{whisper}**", inline=False)
    embed.add_field(name="🧭 Найм:", value=f"`{time}` *(можу бути афк)*\nВинагорода буде роздаватись одразу, тому **почекайте 5 хвилин** після заходу й **чекніть нагороду.**", inline=False)
    embed.add_field(name="🌍 Сервер:", value=f"`{server}` *(уточніть в ПМ)*", inline=False)
    embed.add_field(name="⏱ Старт:", value="`18:10`, після босів **LoML**", inline=False)
    embed.add_field(name="🛣 Шлях:", value="Хан → Бруд → Феррід → CTG на Футурума *(між босами 3–4 хв)*", inline=False)
    embed.add_field(name="🐉 Боси:", value="3 рівня", inline=False)
    embed.add_field(name="⚠️ Примітка:", value="Якщо ви **забукіровали місце в альянсі**, не протискайте прийняття до відведеного часу.", inline=False)
    embed.add_field(name="🎫 Слотів:", value=f"`{slots}`", inline=True)
    embed.add_field(name="🟩 Залишилось:", value=f"`{slots}`", inline=True)
    embed.set_footer(text="Silent Concierge | Найм активний")

    message = await ctx.send(embed=embed)
    raid_data['message_id'] = message.id

# --- Додавання учасника ---
@bot.command()
async def add(ctx):
    if ctx.author.id != OWNER_ID or raid_data['is_closed']:
        return
    if raid_data['taken'] < raid_data['slots']:
        raid_data['taken'] += 1
        await update_embed()

# --- Видалення учасника ---
@bot.command()
async def remove(ctx):
    if ctx.author.id != OWNER_ID or raid_data['is_closed']:
        return
    if raid_data['taken'] > 0:
        raid_data['taken'] -= 1
        await update_embed()

# --- Закриття найму ---
@bot.command()
async def закрити(ctx):
    if ctx.author.id != OWNER_ID:
        return
    raid_data['is_closed'] = True
    await update_embed(closed=True)

# --- Оновлення ембеду ---
async def update_embed(closed=False):
    channel = bot.get_channel(raid_data['channel_id'])
    try:
        message = await channel.fetch_message(raid_data['message_id'])
        embed = message.embeds[0]
        embed.set_field_at(8, name="🟩 Залишилось:", value=f"`{raid_data['slots'] - raid_data['taken']}`", inline=True)
        if closed:
            embed.color = discord.Color.dark_gray()
            embed.set_field_at(0, name="✅ Найм завершено:", value="Всі місця зайняті або найм закрито.", inline=False)
            embed.set_footer(text="Silent Concierge | Найм завершено")
        await message.edit(embed=embed)
    except:
        pass

# --- Запуск ---
bot.run(TOKEN)
