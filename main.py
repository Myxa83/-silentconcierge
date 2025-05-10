import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN") or "тут_токен_вручну_якщо_не_через_.env"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Бот {bot.user} запущено та slash-команди синхронізовано.")

async def main():
    async with bot:
        await bot.load_extension("raid")  # raid.py у тому ж каталозі
        await bot.start(TOKEN)

asyncio.run(main())
