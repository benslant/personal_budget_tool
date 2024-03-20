from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
from itertools import groupby
from re import sub, search
from typing import Dict, List, Optional
from gspread import Client, Worksheet
from gspread.exceptions import SpreadsheetNotFound
from models import Transaction, TransactionType
from thefuzz import fuzz
from thefuzz import process

class SheetsTransactionImporter():

    def __init__(self,
                 google_sheets_client: Client) -> None:
        self.google_sheets_client = google_sheets_client

    def get_rows_from_worksheet(self, sheet_id: str, worksheet_name: str, start_from_row: int = 0) -> List[List]:
        sheet = self.google_sheets_client.open_by_key(sheet_id)
        work_sheet = sheet.worksheet(worksheet_name)
        rows = work_sheet.get_all_values()[start_from_row:]
        return rows
    
    def does_sheet_exist(self, sheet_id: str, worksheet_name: str) -> bool:
        result: bool = False
        try:
            sheet = self.google_sheets_client.open_by_key(sheet_id)
            self.google_sheets_client.open_by_key(sheet_id)
            a = sheet.worksheet(worksheet_name)
            result = True
        except SpreadsheetNotFound as e:
            result = False
        finally:
            return result
        
    def list_all_sheets(self, sheet_id: str) -> List[Worksheet]:
        sheet = self.google_sheets_client.open_by_key(sheet_id)
        result = sheet.worksheets()
        return result
        
    def create_sheet(self, sheet_id, worksheet_name: str) -> bool:
        sheet = self.google_sheets_client.open_by_key(sheet_id)
        sheet.add_worksheet(worksheet_name, rows="100", cols="20")

    def load_transactions_from_sheet(self, sheet_id: str, worksheet_name: str, start_from_row: int = 0) -> OrderedDict[int, Transaction]:
        rows = self.get_rows_from_worksheet(sheet_id, worksheet_name, start_from_row)
        for r in rows:
            try:
                Decimal(r[6])
            except Exception as e:
                pass

        result = OrderedDict({int(r[1]): Transaction(date=datetime.strptime(r[0], "%Y/%m/%d"),
                              unique_id=int(r[1]),
                              transaction_type=TransactionType.from_asb_csv_export_str(r[2]),
                              cheque_number=r[3],
                              payee=r[4],
                              memo=r[5],
                              amount=Decimal(r[6])) for r in rows})

        return result
    
    def add_transactions_to_sheet(self, sheet_id: str, worksheet_name: str, start_from_row: int, transactions: OrderedDict[int, Transaction]):
        if not self.does_sheet_exist(sheet_id, worksheet_name):
            self.create_sheet(sheet_id, worksheet_name)

        sheet = self.google_sheets_client.open_by_key(sheet_id)
        work_sheet = sheet.worksheet(worksheet_name)
        raw_transactions = [t.to_csv_list() for _, t in transactions.items()]
        new_rows = [['']]*len(raw_transactions)
        work_sheet.append_rows(new_rows)
        work_sheet.update(f'A{start_from_row + 1}', raw_transactions, value_input_option='USER_ENTERED')
    
    def get_last_row_in_transaction_sheet_based_on_transaction_list(self, transactions: OrderedDict[int, Transaction]) -> int:
        return len((transactions.keys())) + 4
    
    def load_coded_transactions_from_spreadsheet(self, sheet_id: str, worksheet_name: str) -> OrderedDict[int, Transaction]:
        result: OrderedDict[int, Transaction] = OrderedDict()
        rows = self.get_rows_from_worksheet(sheet_id, worksheet_name)
        
        for i, r in enumerate(rows[1:]):
            if not r[9] and not r[10]:
                amount = 0
            else:
                amount= Decimal(sub(r'[^\d.]', '', r[9])) if r[9] else Decimal(sub(r'[^\d.]', '', r[10]))
            if not r[5]: continue
            result[int(r[5])] = Transaction.build(date=datetime.strptime(r[0].strip(), "%A %d/%m/%Y"),
                                                  unique_id=int(r[5]),
                                                  transaction_type=TransactionType.from_asb_csv_export_str(r[6]),
                                                  cheque_number='',
                                                  payee=r[7],
                                                  memo=r[8],
                                                  amount=amount,
                                                  transaction_type_primary_code=r[11],
                                                  transaction_type_secondary_code=r[12],
                                                  transfer_account=r[3])

        return result
    
    def fuzzy_match(self):
        uber_group: Dict[str, List[str]] = {}
        keys = [k for k, r in result.items() if not r.transfer_account]
        for key in keys:
            for i, k in enumerate(keys):
                if k == key: continue
                ratio = fuzz.ratio(key, k)
                if ratio >= 95:
                    if key not in uber_group: uber_group[key] = []
                    uber_group[key].append(k)
                    keys.pop(i)

    def consolidate_payees(self, payees: List[str]) -> Dict[str, List[str]]:
        all_payees = [p for p in payees if p]
        result: Dict[str, List[str]] = {}
        matches: List[str] = []
        for i, payee in enumerate(all_payees):
            if not payee: continue        
            high_score = 0
            likely_match = ''
            likely_match_index = 0
            if payee not in matches:
                for k in matches:
                    ratio = fuzz.token_set_ratio(payee, k)
                    if k != payee and ratio > high_score and abs(len(k) - len(payee)) < 3:
                        high_score = ratio
                        likely_match = k
                if high_score < 95:
                    for j, p in enumerate(all_payees):
                        ratio = fuzz.token_set_ratio(payee, p)
                        if p != payee and ratio > high_score and abs(len(p) - len(payee)) < 3:
                            high_score = ratio
                            likely_match = p

                if high_score > 95 and likely_match not in result: 
                    result[likely_match] = []
                    result[likely_match].append(payee)
                else:
                    result[payee] = []
                matches = list(result.keys())
        consolidate_list = list(result.keys())
        reduction = len(payees) - len(consolidate_list)
        return consolidate_list

    def get_uncoded_transactions(self, transactions: OrderedDict[int, Transaction]) -> OrderedDict[int, Transaction]:
        return OrderedDict({k:v for k,v in transactions.items() if not v.transaction_type_primary_code})
    
    def get_coding_history(self, grouped_transactions: OrderedDict[str, OrderedDict[int, Transaction]]) -> Dict[str, str]:
        likely_codes: Dict[str, str] = {}

        for payee, transactions_to_payee in grouped_transactions.items():
            raw_transactions: List[Transaction] = [t for _, t in transactions_to_payee.items()]
            likely_code: str = ''
            highest_freq: int = 0
            sorted_raw_transactions = sorted(raw_transactions, key=lambda t: t.transaction_type_primary_code)
            for _, group in groupby(sorted_raw_transactions, key=lambda x: x.transaction_type_primary_code):
                list_group = list(group)
                freq = len(list_group)
                if freq > highest_freq: 
                    highest_freq = freq
                    likely_code = list_group[0].transaction_type_primary_code
            if likely_code and likely_code.lower() != "uncoded":
                likely_codes[payee] = likely_code
        return likely_codes

    def code_transactions(self, transactions: OrderedDict[int, Transaction], coding_history: Dict[str, str]) -> OrderedDict[int, Transaction]:
        result: OrderedDict[int, Transaction] = OrderedDict()
        for transaction_id, transaction in transactions.items():
            if not transaction.transaction_type_primary_code:
                if transaction.transaction_type in [TransactionType.transfer_in, TransactionType.transfer_out]:
                    result[transaction_id] = transactions[transaction_id]
                    result[transaction_id].transaction_type_primary_code = 'Excluded'
                    continue
                if transaction.payee in coding_history:
                    result[transaction_id] = transactions[transaction_id]
                    result[transaction_id].transaction_type_primary_code = coding_history[transaction.payee]

        return result 
    
    def group_transactions_by_payee(self, transactions: OrderedDict[int, Transaction]) -> OrderedDict[str, Dict[int, Transaction]]:
        result: OrderedDict[str, OrderedDict[int, Transaction]] = OrderedDict()
        raw_transactions: List[Transaction] = [v for k,v in transactions.items()]
        sorted_raw_transaction = sorted(raw_transactions, key=lambda t: t.payee)
        for payee, group in groupby(sorted_raw_transaction, key=lambda t: t.payee):
            transaction_group = list(group)
            result[payee] = OrderedDict({t.unique_id:t for t in transaction_group})

        return result