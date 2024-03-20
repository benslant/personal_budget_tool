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

class ImportTransactions():

  def __init__(self) -> None:
    pass

  def import_transactions(self, file_name: Optional[str], folder_name: Optional[str]):
    console = Console()
    try:
      gc: Client = authorize(credentials)
      csv_importer = CSVTransactionImporter()
      sheets_importer = SheetsTransactionImporter(gc)
      transaction_service = TransactionsService()

      if not file_name:
        if not folder_name:
          console.print('Error! You must specify either a filename or a folder name!')
          return
        exports_in_folder = csv_importer.list_export_files_in_folder(folder_name, True)
        sorted_by_account_number = sorted(exports_in_folder, key=lambda e: e.account.__repr__())
        grouped_by_account_number: Dict[str, List[TransactionCSVFile]] = {}
        for key, group in groupby(sorted_by_account_number, key=lambda e: e.account.__repr__()):
          grouped_by_account_number[key] = list(group)
        index: int = 0
        file_list: List[TransactionCSVFile] = []
        for account_number, transactions in grouped_by_account_number.items():
          console.print(f'{transactions[0].account.label} - {account_number}')
          for transaction in transactions:
            option = f'({index}) from: {transaction.from_date.strftime('%Y-%m-%d')} to: {transaction.to_date.strftime('%Y-%m-%d')} exported on: {transaction.export_date.strftime('%Y-%m-%d')} - \[{transaction.folder_name}/{transaction.file_name}]'
            console.print(option)
            file_list.append(transaction)
            index += 1
        selection = click.prompt("Select an import file", type=int)
        if selection < len(file_list):
          file_name = f'{file_list[selection].folder_name}/{file_list[selection].file_name}'
        else:
          console.print('Error! Invalid selection')
        
      account = csv_importer.get_account_from_file(file_name)
      sheet_name = f'{account.label} - {account}'
      if not sheets_importer.does_sheet_exist(SAMPLE_SPREADSHEET_ID, sheet_name):
        sheets_importer.create_sheet(SAMPLE_SPREADSHEET_ID, sheet_name)
      print(f'Processing transactions for account: {account} with label: {account.label}')
      csv_transactions = csv_importer.load_transactions_from_file(file_name)
      sheet_transactions = sheets_importer.load_transactions_from_sheet(SAMPLE_SPREADSHEET_ID, sheet_name, 4)
      last_row = sheets_importer.get_last_row_in_transaction_sheet_based_on_transaction_list(sheet_transactions)
      last_common_transaction_id =  transaction_service.find_intersection_of_lists(csv_transactions, sheet_transactions)
      unique_transactions = transaction_service.slice_transaction_list(last_common_transaction_id, csv_transactions)
      if len(unique_transactions) > 0:
          sheets_importer.add_transactions_to_sheet(SAMPLE_SPREADSHEET_ID, sheet_name,
                                                  sheets_importer.get_last_row_in_transaction_sheet_based_on_transaction_list(sheet_transactions),
                                                  unique_transactions)
      else:
        print("The spreadsheet is up to date!")

      result = sheets_importer.load_coded_transactions_from_spreadsheet(SAMPLE_SPREADSHEET_ID, "Code Here")
      grouped_by_payee = sheets_importer.group_transactions_by_payee(result)
      payees = [k for k,_ in grouped_by_payee.items()]
      cp = sheets_importer.consolidate_payees(payees)
      coding_history = sheets_importer.get_coding_history(grouped_by_payee)
      uncoded = sheets_importer.get_uncoded_transactions(result)
      coded = sheets_importer.code_transactions(uncoded, coding_history)
      remainder = sheets_importer.get_uncoded_transactions(uncoded)
      pass
    except HttpError as err:
      print(err)