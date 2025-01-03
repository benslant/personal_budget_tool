from itertools import groupby
from typing import Dict, List, Tuple
from collections import OrderedDict
from models.transaction_type import TransactionType
from models import Transaction, AliasMatch, Payee
from thefuzz import fuzz
from re import compile

non_word_pattern = compile('([A-Za-z]+[\\d]+[\\w]*|[\\d]+[A-Za-z]+[\\w]*)')

class TransactionsService():

    def __init__(self) -> None:
        pass

    def merge_transaction_lists(self, 
                                last_common_transaction_id: int, 
                                list_one: List[Transaction], 
                                list_two: List[Transaction]) -> List[Transaction]:
        pass

    def slice_transaction_list(self, 
                               starting_transaction_id: int, 
                               transactions: OrderedDict[int, Transaction]) -> OrderedDict[int, Transaction]:
        result = OrderedDict({k:v for k,v in transactions.items() if k > starting_transaction_id})
        return result

    def find_intersection_of_lists(self, list_one: OrderedDict[int, Transaction], list_two: OrderedDict[int, Transaction]) -> int:
        set_one = set(list_one)
        set_two = set(list_two)

        intersection = sorted(list(set_one.intersection(set_two)))
        last_common_unique_id = list(intersection)[-1:][0] if len(intersection) > 0 else 0
        
        return int(last_common_unique_id)

    def get_close_payee_matches(self, payee: str, payees: List[Tuple[str, str]], aliases: Dict[str, List[str]]) -> AliasMatch:
        result: AliasMatch = AliasMatch(False, False, [])
        all_aliases = [item for _, item in aliases.items()]
        flat_aliases = [item[0] for row in all_aliases for item in row]
        if payee[0] in aliases or payee[0] in flat_aliases:
           result.is_an_existing_alias = True
           return result
        
        for p in payees:
            if not p[0] or p[0] == payee[0]: 
               continue
            ratio = fuzz.ratio(payee[1].lower(), p[1].lower())
            if ratio > 88:
               result.matches.append((p[0], ratio))
        if len(result.matches) > 0:
           result.matches_found = True
        return result

    def get_payee_names_stripped_of_whitespace(self, payees: List[Payee]) -> List[str]:
        result = []
        names = [s.name for s in payees]
        for name in names:
            sn = non_word_pattern.sub('', name)
            result.append((name, sn))
        return result
    
    def get_unqiue_payees_from_transactions(self, transactions: OrderedDict[int, Transaction]) -> List[Payee]:
        raw_transactions = [t for _, t in transactions.items() if t.transaction_type not in [TransactionType.transfer_in, TransactionType.transfer_out]]
        sorted_uncoded = sorted(raw_transactions, key=lambda t: t.payee)
        list_of_payees: List[Payee] = []
        for k, g in groupby(sorted_uncoded, key=lambda t: t.payee):
            transaction_list = list(g)
            list_of_payees.append(Payee(k, transaction_list))
        return list_of_payees
    
    def group_payees_by_name_similarity(self, transactions: List[Transaction]) -> Dict[str, Payee]:
        payees = self.get_unqiue_payees_from_transactions(transactions)
        stripped_names = self.get_payee_names_stripped_of_whitespace(payees)
        sorted_names = sorted(stripped_names)
        aliases: Dict[str, List[str]] = {}
        for payee in sorted_names:
            result = self.get_close_payee_matches(payee, sorted_names, aliases)
            if not result.matches_found: 
                if payee[0] not in aliases and not result.is_an_existing_alias: aliases[payee[0]] = []
                continue
            if payee[0] not in aliases: aliases[payee[0]] = []
            aliases[payee[0]].extend(result.matches)
        return aliases
