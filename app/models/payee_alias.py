from dataclasses import dataclass
from typing import Dict

from app.models.payee import Payee


@dataclass
class PayeeAlias():
    name: str
    payees: Dict[str, Payee]
