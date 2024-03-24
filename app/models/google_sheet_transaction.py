from dataclasses import dataclass
from typing import List
from models import Transaction


@dataclass
class GoogleSheetTransaction():
    worksheet_name: str
    row: id
    transaction: Transaction
