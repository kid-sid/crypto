import asyncio
import time
from app.services.moralis import fetch_token_details
from app.services.birdeye import fetch_token_stats
from app.services.aggregator import aggregated_tokenomics
from app.config import settings

async def main():
    # Test individual services first
    # print("=== Testing Moralis ===")
    # try:
    #     price = await fetch_token_details()
    #     print("Price:", price)
    # except Exception as e:
    #     print("Moralis error:", e)

    # print("\n=== Testing Birdeye ===")
    # try:
    #     data = await fetch_token_stats()  # uses settings.TOKEN_ADDRESS internally
    #     print("Market Data:", data)
    # except Exception as e:
    #     print("Birdeye error:", e)

    # # Add delay to avoid rate limiting
    # print("\nWaiting 2 seconds to avoid rate limiting...")
    # await asyncio.sleep(2)

    print("\n=== Testing Aggregator ===")
    try:
        data = await aggregated_tokenomics()  # uses settings.TOKEN_ADDRESS internally
        print("Aggregated data:", data)
    except Exception as e:
        print("Aggregator error:", e)

    

if __name__ == "__main__":
    asyncio.run(main())
