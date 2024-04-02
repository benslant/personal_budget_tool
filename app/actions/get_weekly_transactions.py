from datetime import datetime
from decimal import Decimal
from typing import List
from googleapiclient.errors import HttpError
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from models.transaction_type import TransactionType
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from rich.console import Console

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"

credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)

class GetWeeklyTransactions():

  def __init__(self) -> None:
    pass

  def list_weekly_transactions(self, year: int, relative_week: int):
    console = Console()
    try:
      gc: Client = authorize(credentials)
      sheets_importer = SheetsTransactionImporter(gc)
      current_date = datetime.now()
      current_week = current_date.isocalendar().week
      if not year or year == 0:
        year = current_date.year
      week = current_week
      if not relative_week:
        week == current_week
      elif relative_week > 52:
        week = 52
      elif relative_week <= 0:
        week = current_week + relative_week

      google_transation_sheet = sheets_importer.load_worksheet_transactions(SAMPLE_SPREADSHEET_ID, "Code Here")
      weekly_transactions = google_transation_sheet.get_raw_transactions_for_week_of_year(week, year)
      grouped = google_transation_sheet.group_by_year_and_week_and_category(weekly_transactions)

      for year, weeks in grouped.items():
        for week, categories in weeks.items():
            rows: List[str] = []
            total_spend: Decimal = 0
            category_spend: Decimal = 0

            for category, transactions in categories.items():
                filtered_transactions = [t for t in transactions if t.transaction_type_primary_code not in ['Excluded']]
                category_spend = sum(t.amount for t in filtered_transactions)
                total_spend += category_spend
                rows.append(f'{category} - ${category_spend:,}')
                for t in filtered_transactions:
                    rows.append(f'\t{t.payee} - ${t.amount:,}')
            console.print(f'Spend in week {week} of {year} [Total: ${total_spend:,}]')
            for row in rows:
                console.print(row)
      pass
    except HttpError as err:
      print(err)