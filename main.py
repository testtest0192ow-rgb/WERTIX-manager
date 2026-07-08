import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"WERTIX SYSTEM | FULLY OPERATIONAL")

# Универсальный билдер Embed
def create_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="WERTIX Security System")
    embed.timestamp = datetime.datetime.now()
    return embed

async def send_dm(member: discord.Member, embed: discord.Embed):
    try:
        await member.send(embed=embed)
    except discord.Forbidden:
        pass

# --- КОМАНДЫ МОДЕРАЦИИ ---

@bot.tree.command(name="ban", description="Забанить участника")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    embed_dm = create_embed("🚫 Вы получили БАН", f"Сервер: {interaction.guild.name}\nПричина: {reason}", discord.Color.red())
    await send_dm(member, embed_dm)
    await member.ban(reason=reason)
    await interaction.response.send_message(embed=create_embed("🔨 Бан", f"{member.mention} был забанен.", discord.Color.red()))

@bot.tree.command(name="unban", description="Разбанить участника по ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(embed=create_embed("🔓 Разбан", f"Пользователь {user.name} был разбанен.", discord.Color.green()))

@bot.tree.command(name="mute", description="Замутить участника")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Не указана"):
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
    embed_dm = create_embed("🔇 Вы получили МУТ", f"Сервер: {interaction.guild.name}\nВремя: {minutes} мин.\nПричина: {reason}", discord.Color.orange())
    await send_dm(member, embed_dm)
    await interaction.response.send_message(embed=create_embed("🔇 Мут", f"{member.mention} в муте на {minutes} мин.", discord.Color.orange()))

@bot.tree.command(name="unmute", description="Снять мут")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.edit(timed_out_until=None)
    embed_dm = create_embed("🔊 Мут снят", f"С вас сняли ограничения на сервере {interaction.guild.name}", discord.Color.green())
    await send_dm(member, embed_dm)
    await interaction.response.send_message(embed=create_embed("🔊 Снятие мута", f"Мут с {member.mention} снят.", discord.Color.green()))

@bot.tree.command(name="warn", description="Выдать варн")
@app_commands.checks.has_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    embed_dm = create_embed("⚠️ Вы получили ПРЕДУПРЕЖДЕНИЕ", f"Сервер: {interaction.guild.name}\nПричина: {reason}", discord.Color.yellow())
    await send_dm(member, embed_dm)
    await interaction.response.send_message(embed=create_embed("⚠️ Варн", f"{member.mention} получил варн.", discord.Color.yellow()))

@bot.tree.command(name="unwarn", description="Сбросить варны")
@app_commands.checks.has_permissions(manage_messages=True)
async def unwarn(interaction: discord.Interaction, member: discord.Member):
    embed_dm = create_embed("✅ Варны сброшены", f"С вас сняли все варны на сервере {interaction.guild.name}", discord.Color.green())
    await send_dm(member, embed_dm)
    await interaction.response.send_message(embed=create_embed("✅ Варны сброшены", f"Варны у {member.mention} удалены.", discord.Color.green()))

bot.run(os.environ['DISCORD_TOKEN'])
