import hashlib
import time
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
from app.services.redis import get_cache, set_cache, get_cache_info
from app.config import settings

class CacheManager:
    """High-level cache management with statistics and performance tracking"""
    
    def __init__(self, namespace: str = "tokenomics"):
        self.namespace = namespace
    
    def get_cache_key(self, identifier: str) -> str:
        """Generate a cache key with namespace"""
        return f"{self.namespace}:{hashlib.md5(identifier.encode()).hexdigest()}"
    
    def get_stats_key(self, identifier: str) -> str:
        """Generate a cache statistics key"""
        return f"{self.namespace}:stats:{hashlib.md5(identifier.encode()).hexdigest()}"
    
    def update_cache_stats(self, identifier: str, cache_hit: bool, response_time: float) -> None:
        """Update cache statistics for monitoring"""
        try:
            stats_key = self.get_stats_key(identifier)
            current_stats = get_cache(stats_key) or {
                "hits": 0,
                "misses": 0,
                "total_requests": 0,
                "avg_response_time": 0,
                "last_updated": None
            }
            
            current_stats["total_requests"] += 1
            if cache_hit:
                current_stats["hits"] += 1
            else:
                current_stats["misses"] += 1
            
            # Update average response time
            total_time = current_stats["avg_response_time"] * (current_stats["total_requests"] - 1) + response_time
            current_stats["avg_response_time"] = total_time / current_stats["total_requests"]
            current_stats["last_updated"] = datetime.now().isoformat()
            
            # Cache stats for 1 hour
            set_cache(stats_key, current_stats, expiration=3600)
            
        except Exception as e:
            logger.warning(f"Failed to update cache stats: {e}")
    
    def get_cache_hit_rate(self, identifier: str) -> Dict[str, Any]:
        """Get cache hit rate and statistics"""
        try:
            stats_key = self.get_stats_key(identifier)
            stats = get_cache(stats_key)
            
            if not stats:
                return {
                    "hit_rate": 0.0,
                    "total_requests": 0,
                    "hits": 0,
                    "misses": 0,
                    "avg_response_time": 0
                }
            
            total_requests = stats.get("total_requests", 0)
            hits = stats.get("hits", 0)
            
            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests,
                "hits": hits,
                "misses": stats.get("misses", 0),
                "avg_response_time": round(stats.get("avg_response_time", 0), 3),
                "last_updated": stats.get("last_updated")
            }
        except Exception as e:
            logger.warning(f"Failed to get cache hit rate: {e}")
            return {"error": str(e)}
    
    def get_cached_data(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get cached data with statistics tracking"""
        start_time = time.time()
        cache_key = self.get_cache_key(identifier)
        
        cached_data = get_cache(cache_key)
        response_time = time.time() - start_time
        
        if cached_data:
            logger.info(f"Cache HIT for {identifier} in {response_time:.3f}s")
            self.update_cache_stats(identifier, cache_hit=True, response_time=response_time)
        else:
            logger.info(f"Cache MISS for {identifier} in {response_time:.3f}s")
            self.update_cache_stats(identifier, cache_hit=False, response_time=response_time)
        
        return cached_data
    
    def set_cached_data(self, identifier: str, data: Dict[str, Any], expiration: Optional[int] = None) -> bool:
        """Set cached data with metadata"""
        cache_key = self.get_cache_key(identifier)
        
        # Add cache metadata
        data["cache_info"] = {
            "source": "api",
            "cached_at": datetime.now().isoformat(),
            "namespace": self.namespace
        }
        
        success = set_cache(cache_key, data, expiration=expiration)
        if success:
            logger.info(f"Successfully cached data for {identifier}")
        else:
            logger.warning(f"Failed to cache data for {identifier}")
        
        return success
    
    def get_cache_performance(self, identifier: str) -> Dict[str, Any]:
        """Get comprehensive cache performance metrics"""
        try:
            # Get Redis server info
            redis_info = get_cache_info()
            
            # Get cache hit rate
            hit_rate_info = self.get_cache_hit_rate(identifier)
            
            return {
                "redis_server": redis_info,
                "cache_performance": hit_rate_info,
                "identifier": identifier,
                "cache_key": self.get_cache_key(identifier),
                "namespace": self.namespace
            }
        except Exception as e:
            logger.error(f"Failed to get cache performance: {e}")
            return {"error": str(e)}

# Global cache manager instance for tokenomics
tokenomics_cache = CacheManager(namespace="tokenomics")
