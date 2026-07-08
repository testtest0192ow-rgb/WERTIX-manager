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
LOG_CHANNEL_ID = 1523365711790080151  # <--- ЗАМЕНИ НА СВОЙ ID КАНАЛА ЛОГОВ

def load_warns():
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, "r") as f: return json.load(f)
    return {}

warns = load_warns()

def save_warns():
    with open(WARNS_FILE, "w") as f: json.dump(warns, f)

# ДИЗАЙНЕР ПРЕМИУМ-СООБЩЕНИЙ
def get_embed(title, desc, color, target, admin, fields=None):
    embed = discord.Embed(title=f"『 WERTIX 』| {title}", description=desc, color=color)
    embed.set_author(name=f"Admin: {admin.name}", icon_url=admin.display_avatar.url)
    embed.set_thumbnail(url=target.display_avatar.url if hasattr(target, 'display_avatar') else None)
    if hasattr(target, 'mention'): embed.add_field(name="Target", value=f"{target.mention}", inline=True)
    if fields:
        for name, value in fields.items(): embed.add_field(name=name, value=value, inline=True)
    embed.set_footer(text="WERTIX Security | Elite Protocol", icon_url=admin.guild.icon.url if admin.guild.icon else None)
    embed.timestamp = datetime.datetime.now()
    return embed

async def execute_action(interaction, member, title, desc, color, fields=None):
    embed = get_embed(title, desc, color, member, interaction.user, fields)
    await interaction.response.send_message(embed=embed)
    log_ch = interaction.guild.get_channel(LOG_CHANNEL_ID)
    if log_ch: await log_ch.send(embed=embed)
    try: await member.send(embed=embed)
    except: pass

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"WERTIX SYSTEM | OPERATIONAL | 2026")

# --- КОМАНДЫ ---

@bot.tree.command(name="ban", description="Блокировка участника")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction, member: discord.Member, reason: str = "Нарушение"):
    await member.ban(reason=reason)
    await execute_action(interaction, member, "BAN", "Навсегда исключен из системы.", discord.Color.red(), {"Reason": reason})

@bot.tree.command(name="unban", description="Разблокировка участника")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"✅ Пользователь {user.name} был разблокирован.")

@bot.tree.command(name="mute", description="Изоляция на 5 часов")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction, member: discord.Member, reason: str = "Нарушение"):
    await member.timeout(datetime.timedelta(hours=5), reason=reason)
    await execute_action(interaction, member, "TIMEOUT", "Активирован протокол изоляции на 5 часов.", discord.Color.gold(), {"Reason": reason})

@bot.tree.command(name="unmute", description="Снятие изоляции")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction, member: discord.Member):
    await member.edit(timed_out_until=None)
    await execute_action(interaction, member, "UNMUTE", "Все ограничения сняты.", discord.Color.green())

@bot.tree.command(name="warn", description="Выдача предупреждения")
@app_commands.checks.has_permissions(manage_messages=True)
async def warn(interaction, member: discord.Member, reason: str = "Нарушение"):
    uid = str(member.id)
    warns[uid] = warns.get(uid, 0) + 1
    count = warns[uid]
    status = "Предупреждение зафиксировано."
    if count >= 3:
        await member.timeout(datetime.timedelta(hours=5), reason="Лимит варнов")
        status = "Лимит достигнут! Протокол изоляции (5ч) активен."
        warns[uid] = 0
    save_warns()
    await execute_action(interaction, member, "WARNING", status, discord.Color.yellow(), {"Violations": f"{count}/3", "Reason": reason})

@bot.tree.command(name="unwarn", description="Очистка истории")
@app_commands.checks.has_permissions(manage_messages=True)
async def unwarn(interaction, member: discord.Member):
    warns[str(member.id)] = 0
    save_warns()
    await execute_action(interaction, member, "CLEARED", "История нарушений сброшена.", discord.Color.green())

@bot.tree.command(name="warnlist", description="Просмотр базы данных")
@app_commands.checks.has_permissions(manage_messages=True)
async def warnlist(interaction):
    data = [f"👤 <@{u}> — `{c} варнов`" for u, c in warns.items() if c > 0]
    desc = "\n".join(data) if data else "База данных чиста."
    embed = discord.Embed(title="📜 WERTIX | DATABASE", description=desc, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

bot.run(os.environ['DISCORD_TOKEN'])
