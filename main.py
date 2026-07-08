import discord
from discord.ext import commands
from discord import app_commands
import datetime
import os
import re

TOKEN = os.environ.get('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='!', intents=intents)

warns = {}

def parse_time(time_str):
    time_str = time_str.lower().replace(" ", "")
    match = re.match(r"(\d+)([smhd])", time_str)
    if not match: return 10
    amount, unit = int(match.group(1)), match.group(2)
    multipliers = {'s': 1/60, 'm': 1, 'h': 60, 'd': 1440}
    return int(amount * multipliers.get(unit, 1))

# Красивый и чистый стиль
def create_embed(member, title, action, reason, duration=None):
    embed = discord.Embed(title=title, color=0x2b2d31)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="Действие", value=action, inline=True)
    embed.add_field(name="Причина", value=reason, inline=False)
    if duration:
        embed.add_field(name="Длительность", value=duration, inline=True)
    embed.set_footer(text=f"ID: {member.id} | WERTIX SYSTEM")
    embed.timestamp = discord.utils.utcnow()
    return embed

# ЛС сообщение (кратко и по делу)
async def send_dm(member, title, text):
    try:
        embed = discord.Embed(title=title, description=text, color=0x2b2d31)
        await member.send(embed=embed)
    except: pass

@bot.tree.command(name="mute", description="Выдать мут")
async def mute(int: discord.Interaction, member: discord.Member, time: str, reason: str = "Не указана"):
    await int.response.defer()
    mins = parse_time(time)
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=mins), reason=reason)
    embed = create_embed(member, "🔇 Мут", "Ограничение доступа", reason, time)
    await int.followup.send(embed=embed)
    await send_dm(member, "🔇 Вы получили мут", f"Причина: {reason}\nВремя: {time}")

@bot.tree.command(name="ban", description="Забанить")
async def ban(int: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    await member.ban(reason=reason)
    embed = create_embed(member, "🔨 Бан", "Полный запрет", reason)
    await int.response.send_message(embed=embed)
    await send_dm(member, "🔨 Вы забанены", f"Причина: {reason}")

@bot.tree.command(name="warn", description="Предупреждение")
async def warn(int: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    await int.response.defer()
    uid = member.id
    warns[uid] = warns.get(uid, 0) + 1
    if warns[uid] >= 3:
        warns[uid] = 0
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(hours=1), reason="3 варна")
        embed = create_embed(member, "🚫 Авто-мут", "Лимит варнов 3/3", "Превышение лимита", "1 час")
        await send_dm(member, "🚫 Авто-мут", "Вы получили 3 варна и отправлены в мут на 1 час.")
    else:
        embed = create_embed(member, "⚠️ Предупреждение", f"Варн {warns[uid]}/3", reason)
        await send_dm(member, "⚠️ Предупреждение", f"Варн {warns[uid]}/3. Причина: {reason}")
    await int.followup.send(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("WERTOX SYSTEM | ONLINE")

bot.run(TOKEN)
