from dataclasses import dataclass
from datetime import datetime
from typing import List
from models import Account, Transaction

@dataclass
class TransactionCSVFile():
    folder_name: str
    file_name: str
    export_date: datetime
    account: Account
    from_date: datetime
    to_date: datetime

    @staticmethod
    def create_filename_at_time(timestamp: datetime) -> str:
        return f'Export{timestamp.strftime('%Y')}{timestamp.strftime('%m')}{timestamp.strftime('%d')}{timestamp.strftime('%H')}{timestamp.strftime('%M')}{timestamp.strftime('%S')}.csv'
    
    @staticmethod
    def file_from_transaction_list(destination: str,
                                   account_label: str, 
                                   bank_code: str,
                                   branch: str,
                                   account: str,
                                   suffix: str,
                                   transactions: List[Transaction]):
        now = datetime.now()
        file_name = TransactionCSVFile.create_filename_at_time(now)
        from_date = transactions[0].date
        to_date = transactions[-1:][0].date
        lines: List[str] = []
        lines.append(f'Created date / time : {now.day} {now.month} {now.year} / {now.hour}:{now.minute}:{now.second}')
        lines.append(f'Bank {bank_code}; Branch {branch}; Account {account}-{suffix} ({account_label})')
        lines.append(f'From date {from_date.strftime("%Y%m%d")}')
        lines.append(f'To date {to_date.strftime("%Y%m%d")}')
        lines.append(f'Avail Bal : ? as of ?')
        lines.append(f'Ledger Balance : ? as of ?')
        lines.append('Date,Unique Id,Tran Type,Cheque Number,Payee,Memo,Amount')
        lines.append('')

        for transaction in transactions:
            lines.append(transaction.to_csv_line())

        with open(f'{destination}/{file_name}', 'w+') as csv_file:
            for line in lines:
                csv_file.write(f'{line}\n')