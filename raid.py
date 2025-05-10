from discord.ext import commands
from discord import app_commands, Interaction, Embed
import discord
import asyncio
import datetime
import pytz

raid_data = {
    'slots': 0,
    'taken': 0,
    'is_closed': False,
    'channel_id': None,
    'message_id': None
}

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
    async def raid_post(self, interaction: Interaction, date: str, recruit_time: str, start_time: str, server: str, nickname: str, slots: int, channel_name: str):
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

        now = datetime.datetime.now(pytz.timezone("Europe/London"))
        recruit_timestamp = int(now.timestamp())
        start_timestamp = int((now + datetime.timedelta(hours=1)).timestamp())
        remaining = slots

        embed = Embed(
            title="✨ Гільдійні боси з Ｓｉｌｅｎｔ Ｃｏｖｅ",
            description=(
                f"📅 **Дата: {date}**\n\n"
                f"📌 **Шепотіть:**\n```ansi\n\u001b[0;31m{nickname}\u001b[0m\n```\n\n"
                f"⏰ **Найм:** <t:{recruit_timestamp}:t> *(можу бути афк)* Винагорода буде роздаватись одразу, тому почекайте 5 хвилин після заходу й чекніть нагороду.**\n\n"
                f"🏝️ **Сервер: {server} *(уточніть в ПМ)* **\n\n"
                f"⏱ **Старт:** <t:{start_timestamp}:t>, після босів LoML**\n\n"
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

        self.bot.loop.create_task(auto_close())

# Додати наприкінці файлу:
async def setup(bot):
    await bot.add_cog(RaidBot(bot))
