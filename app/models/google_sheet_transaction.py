from dataclasses import dataclass
from typing import List
from models import Transaction


@dataclass
class GoogleSheetTransaction(Transaction):
    worksheet_name: str = ''
    row: id = 0