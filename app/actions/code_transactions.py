from itertools import groupby
from typing import List
from googleapiclient.errors import HttpError
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from models import TransactionType
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from transactions_service import TransactionsService
from transaction_code_service import TransactionCodeService
from rich.console import Console
import click

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"

credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)

class CodeTransactions():

  def __init__(self) -> None:
    pass

  def select_transaction_code_options(self, codes: List[str], console):
    length = len(codes)
    spacing = 5
    for index in range(0, len(codes), spacing):
      end = index + spacing if index + spacing < length else length
      a = [f'({c[0]}) {c[1]}' for c in list(zip(range(index, end), codes[index:end]))]
      console.print(' | '.join(a))

    selection = click.prompt("Select a code", type=int)
    return selection

  def code_transactions(self):
    console = Console()
    try:
      gc: Client = authorize(credentials)
      sheets_importer = SheetsTransactionImporter(gc)
      transaction_service = TransactionsService()
      code_service = TransactionCodeService(gc)

      codes = code_service.get_transaction_codes(SAMPLE_SPREADSHEET_ID)

      # sheets_importer.load_worksheet_transactions(SAMPLE_SPREADSHEET_ID, "Code Here", 1)

      google_transation_sheet = sheets_importer.load_worksheet_transactions(SAMPLE_SPREADSHEET_ID, "Code Here")

      result = google_transation_sheet.transactions
      unique_payees = transaction_service.group_payees_by_name_similarity(result)
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

      unique_payees = transaction_service.get_unqiue_payees_from_transactions(remainder)
      console.print(f'There are [{len(unique_payees)}] unique uncodable payees!')

      worksheet = sheets_importer.get_worksheet(SAMPLE_SPREADSHEET_ID, "Code Here")

      # a = google_transation_sheet.get_row_by_transaction_id(2022061303)
      b = google_transation_sheet.get_transaction_by_row(923)
      c = google_transation_sheet.get_transaction_by_row(1156)

      with click.progressbar(length=len(coded), label='Autocoding transactions that match previous patterns...') as bar: 
        for _, transaction in coded.items():
          bar.label = f'Autocoding transactions that match previous patterns: Setting [{transaction.payee}] on [{transaction.date.strftime('%d-%m-&Y')}] as -> [{transaction.transaction_type_primary_code}]'
          sheets_importer.write_row_to_sheet(worksheet, transaction.row, transaction.transaction_type_primary_code)
          bar.update(1)

      for code, transaction in remainder.items():
        console.print(f'{transaction.date.strftime('%d-%m-%Y')} | row-{transaction.row} | {transaction.transaction_id} | {transaction.memo} | {transaction.payee} | ${transaction.amount}\n\n')
        selected = self.select_transaction_code_options(codes, console)
        if selected > len(codes) - 1:
          continue
        transaction.transaction_type_primary_code = codes[selected]
        sheets_importer.write_row_to_sheet(worksheet, transaction.row, transaction.transaction_type_primary_code)

    except HttpError as err:
      print(err)