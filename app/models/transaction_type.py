from enum import Enum

class TransactionType(Enum):
    debit = 0
    transfer_in = 1
    transfer_out = 2
    loan_interest = 3
    load_principle = 4
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
                return TransactionType.direct_debit
            case "BILLPAY":
                return TransactionType.bill_payment
            case "D/C":
                return TransactionType.direct_credit
            case _:
                raise Exception(f'Unkown transaction type [{transaction_type}]')