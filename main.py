import discord
from discord.ext import commands
import datetime
import os
import re

TOKEN = os.environ.get('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='!', intents=intents)

warns = {}

def parse_time(time_str):
    time_str = time_str.lower().replace(" ", "")
    match = re.match(r"(\d+)([smhd])", time_str)
    if not match: return 10
    amount, unit = int(match.group(1)), match.group(2)
    multipliers = {'s': 1/60, 'm': 1, 'h': 60, 'd': 1440}
    return int(amount * multipliers.get(unit, 1))

def create_embed(title, desc):
    embed = discord.Embed(title=title, description=desc, color=0x2b2d31)
    embed.set_footer(text="WERTIX SYSTEM | SECURE OPERATIONS")
    embed.timestamp = discord.utils.utcnow()
    return embed

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, time: str, *, reason: str = "Не указана"):
    mins = parse_time(time)
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=mins), reason=reason)
    await ctx.send(embed=create_embed("🔇 Мут", f"{member.mention} на {time}.\nПричина: {reason}"))

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(embed=create_embed("✅ Анмут", f"{member.mention} свободен."))

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason: str = "Не указана"):
    warns[member.id] = warns.get(member.id, 0) + 1
    if warns[member.id] >= 3:
        warns[member.id] = 0
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(hours=1), reason="3 варна")
        await ctx.send(embed=create_embed("🚫 Авто-мут", f"{member.mention} — 3/3 варна. 1 час мута."))
    else:
        await ctx.send(embed=create_embed("⚠️ Варн", f"{member.mention} ({warns[member.id]}/3)\nПричина: {reason}"))

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "Не указана"):
    await member.ban(reason=reason)
    await ctx.send(embed=create_embed("🔨 Бан", f"{member.mention} забанен.\nПричина: {reason}"))

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(embed=create_embed("🔓 Разбан", f"{user.name} снова в строю."))

@bot.command()
async def warnlist(ctx):
    desc = "\n".join([f"<@{uid}>: {count}/3" for uid, count in warns.items() if count > 0]) or "Список чист."
    await ctx.send(embed=create_embed("📋 Warn List", desc))

@bot.event
async def on_ready():
    print("WERTIX SYSTEM | FULLY OPERATIONAL")

bot.run(TOKEN)
