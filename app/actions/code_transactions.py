from typing import List
from googleapiclient.errors import HttpError
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from transactions_service import TransactionsService
from rich.console import Console
import click
from services import ConfigurationService, TransactionCodeService


class CodeTransactions():

  def __init__(self,
               transaction_code_service: TransactionCodeService,
               sheets_importer: SheetsTransactionImporter,
               configuration: ConfigurationService) -> None:
    self.transaction_code_service = transaction_code_service
    self.sheets_importer = sheets_importer
    self.configuration = configuration

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

    sheet = self.configuration.get_value_by_key('google_sheet')
    sheet_id = sheet['spreadsheet_id']

    try:
      transaction_service = TransactionsService()
      codes = self.transaction_code_service.get_transaction_codes(sheet_id)

      google_transation_sheet = self.sheets_importer.load_worksheet_transactions(sheet_id, "Code Here")

      result = google_transation_sheet.transactions
      unique_payees = transaction_service.group_payees_by_name_similarity(result)
      grouped_by_payee = self.sheets_importer.group_transactions_by_payee(result)
      coding_history = self.sheets_importer.get_coding_history(grouped_by_payee)
      uncoded = self.sheets_importer.get_uncoded_transactions(result)
      coded = self.sheets_importer.code_transactions(uncoded, coding_history)
      remainder = self.sheets_importer.get_uncoded_transactions(uncoded)
      console.print(f"Total uncoded transactions: {len(uncoded)}")
      console.print(f"Successfully coded [{len(coded)}] transactions")
      console.print(f"Failed to code [{len(remainder)}] transactions")
      console.print(f"Success rate: [{len(coded)/len(uncoded)*100:.2f}%]")

      unique_payees = transaction_service.get_unqiue_payees_from_transactions(remainder)
      console.print(f'There are [{len(unique_payees)}] unique uncodable payees!')

      worksheet = self.sheets_importer.get_worksheet(sheet_id, "Code Here")

      with click.progressbar(length=len(coded), label='Autocoding transactions that match previous patterns...') as bar: 
        for _, transaction in coded.items():
          bar.label = f'Autocoding transactions that match previous patterns: Setting [{transaction.payee}] on [{transaction.date.strftime('%d-%m-&Y')}] as -> [{transaction.transaction_type_primary_code}]'
          self.sheets_importer.write_row_to_sheet(worksheet, transaction.row, transaction.transaction_type_primary_code)
          bar.update(1)

      for code, transaction in remainder.items():
        console.print(f'{transaction.date.strftime('%d-%m-%Y')} | row-{transaction.row} | {transaction.transaction_id} | {transaction.memo} | {transaction.payee} | ${transaction.amount}\n\n')
        selected = self.select_transaction_code_options(codes, console)
        if selected > len(codes) - 1:
          continue
        transaction.transaction_type_primary_code = codes[selected]
        self.sheets_importer.write_row_to_sheet(worksheet, transaction.row, transaction.transaction_type_primary_code)

    except HttpError as err:
      print(err)