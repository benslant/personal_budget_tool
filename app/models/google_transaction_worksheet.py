from dataclasses import dataclass
from typing import Dict, List
from models import GoogleSheetTransaction


@dataclass
class GoogleTransactionWorksheet():
    worksheet_name: str
    transactions: Dict[int, GoogleSheetTransaction]

    def get_row_by_transaction_id(self, transaction_id: int) -> int:
        return self.transactions[transaction_id]
