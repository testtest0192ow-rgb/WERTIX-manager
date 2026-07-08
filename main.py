import discord
from discord.ext import commands
from discord import app_commands
import datetime
import os

TOKEN = os.environ.get('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='!', intents=intents)

warns = {}

def create_embed(title, desc):
    embed = discord.Embed(title=title, description=desc, color=0x2b2d31)
    embed.set_footer(text="WERTIX SYSTEM | ELITE PROTECTION")
    embed.timestamp = discord.utils.utcnow()
    return embed

# --- КОМАНДЫ ---

@bot.tree.command(name="mute", description="Мут")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(int: discord.Interaction, member: discord.Member, time: str, reason: str = "Нет"):
    await int.response.defer()
    mins = int(re.search(r'\d+', time).group()) if re.search(r'\d+', time) else 10
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=mins), reason=reason)
    await int.followup.send(embed=create_embed("🔇 Мут", f"{member.mention} на {mins} мин.\nПричина: {reason}"))

@bot.tree.command(name="unmute", description="Анмут")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(int: discord.Interaction, member: discord.Member):
    await int.response.defer()
    await member.timeout(None)
    await int.followup.send(embed=create_embed("✅ Анмут", f"{member.mention} свободен."))

@bot.tree.command(name="ban", description="Бан")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(int: discord.Interaction, member: discord.Member, reason: str = "Нет"):
    await int.response.defer()
    await member.ban(reason=reason)
    await int.followup.send(embed=create_embed("🔨 Бан", f"{member.mention} забанен."))

@bot.tree.command(name="unban", description="Разбан по ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(int: discord.Interaction, user_id: str):
    await int.response.defer()
    user = await bot.fetch_user(int(user_id))
    await int.guild.unban(user)
    await int.followup.send(embed=create_embed("🔓 Разбан", f"{user.name} разбанен."))

@bot.tree.command(name="warn", description="Варн")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(int: discord.Interaction, member: discord.Member, reason: str = "Нет"):
    await int.response.defer()
    warns[member.id] = warns.get(member.id, 0) + 1
    await int.followup.send(embed=create_embed("⚠️ Варн", f"{member.mention} ({warns[member.id]}/3)\nПричина: {reason}"))

@bot.tree.command(name="unwarn", description="Снять варн")
@app_commands.checks.has_permissions(moderate_members=True)
async def unwarn(int: discord.Interaction, member: discord.Member):
    await int.response.defer()
    if warns.get(member.id, 0) > 0:
        warns[member.id] -= 1
        await int.followup.send(embed=create_embed("✅ Снятие варна", f"У {member.mention} теперь {warns[member.id]}/3 варнов."))
    else:
        await int.followup.send("У пользователя нет активных варнов.")

@bot.tree.command(name="warnlist", description="Список варнов")
async def warnlist(int: discord.Interaction):
    desc = "\n".join([f"<@{uid}>: {count}/3" for uid, count in warns.items() if count > 0]) or "Список чист."
    await int.response.send_message(embed=create_embed("📋 Warn List", desc))

@bot.tree.error
async def on_app_command_error(int: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await int.response.send_message("🚫 Недостаточно прав.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("WERTIX SYSTEM | FULLY OPERATIONAL")

bot.run(TOKEN)
