import logging
import discord
import gspread
import os
import json
from discord.ext import commands
from dotenv import load_dotenv
from gspread import service_account
from google.oauth2 import service_account

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_SHEET_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
ALLOWED_USER_IDS = [163199994919256064]

# TODO update variables
INQ_LEADERSHIP_SHEET_NAME = "Inquisitor Order"
INQ_LEADERSHIP_SHEET_ID = "1QMduATDD2o0XG8P3gqMN7kVtPIpCGH_UEq3sgkwbAb8"
INQ_PUBLIC_SHEET_ID = "15Ae2gh1rHMZx6WAm0tvCGqNHvYdtWjPl6rrQEpiDKB8"
INQ_PUBLIC_SHEET_NAME = "Public Roster"

CHANNEL_NAME = "inactivity-discussion"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
logging.basicConfig(level=logging.INFO)

def GetGoogleSheet(spreadsheet):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        CredsInfo = json.loads(GOOGLE_SHEET_CREDENTIALS)
        creds = service_account.Credentials.from_service_account_info(CredsInfo, scopes=scope)
        client = gspread.authorize(creds)
        if spreadsheet == "leadership":
            sheet = client.open_by_key(INQ_LEADERSHIP_SHEET_ID).worksheet(INQ_LEADERSHIP_SHEET_NAME)
            return sheet
        elif spreadsheet == "public":
            sheet = client.open_by_key(INQ_PUBLIC_SHEET_ID).worksheet(INQ_PUBLIC_SHEET_NAME)
            return sheet
    except Exception as e:
        logging.error(f"Error accessing Google Sheet: {e}")
        return None

def CheckLoa():
    sheet = GetGoogleSheet("public")
    names = []
    rows = sheet.get_all_values()

    for row in rows:
        name = row[2]
        loa = row[17]
        if name != "" and name != "Name" and name != "dont delete":
            if loa != "ROA" and loa != "LOA":
                names.append(name)

    return names

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await check_activity()
    await bot.close()

@bot.command(name="shutdown")
@commands.is_owner()
async def shutdown(ctx):
    if ctx.author.id in ALLOWED_USER_IDS:
        await ctx.send("Shutting down the bot")
        await bot.close()
    else:
        await ctx.send("You don't have permission to shut down the bot")

async def check_activity():
    sheet = GetGoogleSheet("leadership")
    NameColumn = sheet.col_values(7)
    DiscordIDColumn = sheet.col_values(11) # TODO change to use letters
    DaysSinceColumn = sheet.col_values(12)

    NonLoaNames = CheckLoa()
    output = []

    for name, DiscordId, DaysSince in zip(NameColumn, DiscordIDColumn, DaysSinceColumn):
        if name != "" and name != "Name" and name != "dont delete":
            if name not in NonLoaNames:
                continue

            try:
                if DaysSince.isdigit():
                        DaysSince = int(DaysSince)
                if DaysSince >= 9:
                    output.append(f"0 days: <@{DiscordId}>")
                elif DaysSince == 8:
                    output.append(f"1 day: <@{DiscordId}>")
                elif DaysSince == 7:
                    output.append(f"2 days: <@{DiscordId}>")

            except TypeError as e:
                logging.error(f"Unable to convert DaysSince value for {name}: {e}")

    if output:
        response = "\n".join(output)
        channel = discord.utils.get(bot.get_all_channels(), name=CHANNEL_NAME)
        if channel:
            await channel.send(f"\n{response}\n\nIf there are any problems please DM a member of the Inquisitorious!")
        else:
            logging.error(f"Unable to find channel: {CHANNEL_NAME}")

bot.run(DISCORD_TOKEN)