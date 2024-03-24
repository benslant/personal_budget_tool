from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from transactions_service import TransactionsService
from rich.console import Console
from thefuzz import fuzz


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"
# non_word_pattern = compile('([A-Za-z]+[\d]+[\w]*|[\d]+[A-Za-z]+[\w]*)')
credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)

class GroupPayees():

  def __init__(self) -> None:
    pass

  def group(self):
    console = Console()

    gc: Client = authorize(credentials)
    sheets_importer = SheetsTransactionImporter(gc)
    transaction_service = TransactionsService()

    result = sheets_importer.load_coded_transactions_from_spreadsheet(SAMPLE_SPREADSHEET_ID, "Code Here")
    unique_payees = transaction_service.get_unqiue_payees_from_transactions(result)
    console.print(f'There are [{len(unique_payees)}] unqiue payees!')
    aliases = transaction_service.group_payees_by_name_similarity(unique_payees)

    for alias, alternates in aliases.items():
      console.print(f'{alias}')

    console.print(f"{len(aliases.keys())} after consolidation")    