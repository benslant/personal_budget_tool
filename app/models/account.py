from dataclasses import dataclass
from re import compile

pattern = compile("([0-9]{2}); Branch ([0-9]{4}); Account ([0-9]{7})-([0-9]{2}) \((.*)\)")

@dataclass
class Account():
    bank: int = 0
    branch: int = 0
    account: int = 0
    suffix: int = 0
    label: str = ''


    def build(asb_bank_export_field: str) -> 'Account':
        matches = pattern.search(asb_bank_export_field)
        if not matches: raise(f"Invalid ASB account string used - {asb_bank_export_field}")

        return Account(bank = matches.group(1),
                       branch = matches.group(2),
                       account = matches.group(3),
                       suffix = matches.group(4),
                       label= matches.group(5))
    
    def __repr__(self) -> str:
        return f'{self.bank}-{self.branch}-{self.account}-{self.suffix}'