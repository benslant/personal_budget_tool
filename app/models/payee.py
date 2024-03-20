from dataclasses import dataclass
from decimal import Decimal
from typing import List
from models.transaction import Transaction


@dataclass
class Payee():
    name: str
    transactions: List[Transaction]

    def transaction_count(self) -> int:
        return len(self.transactions)
    
    def total_spend(self) -> Decimal:
        return sum(t.amount for t in self.transactions)