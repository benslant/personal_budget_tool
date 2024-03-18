import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from load_transactions_from_csv import CSVTransactionImporter 
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from transactions_service import TransactionsService

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"

credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)

def main():
  discoveryUrl ='https://sheets.googleapis.com/$discovery/rest?version=v4'
  try:
    gc: Client = authorize(credentials)
    csv_importer = CSVTransactionImporter()
    sheets_importer = SheetsTransactionImporter(gc)
    transaction_service = TransactionsService()

    account = csv_importer.get_account_from_file("/Users/ben.caldwell/Downloads/Export20240315100941.csv")
    print(f'Processing transactions for account: {account} with label: {account.label}')
    csv_transactions = csv_importer.load_transactions_from_file("/Users/ben.caldwell/Downloads/Export20240315100941.csv")
    sheet_transactions = sheets_importer.load_transactions_from_sheet(SAMPLE_SPREADSHEET_ID, "Add Chq Trans Here", 4)
    last_row = sheets_importer.get_last_row_in_transaction_sheet_based_on_transaction_list(sheet_transactions)
    last_common_transaction_id =  transaction_service.find_intersection_of_lists(csv_transactions, sheet_transactions)
    unique_transactions = transaction_service.slice_transaction_list(last_common_transaction_id, csv_transactions)
    if len(unique_transactions) > 0:
        sheets_importer.add_transactions_to_sheet(SAMPLE_SPREADSHEET_ID, "Add Chq Trans Here",
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

if __name__ == "__main__":
  main()

