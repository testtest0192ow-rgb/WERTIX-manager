import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os
import json

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

WARNS_FILE = "warns.json"
LOG_CHANNEL_ID = 0  # <--- ВСТАВЬ СЮДА ID КАНАЛА ЛОГОВ

def load_warns():
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, "r") as f: return json.load(f)
    return {}

warns = load_warns()

def save_warns():
    with open(WARNS_FILE, "w") as f: json.dump(warns, f)

# Красивый Embed-генератор
def build_embed(title, description, color, member=None):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="WERTIX Security System | 2026")
    embed.timestamp = datetime.datetime.now()
    if member: embed.set_thumbnail(url=member.display_avatar.url)
    return embed

async def notify(interaction, member, title, desc, color):
    # 1. Отправка в ЛС
    try:
        await member.send(embed=build_embed(title, desc, color, member))
    except: pass
    # 2. Отправка в канал логов
    channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=build_embed(f"LOG: {title}", f"Цель: {member.mention}\nАдмин: {interaction.user.mention}\n{desc}", color, member))
    # 3. Ответ в чат
    await interaction.response.send_message(embed=build_embed(title, f"{member.mention} {desc}", color, member))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"WERTIX SYSTEM | FULLY OPERATIONAL")

# --- КОМАНДЫ ---

@bot.tree.command(name="ban", description="Забанить участника")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction, member: discord.Member, reason: str = "Не указана"):
    await member.ban(reason=reason)
    await notify(interaction, member, "🚫 БАН", f"был забанен.\nПричина: {reason}", discord.Color.red())

@bot.tree.command(name="unban", description="Разбанить по ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"Разбанен: {user.name}")

@bot.tree.command(name="mute", description="Замутить участника")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction, member: discord.Member, minutes: int, reason: str = "Не указана"):
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
    await notify(interaction, member, "🔇 МУТ", f"получил мут на {minutes} мин.\nПричина: {reason}", discord.Color.orange())

@bot.tree.command(name="unmute", description="Снять мут")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction, member: discord.Member):
    await member.edit(timed_out_until=None)
    await notify(interaction, member, "🔊 МУТ СНЯТ", "получил размут.", discord.Color.green())

@bot.tree.command(name="warn", description="Выдать варн")
@app_commands.checks.has_permissions(manage_messages=True)
async def warn(interaction, member: discord.Member, reason: str = "Не указана"):
    uid = str(member.id)
    warns[uid] = warns.get(uid, 0) + 1
    save_warns()
    
    desc = f"получил варн ({warns[uid]}/3).\nПричина: {reason}"
    if warns[uid] >= 3:
        await member.timeout(datetime.timedelta(hours=1), reason="3 варна")
        desc += "\n🚫 Авто-мут на 1 час!"
        warns[uid] = 0
        save_warns()
        
    await notify(interaction, member, "⚠️ ВАРН", desc, discord.Color.yellow())

bot.run(os.environ['DISCORD_TOKEN'])
