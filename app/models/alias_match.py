from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class AliasMatch():
   matches_found: bool
   is_an_existing_alias: bool
   matches: List[Tuple[str, int]]