from dataclasses import dataclass, field
from datetime import datetime
from itertools import groupby
from typing import Dict, List, OrderedDict
from models import GoogleSheetTransaction, Transaction
from dateutil import relativedelta


@dataclass
class GoogleTransactionWorksheet():
    worksheet_name: str
    transactions: Dict[int, GoogleSheetTransaction] = field(default_factory=dict)

    def add_row(self, row_id: int, transaction: Transaction):
        self.transactions[transaction.unique_id()] = GoogleSheetTransaction(worksheet_name=self.worksheet_name, 
                                                           row=row_id, 
                                                           **transaction.__dict__)

    def get_row_by_transaction_id(self, transaction_id: int) -> int:
        return self.transactions[transaction_id]
    
    def get_transaction_by_row(self, row: int) -> int:
        transaction = next((t for id, t in self.transactions.items() if t.row == row), None)
        return transaction
    
    def get_raw_transactions(self) -> List[GoogleSheetTransaction]:
        return [t for _, t in self.transactions.items()]
    
    def get_raw_transactions_between_dates(self, start_date: datetime, end_date: datetime) -> List[GoogleSheetTransaction]:
        return [t for _, t in self.transactions.items() if t.date >= start_date and t.date <= end_date]
    
    def week_of_year_to_datetime(self, week_number: int, year: int, day: int) -> datetime:
        d = datetime.strptime(f'{year}-W{week_number}-{day}', "%Y-W%W-%w")
        return d

    def get_raw_transactions_for_week_of_year(self, week: int, year: int) -> List[Transaction]:
        start_date = self.week_of_year_to_datetime(week, year, 1)
        end_date = start_date + relativedelta.relativedelta(days=6)
        return self.get_raw_transactions_between_dates(start_date, end_date)
    
    def transactions_grouped_by_category(self, transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
        result: Dict[str, List[Transaction]] = {}
        sorted_by_category = sorted(transactions, key=lambda t: t.transaction_type_primary_code)

        for k, v in groupby(sorted_by_category, key=lambda t: t.transaction_type_primary_code):
            result[k] = list(v)

        return result
    
    def transactions_grouped_by_year(self, transactions: List[Transaction]) -> Dict[str, Transaction]:
        result: Dict[str, List[Transaction]] = {}
        sorted_by_date = sorted(transactions, key=lambda t: t.date)
        for k, v in groupby(sorted_by_date, key=lambda t: t.date.year):
            result[k] = list(v)

        return result
    
    def transactions_grouped_by_week(self, transactions: List[Transaction]) -> Dict[str, Transaction]:
        result: Dict[str, List[Transaction]] = {}
        sorted_by_date = sorted(transactions, key=lambda t: t.date)
        for k, v in groupby(sorted_by_date, key=lambda t: t.date.isocalendar().week):
            result[k] = list(v)

        return result
    
    def group_by_year_and_category(self, transactions: List[Transaction]) -> Dict[str, Dict[str, List[Transaction]]]:
        # for category, transactions in grouped.items():
            # g = google_transation_sheet.transactions_grouped_by_year(transactions)
            # for year, yearly_transactions in g.items():
            # if year not in grouped_by_year_and_category: grouped_by_year_and_category[year] = {}
            # grouped_by_year_and_category[year][category] = yearly_transactions
        pass

    def transactions_grouped_by_payee(self, transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
        result: Dict[str, List[Transaction]] = {}
        sorted_by_payee = sorted(transactions, key=lambda t: t.payee)

        for k, v in groupby(sorted_by_payee, key=lambda t: t.payee):
            result[k] = list(v)

        return result

    def group_by_year_and_payee(self, transactions: List[Transaction]) -> Dict[str, Dict[str, List[Transaction]]]:
        result: Dict[str, Dict[str, List[Transaction]]] = {}
        grouped_by_year = self.transactions_grouped_by_year(transactions)
        for year, yearly_transactions in grouped_by_year.items():
            grouped_by_payee = self.transactions_grouped_by_payee(yearly_transactions)
            for payee, payee_transactions in grouped_by_payee.items():
                if year not in result: result[year] = {}
                result[year][payee] = payee_transactions
        return result
    
    def group_by_year_and_week_and_category(self, transactions: List[Transaction]) -> Dict[str, Dict[str, Dict[str, List[Transaction]]]]:
        result: Dict[str, Dict[str, Dict[str, Transaction]]] = OrderedDict()
        yt = self.transactions_grouped_by_year(transactions)
        for year, grouped_yearly_transactions in yt.items():
            if year not in result: result[year] = OrderedDict()
            grouped_weekly_transactions = self.transactions_grouped_by_week(grouped_yearly_transactions)
            for week, weekly_transactions in grouped_weekly_transactions.items():
                if week not in result[year]: result[year][week] = OrderedDict()
                grouped_category_transactions = self.transactions_grouped_by_category(weekly_transactions)
                for category, transaction in grouped_category_transactions.items():
                    if category not in result[year][week]: result[year][week][category] = []
                    result[year][week][category].extend(transaction)
        return result

            

