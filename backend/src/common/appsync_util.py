
from dataclasses import dataclass


@dataclass
class FilterInput():
    attr: str
    condition: str
    value: any
