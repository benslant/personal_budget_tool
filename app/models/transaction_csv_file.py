from dataclasses import dataclass
from datetime import datetime
from models import Account

@dataclass
class TransactionCSVFile():
    folder_name: str
    file_name: str
    export_date: datetime
    account: Account
    from_date: datetime
    to_date: datetime
