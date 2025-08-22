from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Any

class CoinData(BaseModel):
    token_address: str
    token_name: str
    token_symbol: str
    token_total_supply: int

    price_usd: Decimal
    volume_24h: Decimal
    holders: int
    whales: int
    sharks: int

    created_at: datetime
    market_cap: Decimal
    price_change_percentage_24h: Decimal
    price_change_percentage_7d: Decimal


class SuccessResponse(BaseModel):
    message: str
    data: Any
