import disnake
from disnake.ext import commands
import os
import ssl
import json

# Fix SSL issues (Windows)
ssl._create_default_https_context = ssl._create_unverified_context

# Set perms for bot
intents = disnake.Intents.all()
intents.members = True
intents.message_content = True  # ← VERY IMPORTANT
intents.guilds = True

# Prefix-based AND slash-based bot
# Slash commands DO NOT use prefix — this is fine
bot = commands.Bot(command_prefix="/", intents=intents)

GUILD_ID = []

# Paths
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
COGS_PATH = os.path.join(SCRIPT_DIR, "cogs")

# Load mhr.json (for GoodCog fallback)
MHR_PATH = os.path.join(SCRIPT_DIR, "mhr.json")
try:
    with open(MHR_PATH, "r", encoding="utf-8") as f:
        MHR_DATA = json.load(f)
    print(f"[MAIN] Loaded mhr.json from {MHR_PATH}")
except FileNotFoundError:
    print(f"[MAIN] ERROR: mhr.json not found at {MHR_PATH}")
    MHR_DATA = {}

# ------------ BOT READY ------------
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user.name}")
    for g in bot.guilds:
        GUILD_ID.append(g.id)
        print(g.name)

    activity = disnake.Activity(
        type=disnake.ActivityType.playing,
        name="Saathi Mental Wellness",
        details="Supporting Youth",
        assets={"large_image": "pink", "large_text": "Saathi"},
    )
    await bot.change_presence(activity=activity)

# ------------ LOAD COGS ------------
def load_cogs():
    if not os.path.exists(COGS_PATH):
        print(f"[ERROR] cogs folder not found: {COGS_PATH}")
        return
    
    for folder in os.listdir(COGS_PATH):
        folder_path = os.path.join(COGS_PATH, folder)
        if os.path.isdir(folder_path) and os.path.exists(os.path.join(folder_path, "__init__.py")):
            try:
                bot.load_extension(f"cogs.{folder}")
                print(f"Sokudo Loaded: {folder}")
            except Exception as e:
                print(f"\n[ERROR LOADING {folder}] {e}\n")

load_cogs()

# ------------ SLASH COMMAND EXAMPLE ------------
@bot.slash_command(name="hello", description="Say hello!", guild_ids=GUILD_ID)
async def hello_slash(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(f"Hello, {inter.author.mention}! 😊")

# ------------ ADMIN COMMANDS ------------
@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    try:
        bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Loaded `{extension}` successfully.")
    except Exception as e:
        await ctx.send(f"Failed to load `{extension}`:\n{e}")

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    try:
        bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Unloaded `{extension}` successfully.")
    except Exception as e:
        await ctx.send(f"Failed to unload `{extension}`:\n{e}")

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"Reloaded `{extension}` successfully.")
    except Exception as e:
        await ctx.send(f"Failed to reload `{extension}`:\n{e}")

# ------------ LOG COMMAND USE ------------
@bot.event
async def on_command(ctx):
    command_name = ctx.command.name if ctx.command else 'Unknown'
    user = ctx.author
    channel = ctx.channel
    guild = ctx.guild.name if ctx.guild else 'DM'
    location = f"Guild: {guild}, Channel: {channel}" if guild != 'DM' else 'Direct Message'

    print(f"Command '{command_name}' used by {user} in {location}")

    embed = disnake.Embed(
        title=f"Command {command_name} Used",
        description=f"Command: `{command_name}`\nUser: {user.display_name}\nLocation: {location}"
    )

    # OPTIONAL: Change this
    logging_channel_id = 1441897878711832658  # Replace with your logging channel ID
    log_channel = bot.get_channel(logging_channel_id)
    if log_channel:
        await log_channel.send(embed=embed)

# ------------ RUN BOT ------------
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("[FATAL] DISCORD_TOKEN environment variable is not set!")
    else:
        bot.run(token)
