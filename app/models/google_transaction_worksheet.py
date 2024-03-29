from dataclasses import dataclass, field
from typing import Dict, List
from models import GoogleSheetTransaction, Transaction


@dataclass
class GoogleTransactionWorksheet():
    worksheet_name: str
    transactions: Dict[int, GoogleSheetTransaction] = field(default_factory=dict)

    def add_row(self, row_id: int, transaction: Transaction):
        self.transactions[transaction.transaction_id] = GoogleSheetTransaction(worksheet_name=self.worksheet_name, 
                                                           row=row_id, 
                                                           transaction_id=transaction.transaction_id,
                                                           **transaction.__dict__)

    def get_row_by_transaction_id(self, transaction_id: int) -> int:
        return self.transactions[transaction_id]
    
    def get_transaction_by_row(self, row: int) -> int:
        transaction = next((t for id, t in self.transactions.items() if t.row == row), None)
        return transaction
