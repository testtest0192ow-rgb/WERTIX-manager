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

def create_embed(title, desc):
    embed = discord.Embed(title=title, description=desc, color=0x2b2d31)
    embed.set_footer(text="WERTIX SYSTEM | SECURITY PROTOCOL")
    embed.timestamp = discord.utils.utcnow()
    return embed

# --- КОМАНДЫ ДЛЯ ХЕЛПЕРОВ И МОДЕРОВ ---
@bot.tree.command(name="mute", description="Мут (Хелпер+)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(int: discord.Interaction, member: discord.Member, time: str, reason: str = "Нет"):
    await int.response.defer()
    mins = int(re.search(r'\d+', time).group()) if re.search(r'\d+', time) else 10
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=mins), reason=reason)
    await int.followup.send(embed=create_embed("🔇 Мут", f"{member.mention} на {mins} мин.\nПричина: {reason}"))

@bot.tree.command(name="warn", description="Варн (Хелпер+)")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(int: discord.Interaction, member: discord.Member, reason: str = "Нет"):
    await int.response.defer()
    warns[member.id] = warns.get(member.id, 0) + 1
    await int.followup.send(embed=create_embed("⚠️ Варн", f"{member.mention} ({warns[member.id]}/3)\nПричина: {reason}"))

# --- КОМАНДЫ ТОЛЬКО ДЛЯ МОДЕРОВ ---
@bot.tree.command(name="ban", description="Бан (Только Модератор)")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(int: discord.Interaction, member: discord.Member, reason: str = "Нет"):
    await int.response.defer()
    await member.ban(reason=reason)
    await int.followup.send(embed=create_embed("🔨 Бан", f"{member.mention} забанен."))

# --- ОШИБКИ И ПРАВА ---
@bot.tree.error
async def on_app_command_error(int: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await int.response.send_message("🚫 У вас недостаточно прав для этой команды.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("WERTIX SYSTEM | ACTIVE")

bot.run(TOKEN)
