import discord
from discord.ext import commands
from discord import app_commands
import datetime, os

TOKEN = os.environ.get('TOKEN')
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# База данных варнов (в памяти)
warns = {}

def create_embed(title, desc, color=0x2b2d31):
    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_footer(text="WERTIX SECURITY SYSTEM | PROTECTED")
    embed.timestamp = discord.utils.utcnow()
    return embed

# --- КОМАНДЫ МОДЕРАЦИИ ---

@bot.tree.command(name="mute", description="Мут пользователя")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(int: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Нет причины"):
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
    await int.response.send_message(embed=create_embed("🔇 Мут", f"{member.mention} замучен на {minutes} мин.\nПричина: {reason}"))

@bot.tree.command(name="ban", description="Бан пользователя")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(int: discord.Interaction, member: discord.Member, reason: str = "Нет причины"):
    await member.ban(reason=reason)
    await int.response.send_message(embed=create_embed("🔨 Бан", f"{member.mention} был забанен.\nПричина: {reason}"))

@bot.tree.command(name="kick", description="Кик пользователя")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(int: discord.Interaction, member: discord.Member, reason: str = "Нет причины"):
    await member.kick(reason=reason)
    await int.response.send_message(embed=create_embed("🦶 Кик", f"{member.mention} был выгнан.\nПричина: {reason}"))

@bot.tree.command(name="warn", description="Выдать варн")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(int: discord.Interaction, member: discord.Member, reason: str = "Нет причины"):
    warns[member.id] = warns.get(member.id, 0) + 1
    
    if warns[member.id] >= 3:
        warns[member.id] = 0
        await member.timeout(datetime.timedelta(hours=1), reason="3 варна")
        await int.response.send_message(embed=create_embed("🚫 Авто-мут", f"{member.mention} получил 3 варна и отправлен в мут на 1 час!"))
    else:
        await int.response.send_message(embed=create_embed("⚠️ Варн", f"{member.mention} получил варн. Всего: {warns[member.id]}/3.\nПричина: {reason}"))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("WERTIX SYSTEM | Модерация активна")

bot.run(TOKEN)
