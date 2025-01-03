from datetime import datetime
from decimal import Decimal
from typing import List
from googleapiclient.errors import HttpError
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from models.transaction_type import TransactionType
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from rich.console import Console

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"


class GetSpendAtPayee():

  def __init__(self) -> None:
    pass

  def list_spend_at_payee(self):
    console = Console()
    try:
      credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)
      gc: Client = authorize(credentials)
      sheets_importer = SheetsTransactionImporter(gc)

      google_transation_sheet = sheets_importer.load_worksheet_transactions(SAMPLE_SPREADSHEET_ID, "Code Here")
      yearly_transactions = google_transation_sheet.group_by_year_and_payee(google_transation_sheet.get_raw_transactions())
      rows: List[str] = []
      for year, payees in yearly_transactions.items():
        rows.append(f'Payee spend for {year}')
        for payee, transactions in payees.items():
          rows.append(f'\t{payee} - ${sum(t.amount for t in transactions):,}')

      for row in rows:
          console.print(row)
      pass
    except HttpError as err:
      print(err)
