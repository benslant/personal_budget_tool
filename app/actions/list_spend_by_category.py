from itertools import groupby
from typing import Dict, List
from googleapiclient.errors import HttpError
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from models import TransactionType, Transaction
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from transactions_service import TransactionsService
from transaction_code_service import TransactionCodeService
from rich.console import Console
import click

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"

credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)

class ListByCategory():

  def __init__(self) -> None:
    pass

  def list_by_category(self):
    console = Console()
    try:
      gc: Client = authorize(credentials)
      sheets_importer = SheetsTransactionImporter(gc)

      google_transation_sheet = sheets_importer.load_worksheet_transactions(SAMPLE_SPREADSHEET_ID, "Code Here")
      raw_transactions = google_transation_sheet.get_raw_transactions()
      grouped = google_transation_sheet.transactions_grouped_by_category(raw_transactions)

      grouped_by_year_and_category: Dict[str, Dict[str, List[Transaction]]] = {}

      google_transation_sheet.group_by_year_and_week_and_category(raw_transactions)

      for category, transactions in grouped.items():
         g = google_transation_sheet.transactions_grouped_by_year(transactions)
         for year, yearly_transactions in g.items():
           if year not in grouped_by_year_and_category: grouped_by_year_and_category[year] = {}
           grouped_by_year_and_category[year][category] = yearly_transactions
         pass

      for year, category_transactions in grouped_by_year_and_category.items():
        console.print(f'Spend in {year}')
        for category, transactions in category_transactions.items():
          console.print(f'{year} {category}: ${sum(t.amount for t in transactions):,}')

      pass
    except HttpError as err:
      print(err)