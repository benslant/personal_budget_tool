from services.configuration_service import ConfigurationService
from typing import Dict, List
from googleapiclient.errors import HttpError
from models import Transaction
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from rich.console import Console


class ListByCategory():

  def __init__(self,
               sheets_importer: SheetsTransactionImporter,
               configuration: ConfigurationService) -> None:
    self.sheets_importer = sheets_importer
    self.configuration = configuration

  def list_by_category(self):
    console = Console()

    sheet = self.configuration.get_value_by_key('google_sheet')
    sheet_id = sheet['spreadsheet_id']
    try:
      google_transation_sheet = self.sheets_importer.load_worksheet_transactions(sheet_id, "Code Here")
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