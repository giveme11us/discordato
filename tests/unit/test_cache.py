"""
Unit tests for cache management system.
"""
import pytest
import time
from unittest.mock import Mock, patch
from core.cache import CacheManager, CacheError, CacheEntry

@pytest.mark.unit
class TestCacheSystem:
    """Test suite for cache management functionality."""
    
    @pytest.fixture
    def cache_manager(self):
        """Fixture to provide a cache manager instance."""
        return CacheManager()
        
    def test_cache_initialization(self):
        """Test cache system initialization."""
        # Test
        cache = CacheManager(max_size=100)
        
        # Verify
        assert cache.max_size == 100
        assert len(cache) == 0
        
    def test_basic_cache_operations(self, cache_manager):
        """Test basic cache operations (set/get/delete)."""
        # Test set and get
        cache_manager.set("key1", "value1")
        assert cache_manager.get("key1") == "value1"
        
        # Test delete
        cache_manager.delete("key1")
        assert cache_manager.get("key1") is None
        
        # Test default value
        assert cache_manager.get("nonexistent", default="default") == "default"
        
    def test_cache_expiration(self, cache_manager):
        """Test cache entry expiration."""
        # Setup
        ttl = 1  # 1 second TTL
        
        # Test
        cache_manager.set("key1", "value1", ttl=ttl)
        assert cache_manager.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(ttl + 0.1)
        assert cache_manager.get("key1") is None
        
    def test_cache_max_size(self):
        """Test cache maximum size enforcement."""
        # Setup
        max_size = 2
        cache = CacheManager(max_size=max_size)
        
        # Test
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should trigger eviction
        
        # Verify - oldest entry should be evicted
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert len(cache) == max_size
        
    def test_cache_clear(self, cache_manager):
        """Test cache clearing."""
        # Setup
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        
        # Test
        cache_manager.clear()
        
        # Verify
        assert len(cache_manager) == 0
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None
        
    def test_cache_statistics(self, cache_manager):
        """Test cache statistics tracking."""
        # Setup and test
        cache_manager.set("key1", "value1")
        cache_manager.get("key1")  # Hit
        cache_manager.get("nonexistent")  # Miss
        
        # Verify
        stats = cache_manager.get_statistics()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
        
    def test_cache_decorator(self, cache_manager):
        """Test cache decorator functionality."""
        # Setup
        call_count = 0
        
        @cache_manager.cached(ttl=10)
        def expensive_function(arg):
            nonlocal call_count
            call_count += 1
            return f"result_{arg}"
            
        # Test
        result1 = expensive_function("test")
        result2 = expensive_function("test")
        
        # Verify
        assert result1 == result2
        assert call_count == 1  # Function should only be called once
        
    def test_cache_with_custom_key(self, cache_manager):
        """Test cache with custom key function."""
        # Setup
        def key_func(prefix, suffix):
            return f"{prefix}:{suffix}"
            
        # Test
        cache_manager.set_with_key_func(key_func, "prefix", "suffix", "value")
        
        # Verify
        assert cache_manager.get_with_key_func(key_func, "prefix", "suffix") == "value"
        
    def test_cache_bulk_operations(self, cache_manager):
        """Test bulk cache operations."""
        # Setup
        items = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        # Test bulk set
        cache_manager.set_many(items)
        
        # Verify bulk get
        results = cache_manager.get_many(items.keys())
        assert results == items
        
        # Test bulk delete
        cache_manager.delete_many(["key1", "key2"])
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None
        assert cache_manager.get("key3") == "value3"
        
    def test_cache_type_handling(self, cache_manager):
        """Test handling of different value types."""
        test_values = [
            ("string", "test"),
            ("integer", 42),
            ("float", 3.14),
            ("list", [1, 2, 3]),
            ("dict", {"key": "value"}),
            ("none", None),
            ("boolean", True)
        ]
        
        # Test each type
        for type_name, value in test_values:
            cache_manager.set(type_name, value)
            assert cache_manager.get(type_name) == value
            
    def test_cache_errors(self, cache_manager):
        """Test error handling in cache operations."""
        # Test invalid TTL
        with pytest.raises(CacheError, match="Invalid TTL value"):
            cache_manager.set("key", "value", ttl=-1)
            
        # Test invalid key type
        with pytest.raises(CacheError, match="Invalid key type"):
            cache_manager.set(123, "value")
            
        # Test invalid max size
        with pytest.raises(CacheError, match="Invalid max size"):
            CacheManager(max_size=-1)
            
    def test_cache_persistence(self, tmp_path):
        """Test cache persistence functionality."""
        # Setup
        cache_file = tmp_path / "cache.db"
        cache = CacheManager(persistence_file=str(cache_file))
        
        # Test
        cache.set("key1", "value1")
        cache.persist()  # Save to disk
        
        # Create new cache instance and load
        new_cache = CacheManager(persistence_file=str(cache_file))
        new_cache.load()
        
        # Verify
        assert new_cache.get("key1") == "value1"
        
    def test_cache_entry_metadata(self, cache_manager):
        """Test cache entry metadata handling."""
        # Setup
        metadata = {"source": "test", "version": 1}
        
        # Test
        cache_manager.set("key1", "value1", metadata=metadata)
        entry = cache_manager.get_entry("key1")
        
        # Verify
        assert isinstance(entry, CacheEntry)
        assert entry.value == "value1"
        assert entry.metadata == metadata
        
    def test_cache_update_operations(self, cache_manager):
        """Test cache update operations."""
        # Setup
        def increment(value):
            return value + 1
            
        # Test
        cache_manager.set("counter", 0)
        cache_manager.update("counter", increment)
        
        # Verify
        assert cache_manager.get("counter") == 1
        
        # Test update with missing key
        with pytest.raises(CacheError, match="Key not found"):
            cache_manager.update("nonexistent", increment) 