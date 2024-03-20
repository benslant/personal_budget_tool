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

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"

credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)

class CodeTransactions():

  def __init__(self) -> None:
    pass

  def code_transactions(self):
    console = Console()
    try:
      gc: Client = authorize(credentials)
      sheets_importer = SheetsTransactionImporter(gc)
      transaction_service = TransactionsService()

      result = sheets_importer.load_coded_transactions_from_spreadsheet(SAMPLE_SPREADSHEET_ID, "Code Here")
      grouped_by_payee = sheets_importer.group_transactions_by_payee(result)
      payees = [k for k,_ in grouped_by_payee.items()]
      cp = sheets_importer.consolidate_payees(payees)
      coding_history = sheets_importer.get_coding_history(grouped_by_payee)
      uncoded = sheets_importer.get_uncoded_transactions(result)
      coded = sheets_importer.code_transactions(uncoded, coding_history)
      remainder = sheets_importer.get_uncoded_transactions(uncoded)
      console.print(f"Total uncoded transactions: {len(uncoded)}")
      console.print(f"Successfully coded [{len(coded)}] transactions")
      console.print(f"Failed to code [{len(remainder)}] transactions")
      console.print(f"Success rate: [{len(coded)/len(uncoded)*100:.2f}%]")
    except HttpError as err:
      print(err)