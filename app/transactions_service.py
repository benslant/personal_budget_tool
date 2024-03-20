from typing import Dict, List
from collections import OrderedDict
from models.transaction import Transaction


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