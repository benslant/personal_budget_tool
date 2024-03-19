from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from load_transactions_from_csv import CSVTransactionImporter 
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from transactions_service import TransactionsService
from rich.console import Console
from rich.table import Table


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"

credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)

class ListAvailableExports():

  def __init__(self) -> None:
    pass

  def list_exports_in_directory(self, folder_name: str):
    console = Console()
    csv_importer = CSVTransactionImporter()
    export_files = csv_importer.list_export_files_in_folder(folder_name)
    table = Table(title="Export Files", show_lines=True)
    table.add_column("File Name")
    table.add_column("Account Name")
    table.add_column("Account Number")
    table.add_column("From")
    table.add_column("To")
    table.add_column("Exported On")
    sorted_files = sorted(export_files, key=lambda e: e.to_date, reverse=True)
    for file in sorted_files:
        table.add_row(f'{file.folder_name}/{file.file_name}',
                      file.account.label,
                      str(file.account),
                      file.from_date.strftime('%d-%m-%Y'),
                      file.to_date.strftime('%d-%m-%Y'),
                      file.export_date.strftime('%d-%m-%Y'))

    console.print(table)

