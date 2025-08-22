import redis
import json
from app.config import settings
from loguru import logger
from typing import Optional, Dict, Any

# Redis client with error handling
try:
    r = redis.Redis(
        host=settings.REDIS_HOST, 
        port=settings.REDIS_PORT, 
        db=0,  # Default Redis database
        decode_responses=True,
        socket_connect_timeout=5,  # 5 second connection timeout
        socket_timeout=5,          # 5 second operation timeout
        retry_on_timeout=True,
        health_check_interval=30
    )
    
    # Test the connection
    r.ping()
    logger.info(f"Redis connected successfully to {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    r = None
except Exception as e:
    logger.error(f"Redis initialization error: {e}")
    r = None

def get_cache(key: str) -> Optional[Dict[str, Any]]:
    """
    Get data from Redis cache.
    
    Args:
        key: Cache key
        
    Returns:
        Cached data or None if not found or Redis unavailable
    """
    if r is None:
        logger.warning("Redis not available, cannot get cache")
        return None
    
    try:
        value = r.get(key)
        if value:
            logger.info(f"Cache hit for key: {key}")
            return json.loads(value)
        else:
            logger.info(f"Cache miss for key: {key}")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode cached JSON for key {key}: {e}")
        return None
    except redis.RedisError as e:
        logger.error(f"Redis error while getting cache for key {key}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while getting cache for key {key}: {e}")
        return None

def set_cache(key: str, value: Dict[str, Any], expiration: Optional[int] = None) -> bool:
    """
    Set data in Redis cache.
    
    Args:
        key: Cache key
        value: Data to cache
        expiration: Expiration time in seconds (default from settings)
        
    Returns:
        True if successful, False otherwise
    """
    if r is None:
        logger.warning("Redis not available, cannot set cache")
        return False
    
    if expiration is None:
        expiration = settings.CACHE_EXPIRATION_SECONDS
    
    try:
        json_value = json.dumps(value)
        r.setex(key, expiration, json_value)
        logger.info(f"Cached data for key: {key} (expires in {expiration}s)")
        return True
    except json.JSONEncodeError as e:
        logger.error(f"Failed to encode data to JSON for key {key}: {e}")
        return False
    except redis.RedisError as e:
        logger.error(f"Redis error while setting cache for key {key}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while setting cache for key {key}: {e}")
        return False

def delete_cache(key: str) -> bool:
    """
    Delete data from Redis cache.
    
    Args:
        key: Cache key to delete
        
    Returns:
        True if successful, False otherwise
    """
    if r is None:
        logger.warning("Redis not available, cannot delete cache")
        return False
    
    try:
        result = r.delete(key)
        if result > 0:
            logger.info(f"Deleted cache for key: {key}")
        else:
            logger.info(f"Cache key not found for deletion: {key}")
        return True
    except redis.RedisError as e:
        logger.error(f"Redis error while deleting cache for key {key}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while deleting cache for key {key}: {e}")
        return False

def clear_all_cache() -> bool:
    """
    Clear all cached data.
    
    Returns:
        True if successful, False otherwise
    """
    if r is None:
        logger.warning("Redis not available, cannot clear cache")
        return False
    
    try:
        r.flushdb()
        logger.info("Cleared all cached data")
        return True
    except redis.RedisError as e:
        logger.error(f"Redis error while clearing cache: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while clearing cache: {e}")
        return False

def get_cache_info() -> Dict[str, Any]:
    """
    Get information about the cache status.
    
    Returns:
        Dictionary with cache information
    """
    if r is None:
        return {
            "status": "unavailable",
            "message": "Redis connection failed"
        }
    
    try:
        info = r.info()
        return {
            "status": "available",
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "unknown"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0)
        }
    except Exception as e:
        logger.error(f"Failed to get Redis info: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
