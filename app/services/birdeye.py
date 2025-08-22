import httpx
from app.config import settings

async def fetch_token_stats():
    """
    Fetch market cap and total supply for a given Solana token from Birdeye API.
    :param token_address: Solana token address (mint address)
    :return: dict with market_cap and total_supply
    """
    url = (
        f"{settings.BIRDEYE_URL}{settings.TOKEN_ADDRESS}&ui_amount_mode=scaled"
    )

    headers = {
        "accept": "application/json",
        "x-api-key": settings.BIRDEYE_API_KEY,
        "x-chain": "solana"    
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "data" not in data:
            raise ValueError("Unexpected response from Birdeye API")

        token_data = data["data"]

        return {
            "market_cap": token_data.get("market_cap"),
            "total_supply": token_data.get("total_supply"),
            "circulating_supply": token_data.get("circulating_supply"),
        }
