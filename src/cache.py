"""
Caching module for API responses
Provides simple file-based caching to reduce API calls
"""
import os
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional, Callable
from functools import wraps


class Cache:
    """Simple file-based cache for API responses"""
    
    def __init__(self, cache_dir: str = ".cache", ttl: int = 86400):
        """Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl: Time to live in seconds (default 24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash
        
        Args:
            key: Original key string
        
        Returns:
            MD5 hash of the key
        """
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key
        
        Args:
            key: Cache key
        
        Returns:
            Path to cache file
        """
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found or expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            if time.time() - cache_data['timestamp'] > self.ttl:
                cache_path.unlink()  # Delete expired cache
                return None
            
            return cache_data['value']
        except (json.JSONDecodeError, KeyError, IOError):
            # If cache is corrupted, delete it
            if cache_path.exists():
                cache_path.unlink()
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        """
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            'timestamp': time.time(),
            'key': key,
            'value': value
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except (IOError, TypeError) as e:
            # If caching fails, just continue without caching
            pass
    
    def delete(self, key: str) -> None:
        """Delete value from cache
        
        Args:
            key: Cache key
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    def clear(self) -> int:
        """Clear all cache files
        
        Returns:
            Number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count
    
    def clear_expired(self) -> int:
        """Clear expired cache files
        
        Returns:
            Number of expired files deleted
        """
        count = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                if current_time - cache_data['timestamp'] > self.ttl:
                    cache_file.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError, IOError):
                # Delete corrupted cache files
                cache_file.unlink()
                count += 1
        
        return count
    
    def size(self) -> int:
        """Get number of cached items
        
        Returns:
            Number of cache files
        """
        return len(list(self.cache_dir.glob("*.json")))


# Global cache instance
_cache = None


def get_cache(cache_dir: str = ".cache", ttl: int = 86400) -> Cache:
    """Get or create global cache instance
    
    Args:
        cache_dir: Directory to store cache files
        ttl: Time to live in seconds
    
    Returns:
        Cache instance
    """
    global _cache
    if _cache is None:
        _cache = Cache(cache_dir, ttl)
    return _cache


def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (uses cache default if None)
        key_func: Function to generate cache key from args/kwargs
    
    Returns:
        Decorated function
    
    Example:
        @cached(ttl=3600)
        def get_data(url):
            return requests.get(url).json()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name and arguments
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


# Convenience functions

def cache_api_response(url: str, response_data: Any, ttl: int = 86400) -> None:
    """Cache an API response
    
    Args:
        url: API URL (used as cache key)
        response_data: Response data to cache
        ttl: Time to live in seconds
    """
    cache = get_cache(ttl=ttl)
    cache.set(f"api:{url}", response_data)


def get_cached_api_response(url: str) -> Optional[Any]:
    """Get cached API response
    
    Args:
        url: API URL (used as cache key)
    
    Returns:
        Cached response or None
    """
    cache = get_cache()
    return cache.get(f"api:{url}")

# Made with Bob