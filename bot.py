import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await message.channel.send(f'Hello, {message.author}')
    await bot.process_commands(message)

@bot.command(name="hello")
async def HelloCommand(ctx):
    await ctx.send("Hello")

bot.run(DISCORD_TOKEN)