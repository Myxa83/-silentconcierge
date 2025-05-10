from dotenv import load_dotenv
import os
import discord
from discord import Embed
from discord.ext import commands
import random

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

raid_data = {
    'slots': 0,
    'taken': 0,
    'is_closed': False,
    'channel_id': None,
    'message_id': None
}

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
            f"🔴 **Шепотіть:**\n```diff\n- {nickname}\n```\n\n"
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

    await ctx.send(f"✅ Додано {count} учасника(ів) до найму.")

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

@bot.command(name="закрити")
async def close_raid(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("⛔ У вас немає прав для цієї команди.")
        return

    raid_data['is_closed'] = True
    channel = bot.get_channel(raid_data['channel_id'])
    try:
        message = await channel.fetch_message(raid_data['message_id'])
    except discord.NotFound:
        await ctx.send("❌ Неможливо завершити найм: повідомлення не знайдено.")
        return

    embed = message.embeds[0]
    embed.color = 0xff3333  # Червоний
    embed.title = "🔒 **НАЙМ ЗАВЕРШЕНО**"
    embed.set_footer(text="Silent Concierge")

    if "🔴 НАЙМ ЗАКРИТО" not in embed.description:
        embed.description += "\n\n🔴 **НАЙМ ЗАКРИТО — ВСІ МІСЦЯ ЗАЙНЯТО**"

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
