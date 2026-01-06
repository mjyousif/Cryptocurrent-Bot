from dataclasses import dataclass
from typing import Optional


@dataclass
class CryptoQuote:
    id: int
    name: str
    symbol: str
    price: Optional[float]
    market_cap: Optional[float]
    percent_change_1h: Optional[float]
    percent_change_24h: Optional[float]
    percent_change_7d: Optional[float]
    currency: str
