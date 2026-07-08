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

# === ПРЕМИУМ-ЭСТЕТИКА ===
def get_embed(title, description, color, emoji):
    embed = discord.Embed(
        title=f"{emoji} {title}", 
        description=description, 
        color=color
    )
    embed.set_footer(text="WERTOX SYSTEM | SECURE OPERATIONS")
    embed.timestamp = datetime.datetime.utcnow()
    return embed

async def send_private(member, title, desc, emoji):
    try:
        await member.send(embed=get_embed(title, desc, 0x000000, emoji))
    except: pass

# === КОМАНДЫ С ЭМОДЗИ ===

@bot.tree.command(name="mute", description="Выдать мут")
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Нарушение"):
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=minutes), reason=reason)
    embed = get_embed("MUTE", f"**Участник:** {member.mention}\n**Срок:** {minutes} мин.\n**Причина:** {reason}", 0x2f3136, "🔇")
    await interaction.response.send_message(embed=embed)
    await send_private(member, "MUTE", f"Вы были ограничены в правах на {minutes} минут.\nПричина: {reason}", "🔇")

@bot.tree.command(name="unmute", description="Снять мут")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    embed = get_embed("UNMUTE", f"Участник {member.mention} был реабилитирован.", 0x2ecc71, "✅")
    await interaction.response.send_message(embed=embed)
    await send_private(member, "UNMUTE", "Ваши права голоса восстановлены.", "✅")

@bot.tree.command(name="ban", description="Забанить участника")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Нарушение"):
    await send_private(member, "BAN", f"Ваш доступ к серверу ограничен.\nПричина: {reason}", "🚫")
    await member.ban(reason=reason)
    embed = get_embed("BAN", f"Пользователь {member.mention} был изгнан из системы.\nПричина: {reason}", 0x000000, "🚫")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="warn", description="Выдать предупреждение")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Нарушение"):
    embed = get_embed("WARN", f"Участник {member.mention} получил предупреждение.\nПричина: {reason}", 0xffcc00, "⚠️")
    await interaction.response.send_message(embed=embed)
    await send_private(member, "WARN", f"Вам выдано официальное предупреждение.\nПричина: {reason}", "⚠️")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'WERTOX SYSTEM | ONLINE | {bot.user}')

bot.run(TOKEN)
