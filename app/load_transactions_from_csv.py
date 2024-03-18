from collections import OrderedDict
import csv
from datetime import datetime
from typing import Dict, List
from models import Transaction, TransactionType, Account


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
        