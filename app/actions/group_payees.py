from dataclasses import dataclass
from itertools import groupby
from typing import Dict, List, Tuple
from googleapiclient.errors import HttpError
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials
from models import TransactionType
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from transactions_service import TransactionsService
from rich.console import Console
from thefuzz import fuzz
from re import compile


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "12Act5Oi7BwzzeurYbKmnh-2JrpdPztVjtY0z9AUGaGY"
non_word_pattern = compile('([A-Za-z]+[\d]+[\w]*|[\d]+[A-Za-z]+[\w]*)')
credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)

@dataclass
class AliasMatch():
   matches_found: bool
   is_an_existing_alias: bool
   matches: List[Tuple[str, int]]

class GroupPayees():

  def __init__(self) -> None:
    pass

  def group(self):
    console = Console()

    gc: Client = authorize(credentials)
    sheets_importer = SheetsTransactionImporter(gc)

    result = sheets_importer.load_coded_transactions_from_spreadsheet(SAMPLE_SPREADSHEET_ID, "Code Here")
    unique_payees = sheets_importer.get_unqiue_payees_from_transactions(result)
    sorted_payees = sorted(unique_payees, key=lambda p: p.name, reverse=True)
    console.print(f'There are [{len(unique_payees)}] unqiue payees!')
    names = [s.name for s in sorted_payees]
    stripped_names = []
    for name in names:
        sn = non_word_pattern.sub('', name)
        stripped_names.append((name, sn))
    aliases: Dict[str, List[str]] = {}
    for payee in stripped_names:
      result = self.get_close_payee_matches(payee, stripped_names, aliases)
      if not result.matches_found: 
          if payee[0] not in aliases and not result.is_an_existing_alias: aliases[payee[0]] = []
          continue
      if payee[0] not in aliases: aliases[payee[0]] = []
      aliases[payee[0]].extend(result.matches)
    pass

    console.print(f"{len(aliases.keys())} after consolidation")

  def get_close_payee_matches(self, payee: str, payees: List[Tuple[str, str]], aliases: Dict[str, List[str]]) -> AliasMatch:
        result: AliasMatch = AliasMatch(False, False, [])
        all_aliases = [item for _, item in aliases.items()]
        flat_aliases = [item[0] for row in all_aliases for item in row]
        if payee[0] in aliases or payee[0] in flat_aliases:
           result.is_an_existing_alias = True
           return result
        
        for p in payees:
            if not p[0] or p[0] == payee[0]: 
               continue
            ratio = fuzz.ratio(payee[1].lower(), p[1].lower())
            if ratio > 88:
               result.matches.append((p[0], ratio))
        if len(result.matches) > 0:
           result.matches_found = True
        return result
                    