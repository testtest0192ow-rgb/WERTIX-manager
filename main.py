from flask import Flask
from threading import Thread
import discord
import datetime
import os
import json
from discord import app_commands
from discord.ext import commands

# --- ВЕБ-СЕРВЕР ДЛЯ ПОДДЕРЖАНИЯ ЖИЗНИ НА RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "WERTIX SECURITY: Operational"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# --- ЯДРО И КОНФИГУРАЦИЯ ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

WARNS_FILE = "warns.json"
LOG_CHANNEL_ID = 1523365711790080151

def load_data():
    if os.path.exists(WARNS_FILE):
        try:
            with open(WARNS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data():
    with open(WARNS_FILE, "w") as f:
        json.dump(warns, f, indent=4)

warns = load_data()

# --- WERTIX SECURITY PREMIUM UI ---
class UI:
    @staticmethod
    def embed(title, desc, color, target, admin, fields=None):
        embed = discord.Embed(
            title=f"WERTIX SECURITY | {title.upper()}",
            description=desc,
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=f"Moderator: {admin.display_name}", icon_url=admin.display_avatar.url)
        if target:
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.add_field(name="Target User", value=target.mention, inline=True)
        
        if fields:
            for k, v in fields.items():
                embed.add_field(name=k, value=v, inline=True)
                
        embed.set_footer(text="WERTIX SEC | TRANSCENDENT PROTOCOL")
        return embed

# --- ДИСПЕТЧЕР БЕЗОПАСНОСТИ ---
async def dispatch(interaction, member, title, desc, color, fields=None):
    try:
        embed = UI.embed(title, desc, color, member, interaction.user, fields)
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)
            
        log_ch = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_ch:
            await log_ch.send(embed=embed)
            
        try:
            await member.send(embed=embed)
        except Exception:
            pass
    except Exception as e:
        print(f"CRITICAL DISPATCH ERROR: {e}")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("WERTIX SYSTEM | TRANSCENDENT MODE | OPERATIONAL")

# --- КОМАНДЫ МОДЕРАЦИИ ---

@bot.tree.command(name="ban", description="Перманентная блокировка пользователя")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Нарушение правил"):
    await member.ban(reason=reason)
    await dispatch(interaction, member, "BAN", f"Объект удален из реестра.\nПричина: {reason}", discord.Color.red())

@bot.tree.command(name="unban", description="Восстановление доступа пользователю")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    await interaction.response.defer(ephemeral=True)
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.followup.send(f"Доступ для {user.name} восстановлен.")
    except Exception:
        await interaction.followup.send("Не удалось снять бан. Проверьте ID.")

@bot.tree.command(name="mute", description="Таймаут нарушителя")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Нарушение правил"):
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
    await dispatch(interaction, member, "TIMEOUT", f"Изоляция активирована на {minutes} мин.\nПричина: {reason}", discord.Color.orange())

@bot.tree.command(name="unmute", description="Снятие таймаута")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.edit(timed_out_until=None)
    await dispatch(interaction, member, "UNMUTE", "Изоляция принудительно прекращена.", discord.Color.green())

@bot.tree.command(name="warn", description="Регистрация инцидента и выдача предупреждения")
@app_commands.checks.has_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Нарушение правил"):
    uid = str(member.id)
    warns[uid] = warns.get(uid, 0) + 1
    count = warns[uid]
    
    desc = f"Предупреждение зафиксировано в реестре.\nПричина: {reason}"
    
    if count >= 3:
        await member.timeout(datetime.timedelta(hours=5), reason="Критический лимит предупреждений")
        desc = "Критический лимит достигнут. Активирован 5-часовой протокол изоляции."
        warns[uid] = 0
        
    save_data()
    await dispatch(interaction, member, "WARNING", desc, discord.Color.yellow(), {"Всего варнов": str(count)})

@bot.tree.command(name="unwarn", description="Аннулирование дисциплинарного предупреждения")
@app_commands.checks.has_permissions(manage_messages=True)
async def unwarn(interaction: discord.Interaction, member: discord.Member):
    uid = str(member.id)
    if uid in warns and warns[uid] > 0:
        warns[uid] -= 1
        count = warns[uid]
        save_data()
        await dispatch(interaction, member, "UNWARN", "Дисциплинарное замечание аннулировано.", discord.Color.green(), {"Осталось варнов": str(count)})
    else:
        await interaction.response.send_message("У объекта нет активных предупреждений.", ephemeral=True)

@bot.tree.command(name="clear", description="Очистка сообщений")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        return await interaction.response.send_message("Укажите число от 1 до 100.", ephemeral=True)
        
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Очищено сообщений: {len(deleted)}")

@bot.tree.command(name="warnlist", description="Глобальный реестр нарушений")
@app_commands.checks.has_permissions(manage_messages=True)
async def warnlist(interaction: discord.Interaction):
    data = sorted([(k, v) for k, v in warns.items() if v > 0], key=lambda x: x[1], reverse=True)
    list_str = "\n".join([f"<@{u}> — {c} варнов" for u, c in data]) if data else "Реестр пуст."
    
    embed = discord.Embed(title="WERTIX | GLOBAL REGISTRY", description=list_str, color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed)

bot.run(os.environ['DISCORD_TOKEN'])
