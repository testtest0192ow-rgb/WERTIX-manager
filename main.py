import discord
from discord.ext import commands
from discord import app_commands
import datetime
import os
import re

# Токен берется из облака
TOKEN = os.environ.get('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='!', intents=intents)

# База данных варнов: {member_id: warn_count}
warns = {}

# === ЯДРО СИСТЕМЫ ===
def parse_time(time_str):
    time_str = time_str.lower().replace(" ", "")
    match = re.match(r"(\d+)([smhd])", time_str)
    if not match: return 10 # По умолчанию 10 минут
    amount, unit = int(match.group(1)), match.group(2)
    multipliers = {'s': 1/60, 'm': 1, 'h': 60, 'd': 1440}
    return int(amount * multipliers.get(unit, 1))

def get_embed(title, desc, color, emoji):
    embed = discord.Embed(title=f"{emoji} {title}", description=desc, color=color)
    embed.set_footer(text="WERTOX SYSTEM | ELITE PROTECTION")
    embed.timestamp = discord.utils.utcnow()
    return embed

# === КОМАНДЫ ===

@bot.tree.command(name="mute", description="Мут (например: 10м, 1ч, 1д)")
async def mute(int: discord.Interaction, member: discord.Member, time: str, reason: str = "Нет"):
    await int.response.defer()
    mins = parse_time(time)
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=mins), reason=reason)
    await int.followup.send(embed=get_embed("MUTE", f"{member.mention} в муте на {time}.\nПричина: {reason}", 0x2f3136, "🔇"))

@bot.tree.command(name="unmute", description="Снять мут")
async def unmute(int: discord.Interaction, member: discord.Member):
    await int.response.defer()
    await member.timeout(None)
    await int.followup.send(embed=get_embed("UNMUTE", f"{member.mention} свободен.", 0x2ecc71, "✅"))

@bot.tree.command(name="warn", description="Выдать варн (3 = авто-мут)")
async def warn(int: discord.Interaction, member: discord.Member, reason: str = "Нет"):
    await int.response.defer()
    uid = member.id
    warns[uid] = warns.get(uid, 0) + 1
    
    if warns[uid] >= 3:
        warns[uid] = 0
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(hours=1), reason="3/3 Варнов")
        await int.followup.send(embed=get_embed("AUTO-MUTE", f"{member.mention} получил 3 варна и улетел в мут на 1ч.", 0xe74c3c, "🚫"))
    else:
        await int.followup.send(embed=get_embed("WARN", f"{member.mention} получил варн ({warns[uid]}/3).\nПричина: {reason}", 0xf1c40f, "⚠️"))

@bot.tree.command(name="warnlist", description="Список варнов")
async def warnlist(int: discord.Interaction):
    desc = "\n".join([f"<@{uid}>: {count}" for uid, count in warns.items()]) or "Чисто."
    await int.response.send_message(embed=get_embed("WARN LIST", desc, 0xffffff, "📋"))

@bot.tree.command(name="ban", description="Бан")
async def ban(int: discord.Interaction, member: discord.Member, reason: str = "Нет"):
    await member.ban(reason=reason)
    await int.response.send_message(embed=get_embed("BAN", f"{member.mention} забанен.", 0x000000, "🔨"))

@bot.tree.command(name="unban", description="Разбан по ID")
async def unban(int: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await int.guild.unban(user)
    await int.response.send_message(embed=get_embed("UNBAN", f"{user.name} разбанен.", 0x3498db, "🔓"))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("WERTOX SYSTEM | ONLINE")

bot.run(TOKEN)
