import discord
import gspread
import os
from discord.ext import commands
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_SHEET_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
INQ_LEADERSHIP_SHEET_NAME = "Inquisitor Order"
INQ_LEADERSHIP_SHEET_ID = "1QMduATDD2o0XG8P3gqMN7kVtPIpCGH_UEq3sgkwbAb8"

INQ_PUBLIC_SHEET_ID = "15Ae2gh1rHMZx6WAm0tvCGqNHvYdtWjPl6rrQEpiDKB8"
INQ_PUBLIC_SHEET_NAME = "Public Roster"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def GetGoogleSheet(spreadsheet):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEET_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    if spreadsheet == "leadership":
        sheet = client.open_by_key(INQ_LEADERSHIP_SHEET_ID).worksheet(INQ_LEADERSHIP_SHEET_NAME)
        return sheet
    elif spreadsheet == "public":
        sheet = client.open_by_key(INQ_PUBLIC_SHEET_ID).worksheet(INQ_PUBLIC_SHEET_NAME)
        return sheet

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

@bot.command(name="readcell")
async def read_cell(ctx):
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
                elif DaysSince >= 8:
                    output.append(f"1 day: <@{DiscordId}>")
                elif DaysSince >= 7:
                    output.append(f"2 days: <@{DiscordId}>")

            except TypeError as e:
                print(f"Unable to convert DaysSince value for Name: {name}")
                print(e) # TODO add logging

    if output:
        response = "\n".join(output)
        await ctx.send("\nIf there are any problems please dm a member of the inquisitorious!")
        await ctx.send(f"\n{response}")

bot.run(DISCORD_TOKEN)