from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from models import TransactionType
from re import search, compile

pattern_card_number = compile("CARD ([0-9]{4})(.*)")
pattern_exchange_rate = compile("(.*)(at ([0-9]{1}\.[0-9]{4}))")
pattern_native_amount = compile("^([A-Z]{3}) ([0-9]+.[0-9]{2})(.*)")

@dataclass
class Transaction():
    date: datetime
    unique_id: int
    transaction_type: TransactionType
    cheque_number: str
    payee: str
    memo: str
    amount: Decimal
    account_id: str = ''
    transaction_type_primary_code: str = ''
    transaction_type_secondary_code: str = ''
    income_type: str = ''
    notes: str = ''
    transfer_account: str = ''
    card_number: Optional[int] = None
    exchange_rate: Decimal = Decimal(0)
    country_code: str = ''
    native_country_amount: Decimal = Decimal(0)
    raw_memo: str = ''

    def build(date: datetime,
              unique_id: int,
              transaction_type: TransactionType,
              cheque_number: str,
              payee: str,
              memo: str,
              amount: Decimal,
              account_id: str = '',
              transaction_type_primary_code: str ='',
              transaction_type_secondary_code: str ='',
              income_type: str = '',
              notes: str = '',
              transfer_account: str = '') -> 'Transaction':
        actual_payee: str = payee
        actual_memo: str = memo
        card: Optional[int] = None
        exchange_rate: Decimal = Decimal(0)
        country_code: str = ''
        native_country_amount: Decimal = Decimal(0)
        matches = pattern_card_number.search(memo)
        raw_memo = f'{memo} | {payee}'
        if matches:
            card = int(matches.group(1))
            memo = (matches.group(2))
            memo = memo.strip()
        matches = pattern_exchange_rate.search(memo)
        if matches:
            exchange_rate = Decimal(matches.group(3))
            memo = matches.group(1)
            memo = memo.strip()
        matches = pattern_native_amount.search(memo)
        if matches:
            country_code = matches.group(1)
            native_country_amount = Decimal(matches.group(2))
            memo = matches.group(3)
            memo = memo.strip()
        matches = pattern_exchange_rate.search(payee)
        if matches:
            exchange_rate = Decimal(matches.group(3))
            payee = matches.group(1)
            payee = payee.strip()
        matches = pattern_card_number.search(payee)
        if matches:
            card = int(matches.group(1))
            payee = (matches.group(2))
            payee = payee.strip()

        actual_memo = memo.strip()
        actual_payee = payee.strip()
        if transaction_type in [TransactionType.debit, TransactionType.credit]:
            actual_payee = actual_memo
            actual_memo = actual_payee

        return Transaction(date, 
                           unique_id, 
                           transaction_type, 
                           cheque_number, 
                           actual_payee, 
                           actual_memo, 
                           amount, 
                           account_id,
                           transaction_type_primary_code, 
                           transaction_type_secondary_code, 
                           income_type, 
                           notes, 
                           transfer_account,
                           card,
                           exchange_rate,
                           country_code,
                           native_country_amount,
                           raw_memo)
    
    def get_csv_headers() -> List[str]:
        return ['Date', 
                'Unique Id', 
                'Transaction Type', 
                'Cheque Number', 
                'Payee', 
                'Memo', 
                'Amount', 
                'Account Id',
                'Transaction Type Primary Code', 
                'Transaction Type Secondary Code', 
                'Income Type', 
                'Notes', 
                'Transfer Account',
                'Card',
                'Exchange Rate',
                'Country Code',
                'Native Country Amount',
                'Raw Memo']
    
    def to_csv_list(self) -> List[str]:
        return [self.date.strftime("%Y/%m/%d"), 
                self.unique_id, 
                TransactionType.to_asb_string(self.transaction_type), 
                self.cheque_number, 
                self.payee, 
                self.memo, 
                self.amount,
                self.account_id,
                self.transaction_type_primary_code,
                self.transaction_type_secondary_code,
                self.income_type,
                self.notes,
                self.transfer_account,
                self.card_number,
                str(self.exchange_rate),
                self.country_code,
                str(self.native_country_amount),
                self.raw_memo]
    
    def __repr__(self) -> str:
        pass