import discord, datetime, os, json
from discord import app_commands
from discord.ext import commands

# --- ЯДРО И КОНФИГУРАЦИЯ ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

WARNS_FILE = "warns.json"
LOG_CHANNEL_ID = 1523365711790080151 

def load_data():
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, "r") as f: return json.load(f)
    return {}

warns = load_data()

def save_data():
    with open(WARNS_FILE, "w") as f: json.dump(warns, f)

# --- WERTIX QUANTUM UI ---
class UI:
    @staticmethod
    def embed(title, desc, color, target, admin, fields=None):
        embed = discord.Embed(title=f"『 WERTIX SECURITY 』 :: {title}", description=desc, color=color)
        embed.set_author(name=f"Admin: {admin.display_name}", icon_url=admin.display_avatar.url)
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Target Identity", value=f"{target.mention} (`{target.id}`)", inline=True)
        if fields:
            for k, v in fields.items(): embed.add_field(name=k, value=v, inline=True)
        embed.set_footer(text="WERTIX SEC | TRANSCENDENT PROTOCOL 2026", icon_url=target.guild.icon.url)
        embed.timestamp = datetime.datetime.now()
        return embed

# --- ДИСПЕТЧЕР (БЕЗОПАСНАЯ ДОСТАВКА) ---
async def dispatch(interaction, member, title, desc, color, fields=None):
    try:
        embed = UI.embed(title, desc, color, member, interaction.user, fields)
        await interaction.response.send_message(embed=embed)
        log_ch = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_ch: await log_ch.send(embed=embed)
        try: await member.send(embed=embed)
        except: pass
    except Exception as e:
        print(f"CRITICAL DISPATCH ERROR: {e}")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"WERTIX SYSTEM | TRANSCENDENT MODE | OPERATIONAL")

# --- КОМАНДЫ ---

@bot.tree.command(name="ban", description="Перманентная блокировка")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction, member: discord.Member, reason: str = "Нарушение протокола"):
    await member.ban(reason=reason)
    await dispatch(interaction, member, "BAN", "Объект удален из реестра сервера.", discord.Color.red(), {"Reason": reason})

@bot.tree.command(name="unban", description="Восстановление доступа")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"✅ Доступ для {user.name} восстановлен.")

@bot.tree.command(name="mute", description="Таймаут нарушителя")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction, member: discord.Member, minutes: int, reason: str = "Нарушение"):
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
    await dispatch(interaction, member, "TIMEOUT", "Изоляция активирована.", discord.Color.gold(), {"Duration": f"{minutes} min", "Reason": reason})

@bot.tree.command(name="unmute", description="Снятие таймаута")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction, member: discord.Member):
    await member.edit(timed_out_until=None)
    await dispatch(interaction, member, "UNMUTE", "Изоляция принудительно снята.", discord.Color.green())

@bot.tree.command(name="warn", description="Регистрация инцидента")
@app_commands.checks.has_permissions(manage_messages=True)
async def warn(interaction, member: discord.Member, reason: str = "Нарушение"):
    uid = str(member.id)
    warns[uid] = warns.get(uid, 0) + 1
    count = warns[uid]
    desc = "Предупреждение зафиксировано в реестре."
    if count >= 3:
        await member.timeout(datetime.timedelta(hours=5), reason="Критический лимит 3/3")
        desc = "Критический лимит достигнут! Активирован 5-часовой протокол изоляции."
        warns[uid] = 0
    save_data()
    await dispatch(interaction, member, "WARNING", desc, discord.Color.yellow(), {"Violations": f"{count}/3", "Reason": reason})

@bot.tree.command(name="unwarn", description="Аннулирование дисциплинарного инцидента")
@app_commands.checks.has_permissions(manage_messages=True)
async def unwarn(interaction, member: discord.Member):
    uid = str(member.id)
    if uid in warns and warns[uid] > 0:
        warns[uid] -= 1
        count = warns[uid]
        save_data()
        await dispatch(interaction, member, "UNWARN", "Дисциплинарная запись аннулирована.", discord.Color.green(), {"Remaining": f"{count}/3"})
    else:
        await interaction.response.send_message("❌ У объекта нет активных нарушений.", ephemeral=True)

@bot.tree.command(name="clear", description="Очистка сообщений")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction, amount: int):
    if amount < 1 or amount > 100:
        return await interaction.response.send_message("❌ Укажите число от 1 до 100.", ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"✅ Очищено {len(deleted)} сообщений.", ephemeral=True)

@bot.tree.command(name="warnlist", description="Глобальный реестр нарушителей")
@app_commands.checks.has_permissions(manage_messages=True)
async def warnlist(interaction):
    data = sorted([(u, c) for u, c in warns.items() if c > 0], key=lambda x: x[1], reverse=True)
    list_str = "\n".join([f"• <@{u}> — **{c} варнов**" for u, c in data]) or "База данных чиста."
    embed = discord.Embed(title="📜 WERTIX | GLOBAL REGISTRY", description=list_str, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

bot.run(os.environ['DISCORD_TOKEN'])

