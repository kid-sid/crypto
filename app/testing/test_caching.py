#!/usr/bin/env python3
"""
Enhanced Redis Caching Test Script
This script demonstrates the improved caching functionality in the aggregator
"""

import sys
import os
import asyncio
import time

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.aggregator import aggregated_tokenomics, get_cache_performance
from app.services.redis import get_cache_info, clear_all_cache
from app.config import settings

async def test_caching_behavior():
    """Test the enhanced caching behavior"""
    print("🚀 Testing Enhanced Redis Caching...")
    print("=" * 60)
    
    # Check Redis status
    print("1. Checking Redis status...")
    redis_info = get_cache_info()
    if redis_info.get("status") != "available":
        print("   ❌ Redis is not available!")
        print("   Please start Redis: docker run -d --name redis -p 6379:6379 redis")
        return False
    
    print("   ✅ Redis is available")
    print(f"   Host: {redis_info.get('host')}:{redis_info.get('port')}")
    
    # Clear any existing cache
    print("\n2. Clearing existing cache...")
    clear_all_cache()
    print("   ✅ Cache cleared")
    
    # First request - should be a cache miss
    print("\n3. First request (should be cache MISS)...")
    start_time = time.time()
    data1 = await aggregated_tokenomics()
    response_time1 = time.time() - start_time
    
    print(f"   Response time: {response_time1:.3f}s")
    print(f"   Data source: {data1.get('cache_info', {}).get('source', 'unknown')}")
    print(f"   Token name: {data1.get('token_name', 'N/A')}")
    print(f"   Price: ${data1.get('price_usd', 'N/A')}")
    
    # Second request - should be a cache hit
    print("\n4. Second request (should be cache HIT)...")
    start_time = time.time()
    data2 = await aggregated_tokenomics()
    response_time2 = time.time() - start_time
    
    print(f"   Response time: {response_time2:.3f}s")
    print(f"   Data source: {data2.get('cache_info', {}).get('source', 'unknown')}")
    print(f"   Token name: {data2.get('token_name', 'N/A')}")
    print(f"   Price: ${data2.get('price_usd', 'N/A')}")
    
    # Compare response times
    speedup = response_time1 / response_time2 if response_time2 > 0 else 0
    print(f"   Speedup: {speedup:.1f}x faster with cache")
    
    # Check cache performance metrics
    print("\n5. Cache performance metrics...")
    performance = await get_cache_performance()
    
    cache_stats = performance.get("cache_performance", {})
    print(f"   Hit rate: {cache_stats.get('hit_rate', 0)}%")
    print(f"   Total requests: {cache_stats.get('total_requests', 0)}")
    print(f"   Hits: {cache_stats.get('hits', 0)}")
    print(f"   Misses: {cache_stats.get('misses', 0)}")
    print(f"   Average response time: {cache_stats.get('avg_response_time', 0)}s")
    
    # Verify data consistency
    print("\n6. Verifying data consistency...")
    if data1.get('token_name') == data2.get('token_name') and data1.get('price_usd') == data2.get('price_usd'):
        print("   ✅ Data is consistent between requests")
    else:
        print("   ❌ Data inconsistency detected")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced caching test completed!")
    print("\n📊 Summary:")
    print(f"   - Cache hit rate: {cache_stats.get('hit_rate', 0)}%")
    print(f"   - Performance improvement: {speedup:.1f}x faster")
    print(f"   - Redis status: {redis_info.get('status')}")
    
    return True

async def demonstrate_cache_benefits():
    """Demonstrate the benefits of caching with multiple requests"""
    print("\n🔄 Demonstrating Cache Benefits...")
    print("=" * 60)
    
    # Make multiple requests to show cache effectiveness
    requests = 5
    print(f"Making {requests} consecutive requests...")
    
    start_time = time.time()
    for i in range(requests):
        request_start = time.time()
        data = await aggregated_tokenomics()
        request_time = time.time() - request_start
        
        source = data.get('cache_info', {}).get('source', 'unknown')
        print(f"   Request {i+1}: {request_time:.3f}s ({source})")
    
    total_time = time.time() - start_time
    avg_time = total_time / requests
    
    print(f"\n📈 Results:")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Average time per request: {avg_time:.3f}s")
    print(f"   Requests per second: {requests/total_time:.1f}")
    
    # Get final performance stats
    performance = await get_cache_performance()
    cache_stats = performance.get("cache_performance", {})
    print(f"   Final hit rate: {cache_stats.get('hit_rate', 0)}%")

if __name__ == "__main__":
    try:
        # Run basic caching test
        success = asyncio.run(test_caching_behavior())
        
        if success:
            # Run demonstration
            asyncio.run(demonstrate_cache_benefits())
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
