from typing import Dict, List, OrderedDict, Set
from gspread import Client


class TransactionCodeService():

    def __init__(self, google_sheets_client: Client) -> None:
        self.google_sheets_client = google_sheets_client

    def get_transaction_codes(self, sheet_id: str) -> List[str]:
        sheet = self.google_sheets_client.open_by_key(sheet_id)
        self.google_sheets_client.open_by_key(sheet_id)
        work_sheet = sheet.worksheet('Transaction Types')
        rows = work_sheet.get_all_values()
        sorted_rows = sorted([r[0] for r in rows[1:]], key=lambda l: l)
        result = dict.fromkeys(sorted_rows)
        return list(result)