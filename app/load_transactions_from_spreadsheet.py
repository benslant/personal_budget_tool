from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
from itertools import groupby
from re import sub, search
from typing import Dict, List, Optional
from gspread import Client, Worksheet
from gspread.exceptions import SpreadsheetNotFound
from models import Transaction, TransactionType, Payee, GoogleSheetTransaction, GoogleTransactionWorksheet
from thefuzz import fuzz
from thefuzz import process

class SheetsTransactionImporter():

    def __init__(self,
                 google_sheets_client: Client) -> None:
        self.google_sheets_client = google_sheets_client

    def get_worksheet(self, sheet_id: str, worksheet_name: str):
        sheet = self.google_sheets_client.open_by_key(sheet_id)
        return sheet.worksheet(worksheet_name)

    def get_rows_from_worksheet(self, sheet_id: str, worksheet_name: str, start_from_row: int = 0) -> List[List]:
        work_sheet = self.get_worksheet(sheet_id, worksheet_name)
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

    def write_row_to_sheet(self, worksheet, row: int, value: str):
        try:
            cell = worksheet.acell(f'N{row}')
            worksheet.update_cell(cell.row, cell.col, value)
        except Exception as e:
            pass


    def load_transactions_from_sheet(self, sheet_id: str, worksheet_name: str, account_number: str, start_from_row: int = 0) -> OrderedDict[int, Transaction]:
        rows = self.get_rows_from_worksheet(sheet_id, worksheet_name, start_from_row)

        try:
            result = OrderedDict({int(r[3]): Transaction(date=datetime.strptime(r[0], "%Y/%m/%d"),
                                transaction_id=r[3],
                                transaction_type=TransactionType.from_asb_csv_export_str(r[4]),
                                cheque_number=r[5],
                                payee=r[6],
                                memo=r[7],
                                amount=Decimal(r[8]),
                                account_number=account_number) for r in rows if r}) if rows else OrderedDict()
        except Exception as e:
            raise Exception(f'Failed to process transaction! {e.args}')

        return result
    
    def load_worksheet_transactions(self, sheet_id: str, worksheet_name: str) -> GoogleTransactionWorksheet:
        start_row: int = 1
        row_index: int = start_row + 1
        result: GoogleTransactionWorksheet = GoogleTransactionWorksheet(worksheet_name, {})
        raw_transactions = self.load_coded_transactions_from_spreadsheet(sheet_id, worksheet_name, 1)
        for _, transaction in raw_transactions.items():
            result.add_row(row_index, transaction)
            row_index += 1
        return result
            
    def add_transactions_to_sheet(self, sheet_id: str, worksheet_name: str, start_from_row: int, transactions: OrderedDict[int, Transaction]):
        if not self.does_sheet_exist(sheet_id, worksheet_name):
            self.create_sheet(sheet_id, worksheet_name)

        sheet = self.google_sheets_client.open_by_key(sheet_id)
        work_sheet = sheet.worksheet(worksheet_name)
        raw_transactions = [t.to_csv_list_account_local_id() for _, t in transactions.items()]
        new_rows = [['']]*(len(raw_transactions)+2)
        work_sheet.append_rows(new_rows)
        work_sheet.update(f'A{start_from_row + 1}', raw_transactions, value_input_option='USER_ENTERED')
    
    def get_last_row_in_transaction_sheet_based_on_transaction_list(self, transactions: OrderedDict[int, Transaction]) -> int:
        return len(transactions.keys()) + 1
    
    def load_coded_transactions_from_spreadsheet(self, sheet_id: str, worksheet_name: str, start_row: int = 1) -> OrderedDict[int, Transaction]:
        result: OrderedDict[int, Transaction] = OrderedDict()
        rows = self.get_rows_from_worksheet(sheet_id, worksheet_name, start_row)
        
        for _, r in enumerate(rows):
            if not r[11] and not r[12]:
                amount = 0
            else:
                amount= Decimal(sub(r'[^\d.]', '', r[11])) if r[11] else Decimal(sub(r'[^\d.]', '', r[12]))
            if not r[5]: 
                continue
            result[r[5]] = Transaction.build(date=datetime.strptime(r[0].strip(), "%A %d/%m/%Y"),
                                                  transaction_id=r[6],
                                                  transaction_type=TransactionType.from_asb_csv_export_str(r[8]),
                                                  cheque_number='',
                                                  payee=r[9],
                                                  memo=r[9],
                                                  amount=amount,
                                                  transaction_type_primary_code=r[13],
                                                  transaction_type_secondary_code=r[14],
                                                  transfer_account=r[3],
                                                  account_number=r[7])

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
            result[payee] = OrderedDict({t.transaction_id:t for t in transaction_group})

        return result