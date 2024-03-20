from enum import Enum

class TransactionType(Enum):
    debit = 0
    transfer_in = 1
    transfer_out = 2
    loan_interest = 3
    loan_principle = 4
    eftpos = 5
    eftpos_payment = 6
    bank_fee = 7
    interest = 8
    automatic_payment = 9
    direct_debit = 10
    credit = 11
    bill_payment = 12
    direct_credit = 13

    @staticmethod
    def to_asb_string(transaction_type: 'TransactionType') -> str:
        match transaction_type:
            case TransactionType.debit:
                return "DEBIT"
            case TransactionType.transfer_in:
                return "TFR IN"
            case TransactionType.transfer_out:
                return "TFR OUT"
            case TransactionType.loan_interest:
                return "LOAN INT"
            case TransactionType.loan_principle:
                return "LOAN PRIN"
            case TransactionType.eftpos:
                return "EFTPOS"
            case TransactionType.eftpos_payment:
                return "EFTPOSP"
            case TransactionType.bank_fee:
                return "BANK FEE"
            case TransactionType.interest:
                return "INT"
            case TransactionType.automatic_payment:
                return "A/P"
            case TransactionType.direct_debit:
                return "D/D"
            case TransactionType.credit: 
                return "CREDIT"
            case TransactionType.bill_payment:
                return "BILLPAY"
            case TransactionType.direct_credit:
                return "D/C"
            case _:
                raise Exception(f'Unkown transaction type [{transaction_type}]')

    @staticmethod
    def from_asb_csv_export_str(transaction_type: str) -> 'TransactionType':
        match transaction_type:
            case "DEBIT":
                return TransactionType.debit
            case "TFR IN":
                return TransactionType.transfer_in
            case "TFR OUT":
                return TransactionType.transfer_out
            case "LOAN INT":
                return TransactionType.loan_interest
            case "LOAN PRIN":
                return TransactionType.load_principle
            case "EFTPOS":
                return TransactionType.eftpos
            case "EFTPOSP":
                return TransactionType.eftpos_payment
            case "BANK FEE":
                return TransactionType.bank_fee
            case "INT":
                return TransactionType.interest
            case "A/P":
                return TransactionType.automatic_payment
            case "D/D":
                return TransactionType.direct_debit
            case "CREDIT":
                return TransactionType.credit
            case "BILLPAY":
                return TransactionType.bill_payment
            case "D/C":
                return TransactionType.direct_credit
            case _:
                raise Exception(f'Unkown transaction type [{transaction_type}]')