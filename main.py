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

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def create_embed(title, desc):
    embed = discord.Embed(title=title, description=desc, color=0x2b2d31)
    embed.set_footer(text="WERTIX SYSTEM | SECURE OPERATIONS")
    embed.timestamp = discord.utils.utcnow()
    return embed

# --- СЛЕШ-КОМАНДЫ (С ЗАЩИТОЙ) ---

@bot.tree.command(name="ban", description="Забанить участника")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(int: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    await member.ban(reason=reason)
    await int.response.send_message(embed=create_embed("🔨 Бан", f"{member.mention} забанен."))

@bot.tree.command(name="mute", description="Замутить участника")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_mute(int: discord.Interaction, member: discord.Member, time: str, reason: str = "Не указана"):
    # Тут можно добавить parse_time логику, если нужно
    await int.response.send_message(embed=create_embed("🔇 Мут", f"{member.mention} на {time}."))

# --- ОБРАБОТКА ОШИБОК ДЛЯ СЛЕШ-КОМАНД ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("🚫 У тебя нет прав для этого.", ephemeral=True)

# --- ТЕКСТОВЫЕ КОМАНДЫ (С ЗАЩИТОЙ) ---

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "Не указана"):
    await member.ban(reason=reason)
    await ctx.send(embed=create_embed("🔨 Бан", f"{member.mention} забанен."))

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, time: str, *, reason: str = "Не указана"):
    await ctx.send(embed=create_embed("🔇 Мут", f"{member.mention} на {time}."))

# --- ОБРАБОТКА ОШИБОК ДЛЯ ТЕКСТОВЫХ КОМАНД ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=create_embed("🚫 Доступ запрещен", "У тебя недостаточно прав."))

@bot.event
async def on_ready():
    await bot.tree.sync() # Синхронизирует команды, чтобы проверки применились
    print("WERTIX SYSTEM | PROTECTED & READY")

bot.run(TOKEN)
