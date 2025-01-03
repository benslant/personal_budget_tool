from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from load_transactions_from_csv import CSVTransactionImporter 
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from transactions_service import TransactionsService
from rich.console import Console
from rich.table import Table
from os import remove


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"

# credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)

class CleanupExports():

  def __init__(self) -> None:
    pass

  def remove_export_files_from_folder(self, folder_name: str):
    console = Console()
    csv_importer = CSVTransactionImporter()
    export_files = csv_importer.list_export_files_in_folder(folder_name)
    for file in export_files:
      console.print(f'Removing: {file}...')
      remove(file.__repr__())
      

