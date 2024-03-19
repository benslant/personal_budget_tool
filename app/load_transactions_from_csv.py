from collections import OrderedDict
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from models import Transaction, TransactionType, Account, TransactionCSVFile
from os import listdir
from os.path import isfile, join
from re import compile


transaction_export_filename_pattern = compile('Export([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2}).csv')
pattern = 'Created date \/ time : ([0-9]{1,2}) (\w+) ([0-9]{4}) \/ ([0-9]{2}):([0-9]{2}):([0-9]{2})'
to_from_date_pattern = compile('\w+ date ([0-9]{4})([0-9]{2})([0-9]{2})')

class CSVTransactionImporter():

    def __init__(self) -> None:
        pass

    def get_account_from_file(self, file_name) -> Account:
        account: Account = None
        with open(file_name, mode='r') as transactions_file:
            for line in range(2):
                line_content = next(transactions_file)
                if line == 1:
                    account = Account.build(line_content)
                pass
        return account
    
    def date_time_from_import_file_line(self, date_str: str) -> Optional[datetime]:
        match = to_from_date_pattern.search(date_str)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return datetime(year, month, day)
        return None

    def get_date_span_from_file(self, file_name) -> Tuple[datetime, datetime]:
        from_date: datetime = None
        to_date: datetime = None
        with open(file_name, mode='r') as transactions_file:
            for line in range(6):
                line_content = next(transactions_file)
                if line == 2:
                    from_date = self.date_time_from_import_file_line(line_content)
                if line == 3:
                    to_date = self.date_time_from_import_file_line(line_content)
                    
                pass
        return (from_date, to_date)
    
    def list_export_files_in_folder(self, folder_name) -> List[TransactionCSVFile]:
        result: List[TransactionCSVFile] = []
        files = [f for f in listdir(folder_name) if isfile(join(folder_name, f))]
        for file in files:
            match = transaction_export_filename_pattern.search(file)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                hour = int(match.group(4))
                minutes = int(match.group(5))
                seconds = int(match.group(6))
                export_date = datetime(year, month, day, hour, minutes, seconds)
                account = self.get_account_from_file(f'{folder_name}/{file}')
                date_span = self.get_date_span_from_file(f'{folder_name}/{file}')
                result.append(TransactionCSVFile(folder_name,
                                                 file, 
                                                 export_date, 
                                                 account, 
                                                 date_span[0], 
                                                 date_span[1]))
        return result

    def load_raw_transactions_dict_from_file(self, file_name) -> Dict[str, str]:
        result: List[Dict[str, str]] = []
        with open(file_name, mode='r') as transactions_file:
            for line in range(6):
                next(transactions_file)
            reader = csv.DictReader(transactions_file)
            result = [r for r in reader]

        return result
    
    def load_transactions_from_file(self, file_name) -> OrderedDict[int, Transaction]:
        raw_transactions = self.load_raw_transactions_dict_from_file(file_name)
        
        if not raw_transactions: return {}

        result = OrderedDict({int(transaction['Unique Id']):Transaction.build(date=datetime.strptime(transaction['Date'], "%Y/%m/%d"),
                                      unique_id=int(transaction['Unique Id']),
                                      transaction_type=TransactionType.from_asb_csv_export_str(transaction['Tran Type']),
                                      cheque_number=transaction['Cheque Number'],
                                      payee=transaction['Payee'],
                                      memo=transaction['Memo'],
                                      amount=transaction['Amount']) for transaction in raw_transactions})

        return result
        