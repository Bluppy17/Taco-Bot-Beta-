import os, discord, logging, random, datetime, asyncio, time, math
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="t!", ints=intents)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taco")

# Setup state
setup_done = False
command_roles = {}  # e.g. {"warn": 123456789, "ban": 987654321}
warns = {}
verified_users = set()
mod_log = []

def check_setup(ctx):
    if not setup_done:
        # Cannot proceed
        return False
    return True

@bot.event
async def on_ready():
    logger.info(f"Taco Bot online: {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="t!setup 🌮"))

@bot.command()
async def setup(ctx):
    global setup_done
    setup_done = True
    await ctx.send("Setup started 🌮 Assign roles by replying with: `warn: @Role` etc.")

# Helper to assign role
@bot.event
async def on_message(msg):
    global command_roles, setup_done
    if msg.author == bot.user:
        return
    if setup_done and msg.content.startswith("setup:"):
        parts = msg.content.replace("setup:", "").split(":")
        if len(parts) == 2:
            cmd_name = parts[0].strip()
            # Try to find role mention or name
            role_name = parts[1].strip()
            role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), msg.guild.roles)
            if role:
                command_roles[cmd_name] = role.id
                await msg.channel.send(f"Assigned `{cmd_name}` to {role.name} 🌮")
    await bot.process_commands(msg)

# Verify logic
@bot.command()
async def verify(ctx, member: discord.Member = None):
    if not check_setup(ctx):
        await ctx.send("Run `/setup` first 🌮")
        return
    target = member or ctx.author
    verified_users.add(target.id)
    await ctx.send(f"{target.display_name} verified 🌮")

@bot.command()
async def verify_all(ctx):
    if not check_setup(ctx):
        await ctx.send("Run `/setup` first 🌮")
        return
    verified_users.update(ctx.guild.members)
    await ctx.send("All verified 🌮")

# Warn logic
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not check_setup(ctx):
        await ctx.send("Run `/setup` first 🌮")
        return
    # Check role if assigned
    req_role_id = command_roles.get("warn")
    if req_role_id:
        role_obj = ctx.guild.get_role(req_role_id)
        if role_obj and role_obj not in ctx.author.roles:
            await ctx.send(f"You need {role_obj.name} to use `/warn` 🌮")
            return
    user_id = member.id
    warns.setdefault(user_id, []).append(reason)
    await ctx.send(f"Warned {member.display_name}: {reason} 🌮")

@bot.command()
async def check_warns(ctx, member: discord.Member = None):
    if not check_setup(ctx):
        await ctx.send("Run `/setup` first 🌮")
        return
    target = member or ctx.author
    user_warns = warns.get(target.id, [])
    if not user_warns:
        await ctx.send(f"No warns for {target.display_name} 🌮")
    else:
        await ctx.send(f"Warns for {target.display_name}: {len(user_warns)} 🌮")

@bot.command()
async def clear_warns(ctx, member: discord.Member):
    if not check_setup(ctx):
        await ctx.send("Run `/setup` first 🌮")
        return
    warns[member.id] = []
    await ctx.send(f"Warns cleared for {member.display_name} 🌮")

# Base
@bot.command()
async def ping(ctx):
    if not check_setup(ctx):
        await ctx.send("Run `/setup` first 🌮")
        return
    await ctx.send("Pong! 🌮")

@bot.command()
async def taco(ctx):
    if not check_setup(ctx):
        await ctx.send("Run `/setup` first 🌮")
        return
    await ctx.send("Here's a taco! 🌮")

@bot.command()
async def help(ctx):
    await ctx.send("Run `/setup` first. Then assign roles like `setup: warn: Moderator` 🌮")

bot.run(TOKEN)
