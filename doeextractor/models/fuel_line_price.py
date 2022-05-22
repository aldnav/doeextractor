from dataclasses import dataclass, field
from typing import Any


@dataclass
class FuelPrice:
    """
    Fuel price data class.
    """

    company: str
    price: Any


@dataclass
class FuelLinePriceItem:
    """
    Fuel line price item.
    """

    municity: str
    product: str = ""
    prices: list[FuelPrice] = field(default_factory=list)
    overall_range: str = ""
    common_price: str = ""
    average_price: str = ""
