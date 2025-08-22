import asyncio
import time
from datetime import datetime
from app.services.moralis import fetch_token_details
from app.services.birdeye import fetch_token_stats
from app.utils.format import to_fixed_str, format_to_millions
from app.services.cache_manager import tokenomics_cache
from app.config import settings
from loguru import logger
from typing import Dict, Any, Optional

async def fetch_with_fallback(api_func, api_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch data from an API with error handling and logging.
    
    Args:
        api_func: Async function to call
        api_name: Name of the API for logging
    
    Returns:
        API response data or None if failed
    """
    start_time = time.time()
    try:
        logger.info(f"Fetching data from {api_name}")
        data = await api_func()
        response_time = time.time() - start_time
        logger.info(f"Successfully fetched data from {api_name} in {response_time:.3f}s")
        return data
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"Failed to fetch data from {api_name} after {response_time:.3f}s: {str(e)}")
        return None

async def aggregated_tokenomics():
    """
    Aggregate token data from Moralis and Birdeye with enhanced caching and fallback mechanisms.
    
    Returns:
        dict with combined fields, using partial data if some APIs fail
    """
    start_time = time.time()
    token_address = settings.TOKEN_ADDRESS
    
    # Try to get from cache first using the cache manager
    logger.info(f"Checking cache for token: {token_address}")
    cached_data = tokenomics_cache.get_cached_data(token_address)
    
    if cached_data:
        response_time = time.time() - start_time
        logger.info(f"Returning cached data in {response_time:.3f}s")
        
        # Add response time to cache info
        cached_data["cache_info"]["response_time"] = response_time
        return cached_data
    
    # Cache miss - fetch from APIs
    logger.info("Fetching fresh data from APIs")
    
    # Fetch from both APIs concurrently with individual error handling
    moralis_data, birdeye_data = await asyncio.gather(
        fetch_with_fallback(fetch_token_details, "Moralis"),
        fetch_with_fallback(fetch_token_stats, "Birdeye"),
        return_exceptions=True
    )
    
    # Handle exceptions from gather
    if isinstance(moralis_data, Exception):
        logger.error(f"Moralis API failed: {moralis_data}")
        moralis_data = None
    if isinstance(birdeye_data, Exception):
        logger.error(f"Birdeye API failed: {birdeye_data}")
        birdeye_data = None
    
    # Build result with available data
    result = {}
    
    # Add Moralis data if available
    if moralis_data:
        result.update({
            "token_name": moralis_data.get("token_name"),
            "token_symbol": moralis_data.get("token_symbol"),
            "price_usd": moralis_data.get("price_usd"),
            "price_change_percentage_24h": moralis_data.get("price_change_percentage_24h"),
            "volume_24h": moralis_data.get("volume_24h"),
        })
    else:
        # Fallback values for Moralis data
        result.update({
            "token_name": "Unknown Token",
            "token_symbol": "UNKNOWN",
            "price_usd": 0.0,
            "price_change_percentage_24h": 0.0,
            "volume_24h": 0.0,
        })
    
    # Add Birdeye data if available
    if birdeye_data:
        result.update({
            "market_cap": birdeye_data.get("market_cap"),
            "total_supply": birdeye_data.get("total_supply"),
            "circulating_supply": birdeye_data.get("circulating_supply"),
        })
    else:
        # Fallback values for Birdeye data
        result.update({
            "market_cap": 0.0,
            "total_supply": 0.0,
            "circulating_supply": 0.0,
        })
    
    # Add metadata about data sources
    result["data_sources"] = {
        "moralis": "available" if moralis_data else "failed",
        "birdeye": "available" if birdeye_data else "failed"
    }
    
    # Add response time
    response_time = time.time() - start_time
    result["response_time"] = response_time
    
    # Cache the result if we have meaningful data using the cache manager
    if moralis_data or birdeye_data:
        logger.info("Caching aggregated data")
        cache_success = tokenomics_cache.set_cached_data(token_address, result, expiration=300)
        if not cache_success:
            logger.warning("Failed to cache data")
    else:
        logger.warning("No data available from any API, not caching")
    
    return result

async def get_cache_performance():
    """Get comprehensive cache performance metrics"""
    token_address = settings.TOKEN_ADDRESS
    return tokenomics_cache.get_cache_performance(token_address)
