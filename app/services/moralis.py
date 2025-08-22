import httpx
from app.config import settings
from app.utils.format import to_fixed_str


async def fetch_token_details():
    """Fetch token details (price, name, symbol, etc.) from Moralis Solana API"""

    url = f"{settings.MORALIS_URL}/token/mainnet/{settings.TOKEN_ADDRESS}/price"
    headers = {
        "accept": "application/json",
        "X-API-Key": settings.MORALIS_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

    # Map API response to schema format
    return {
        "token_name": data.get("name"),
        "token_symbol": data.get("symbol"),
        "price_usd": data.get("usdPrice"),
        "price_change_percentage_24h": data.get("usdPrice24hrPercentChange"),
        "volume_24h": data.get("usdPrice24h"),
    }
