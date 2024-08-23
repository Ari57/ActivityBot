import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

def GetSheet():
    CredsPath = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"] # TODO double check this

    creds = ServiceAccountCredentials.from_json_keyfile_name(CredsPath, scope)
    client = gspread.authorize(creds)

    SpreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet = client.open_by_key(SpreadsheetId).sheet1
    return sheet

def ReadCell(cell):
    sheet = GetSheet()
    return sheet.acell(cell).value