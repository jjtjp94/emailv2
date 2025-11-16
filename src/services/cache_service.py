"""
Cache service for storing temporary data and API responses.
Simple file-based cache with TTL support.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta

from src.config import get_settings

logger = logging.getLogger(__name__)


class CacheService:
    """Simple file-based cache service."""

    def __init__(self):
        self.settings = get_settings()
        self.cache_dir = Path(self.settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for a cache key."""
        # Sanitize key for filename
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
        return self.cache_dir / f"{safe_key}.cache"

    def _get_metadata_path(self, key: str) -> Path:
        """Get metadata file path for a cache key."""
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
        return self.cache_dir / f"{safe_key}.meta"

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        Store a value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be picklable)
            ttl_seconds: Time to live in seconds (None = no expiration)
        """
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_metadata_path(key)

            # Save value
            with open(cache_path, "wb") as f:
                pickle.dump(value, f)

            # Save metadata
            metadata = {
                "created_at": datetime.utcnow().isoformat(),
                "ttl_seconds": ttl_seconds
            }

            if ttl_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
                metadata["expires_at"] = expires_at.isoformat()

            with open(meta_path, "w") as f:
                json.dump(metadata, f)

            logger.debug(f"Cached value for key: {key}")

        except Exception as e:
            logger.error(f"Failed to cache value for {key}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from cache.

        Args:
            key: Cache key
            default: Default value if not found or expired

        Returns:
            Cached value or default
        """
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_metadata_path(key)

            # Check if cache files exist
            if not cache_path.exists() or not meta_path.exists():
                return default

            # Load metadata and check expiration
            with open(meta_path, "r") as f:
                metadata = json.load(f)

            if "expires_at" in metadata:
                expires_at = datetime.fromisoformat(metadata["expires_at"])
                if datetime.utcnow() > expires_at:
                    logger.debug(f"Cache expired for key: {key}")
                    self.delete(key)
                    return default

            # Load and return value
            with open(cache_path, "rb") as f:
                value = pickle.load(f)

            logger.debug(f"Cache hit for key: {key}")
            return value

        except Exception as e:
            logger.error(f"Failed to get cached value for {key}: {e}")
            return default

    def delete(self, key: str):
        """Delete a cached value."""
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_metadata_path(key)

            if cache_path.exists():
                cache_path.unlink()

            if meta_path.exists():
                meta_path.unlink()

            logger.debug(f"Deleted cache for key: {key}")

        except Exception as e:
            logger.error(f"Failed to delete cache for {key}: {e}")

    def clear_all(self):
        """Clear all cached data."""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()

            for meta_file in self.cache_dir.glob("*.meta"):
                meta_file.unlink()

            logger.info("Cleared all cache")

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

    def clear_expired(self):
        """Clear all expired cache entries."""
        try:
            count = 0

            for meta_file in self.cache_dir.glob("*.meta"):
                try:
                    with open(meta_file, "r") as f:
                        metadata = json.load(f)

                    if "expires_at" in metadata:
                        expires_at = datetime.fromisoformat(metadata["expires_at"])
                        if datetime.utcnow() > expires_at:
                            # Extract key from filename
                            key = meta_file.stem
                            cache_file = self.cache_dir / f"{key}.cache"

                            if cache_file.exists():
                                cache_file.unlink()

                            meta_file.unlink()
                            count += 1

                except Exception as e:
                    logger.warning(f"Error processing {meta_file}: {e}")

            if count > 0:
                logger.info(f"Cleared {count} expired cache entries")

        except Exception as e:
            logger.error(f"Failed to clear expired cache: {e}")

    def get_stats(self) -> dict:
        """Get cache statistics."""
        try:
            cache_files = list(self.cache_dir.glob("*.cache"))
            total_size = sum(f.stat().st_size for f in cache_files)

            return {
                "total_entries": len(cache_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_dir": str(self.cache_dir)
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


# Global instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create the global CacheService instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
