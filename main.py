import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Словарь для хранения варнов
warns = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"WERTIX SYSTEM | FULLY OPERATIONAL")

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

# --- КОМАНДЫ ---

@bot.tree.command(name="warn", description="Выдать предупреждение")
@app_commands.checks.has_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    user_id = str(member.id)
    warns[user_id] = warns.get(user_id, 0) + 1
    count = warns[user_id]

    # Отправка уведомления о варне
    embed_dm = create_embed("⚠️ Вы получили ПРЕДУПРЕЖДЕНИЕ", f"Сервер: {interaction.guild.name}\nПричина: {reason}\nВсего варнов: {count}/3", discord.Color.yellow())
    await send_dm(member, embed_dm)
    
    msg = f"{member.mention} получил варн. Всего: {count}."

    # Логика автоматического мута
    if count >= 3:
        duration = datetime.timedelta(hours=1)
        await member.timeout(duration, reason="3 предупреждения")
        msg += "\n🚫 **Автоматически выдан мут на 1 час (3 варна).**"
        
        embed_mute = create_embed("🔇 Авто-МУТ", f"Вы получили мут на 1 час за 3 предупреждения.", discord.Color.red())
        await send_dm(member, embed_mute)
        
        # Сбрасываем варны после мута (опционально, можно убрать эту строку)
        warns[user_id] = 0 

    await interaction.response.send_message(embed=create_embed("⚠️ Варн", msg, discord.Color.yellow()))

@bot.tree.command(name="warnlist", description="Показать список нарушителей")
@app_commands.checks.has_permissions(manage_messages=True)
async def warnlist(interaction: discord.Interaction):
    if not warns:
        return await interaction.response.send_message("На сервере пока нет нарушителей.")
    
    description = ""
    for user_id, count in warns.items():
        if count > 0:
            member = interaction.guild.get_member(int(user_id))
            name = member.mention if member else f"ID: {user_id}"
            description += f"👤 {name} — **{count} варн(а/ов)**\n"
    
    if not description:
        return await interaction.response.send_message("Список нарушителей пуст.")
        
    await interaction.response.send_message(embed=create_embed("📜 Список предупреждений", description, discord.Color.purple()))

# Оставляем команды ban, unban, mute, unmute, unwarn без изменений
bot.run(os.environ['DISCORD_TOKEN'])
