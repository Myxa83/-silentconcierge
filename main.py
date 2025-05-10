from dotenv import load_dotenv
import os
from datetime import datetime
import pytz

load_dotenv()

import discord
from discord import Embed
from discord.ext import commands
import random

TOKEN = os.getenv("TOKEN")
print("DEBUG TOKEN:", TOKEN)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

OWNER_ID = 279395551198445568
raid_data = {
    'slots': 0,
    'taken': 0,
    'is_closed': False,
    'channel_id': None,
    'message_id': None
}

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1324986848866599004)
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
            title="👋 Ласкаво просимо!",
            description="### " + msg_text,
            color=0x00ffcc
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        embed.set_image(url="https://i.imgur.com/Mt7OfAO.jpeg")
        embed.add_field(
            name="🕵️‍♂️ Шепотіть:",
            value=f"""```ansi
\u001b[0;31mFalgestar\u001b[0m```""",
            inline=True
        )
        embed.set_footer(text="Silent Cove")
        await channel.send(embed=embed)

@bot.command()
async def debug(ctx):
    await ctx.send("✅ Бот активний і працює.")

@bot.command(name="довідка")
async def help_command(ctx):
    embed = discord.Embed(
        title="📜 Доступні команди",
        description="### Ось список команд, які можна використовувати:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!найм <дата> <час найму> <час старту> <сервер> <нік> <кількість>", value="Створює повідомлення про найм.", inline=False)
    embed.add_field(name="!add [кількість]", value="Додає вказану кількість учасників до найму (за замовчуванням 1).", inline=False)
    embed.add_field(name="!remove", value="Видаляє одного учасника з найму.", inline=False)
    embed.add_field(name="!закрити", value="Закриває найм і змінює статус повідомлення.", inline=False)
    embed.add_field(name="!скинути", value="Обнуляє всі дані про найм.", inline=False)
    embed.add_field(name="!debug", value="Перевіряє, чи активний бот.", inline=False)
    embed.add_field(name="!hello", value="Бот привітає вас у відповідь.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Привіт, {ctx.author.name}! Я тут, як завжди")


@bot.command(name="remove")
async def remove_slot(ctx, count: int = 1):
    if raid_data['taken'] == 0:
        await ctx.send("⚠️ У наймі ще немає учасників.")
        return

    raid_data['taken'] = max(0, raid_data['taken'] - count)

    channel = bot.get_channel(raid_data['channel_id'])
    try:
        message = await channel.fetch_message(raid_data['message_id'])
    except discord.NotFound:
        await ctx.send("❌ Неможливо оновити найм: повідомлення не знайдено.")
        return

    embed = message.embeds[0]
    lines = embed.description.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("🎫"):
            lines[i] = f"🎫 **Слотів:** {raid_data['slots']}    ✅ **Залишилось:** {raid_data['slots'] - raid_data['taken']}"
            break
    embed.description = '\n'.join(lines)
    await message.edit(embed=embed)

    await ctx.send(f"↩️ Видалено {count} учасника(ів) з найму.")

@bot.command(name="найм")
async def raid_post(ctx, date, recruit_time, start_time, server, nickname, slots: int, channel_name: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("⛔ У вас немає прав для цієї команди.")
        return

    raid_data['slots'] = slots
    raid_data['taken'] = 0
    raid_data['is_closed'] = False

    channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
    if not channel:
        await ctx.send(f"❌ Канал з назвою '{channel_name}' не знайдено.")
        return

    embed = Embed(
        title="✨ Гільдійні боси з SilentCove",
        description=(
            f"📅 **Дата:** {date}\n\n"
            f"🔴 **Шепотіть:** ```ansi\n\u001b[0;31m{nickname}\u001b[0m```\n\n"
            f"🧭 **Найм:** {recruit_time} *(можу бути афк)*\n\n"
            f"🎁 **Винагорода:** буде роздаватись одразу, тому почекайте 5 хвилин після заходу й чекніть нагороду.\n\n"
            f"🌍 **Сервер:** `{server}` *(уточніть в ПМ)*\n\n"
            f"⏱ **Старт:** {start_time}, після босів LoML\n\n"
            f"🛤 **Шлях:** Хан → Бруд → Феррід → CTG на Футурума *(між босами 3–4 хв)*\n\n"
            f"🐉 **Боси:** 3 рівня\n\n"
            f"⚠️ **Примітка:** Якщо ви забукіровали місце в альянсі, не протискайте прийняття до відведеного часу.\n\n"
            f"🎫 **Слотів:** {slots}    ✅ **Залишилось:** {slots}"
        ),
        color=0x00ffcc
    )
    embed.set_image(url="https://i.imgur.com/Mt7OfAO.jpeg")
    embed.set_footer(text="Silent Concierge | Найм активний")

    msg = await channel.send(embed=embed)
    if msg:
        raid_data['channel_id'] = channel.id
        raid_data['message_id'] = msg.id
@bot.command(name="закрити")
async def close_raid(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("⛔ У вас немає прав для цієї команди.")
        return
    raid_data['is_closed'] = True

    channel = bot.get_channel(1324986848866599004)
    message = await channel.fetch_message(raid_data['message_id'])

    embed = message.embeds[0]
    embed.color = 0x777777
    embed.set_footer(text="Silent Concierge | Найм завершено")
    await message.edit(embed=embed)
    await ctx.send("🔒 Найм закрито.")

@bot.command(name="скинути")
async def reset_raid_data(ctx):
    raid_data['slots'] = 0
    raid_data['taken'] = 0
    raid_data['is_closed'] = False
    raid_data['channel_id'] = None
    raid_data['message_id'] = None
    await ctx.send("🔄 Дані найму скинуто. Тепер ви можете створити новий найм.")

bot.run(TOKEN)
