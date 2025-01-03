from itertools import groupby
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from models.transaction_csv_file import TransactionCSVFile
from load_transactions_from_csv import CSVTransactionImporter 
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from transactions_service import TransactionsService
import rich_click as click
from rich.console import Console
from re import compile

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"

transaction_sheet_pattern = compile('([\\w+ ]+) - ([0-9]{2})-([0-9]{4})-([0-9]{7})-([0-9]{2})')

class DumpSheetToCSV():

  def __init__(self) -> None:
    pass

  def request_account_number_selection(self, importer: SheetsTransactionImporter):
    console = Console()
    sheets = importer.list_all_sheets(SAMPLE_SPREADSHEET_ID)
    transaction_sheets: List[str] = []
    for sheet in sheets:
      matches = transaction_sheet_pattern.search(sheet.title)
      if matches:
        transaction_sheets.append(sheet.title)

    for index, sheet in enumerate(transaction_sheets):
        option = f'({index}) {sheet}'
        console.print(option)

    while True:
      selection = click.prompt("Select sheet to dump", type=int)
      if selection < len(transaction_sheets):
        return transaction_sheets[selection]
      

  def to_csv(self, destination: str, account_number: str = ''):
    console = Console()

    if not destination:
      console.print('Error! No destination directory provided.')
      return
    try:
      credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)
      gc: Client = authorize(credentials)
      sheets_importer = SheetsTransactionImporter(gc)
      transaction_service = TransactionsService()

      sheet_name = ''

      if not account_number:
        sheet_name = self.request_account_number_selection(sheets_importer)

      if not sheet_name:
        console.print('Error! No sheet name provided')
        return

      matches =transaction_sheet_pattern.search(sheet_name)
      account_label = matches.group(1)
      bank_code = matches.group(2)
      branch = matches.group(3)
      account = matches.group(4)
      suffix = matches.group(5)

      result = sheets_importer.load_transactions_from_sheet(SAMPLE_SPREADSHEET_ID, sheet_name, 1)
      csv_file_name = TransactionCSVFile.file_from_transaction_list(destination, account_label, bank_code, branch, account, suffix, [v for _, v in result.items()])
    except HttpError as err:
      print(err)
