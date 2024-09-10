import logging
import discord
import gspread
import os
import json
import sys
from discord.ext import commands
from dotenv import load_dotenv
from gspread import service_account
from google.oauth2 import service_account

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_SHEET_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
ALLOWED_USER_IDS = [163199994919256064]

INQ_LEADERSHIP_SHEET_NAME = "Inquisitor Order"
INQ_LEADERSHIP_SHEET_ID = "1qZh4wRgSaN8FQXFLZOazSACESSVfWAdAmqOcB66DWDs"
INQ_PUBLIC_SHEET_ID = "1b6u92zn9pf_xJpxy_t4VYon7zvFVtiOEpYz9XefgatM"
INQ_PUBLIC_SHEET_NAME = "Public Roster"

testing = sys.argv[1]

if testing == "Y":
    CHANNEL_NAME = "inactivity-discussion-testing"
else:
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
        loa = row[18]
        if name != "" and name != "Name" and name != "dont delete":
            if loa != "ROA" and loa != "LOA":
                names.append(name)

    return names


@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')
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
    DiscordIDColumn = sheet.col_values(11)  # TODO change to use letters
    DaysSinceColumn = sheet.col_values(12)

    NonLoaNames = CheckLoa()

    OverNineDays = []
    NineDays = []
    EightDays = []
    SevenDays = []

    for name, DiscordId, DaysSince in zip(NameColumn, DiscordIDColumn, DaysSinceColumn):
        if name != "" and name != "Name" and name != "dont delete":
            if name not in NonLoaNames:
                continue

            try:
                if DaysSince.isdigit():
                    DaysSince = int(DaysSince)
                    if DaysSince > 9:
                        OverNineDays.append(f"<@{DiscordId}>")
                    elif DaysSince == 9:
                        NineDays.append(f"<@{DiscordId}>")
                    elif DaysSince == 8:
                        EightDays.append(f"<@{DiscordId}>")
                    elif DaysSince == 7:
                        SevenDays.append(f"<@{DiscordId}>")

            except TypeError as e:
                logging.error(f"Unable to convert DaysSince value for {name}: {e}")

    output = []

    if SevenDays:
        output.append(f"2 days: {' '.join(SevenDays)}")
    if EightDays:
        output.append(f"1 day: {' '.join(EightDays)}")
    if OverNineDays:
        output.append(f"Inactive: {' '.join(OverNineDays)}")

    if output:
        response = "\n".join(output)
        channel = discord.utils.get(bot.get_all_channels(), name=CHANNEL_NAME)
        if channel:
            message = f"\n{response}\n\nPlease participate in an event or training to update your activity, if there are any problems DM a member of the Inquisitorious\n"

            if NineDays:
                message += f"\n{' '.join(NineDays)} You will be removed if you do not come on for an event or training today"
            await channel.send(message)

        else:
            logging.error(f"Unable to find channel: {CHANNEL_NAME}")


bot.run(DISCORD_TOKEN)
