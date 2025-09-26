# Phase 2 Preview: Repository Layer Implementation

## Executive Summary

Phase 2 introduces the Repository pattern to create a clean data access layer. This abstraction separates data storage concerns from business logic, enabling easy switching between data sources (JSON, database, API) and providing built-in caching, query optimization, and proper error handling.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│                  (UI Components - Phase 4)                   │
└─────────────────────────────────────────────────────────────┘
                               ▲
                               │
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
│                  (Business Logic - Phase 3)                  │
└─────────────────────────────────────────────────────────────┘
                               ▲
                               │
┌─────────────────────────────────────────────────────────────┐
│                   Repository Layer ← Phase 2                 │
│              (Data Access Abstraction)                       │
├───────────────────────────────────────────────────────────────┤
│   ┌─────────────────┐    ┌─────────────────┐               │
│   │ PresetRepository│◄───│JSONPresetRepo   │               │
│   │   (Interface)   │    │ (Implementation) │               │
│   └─────────────────┘    └─────────────────┘               │
│                           ┌─────────────────┐               │
│                           │  CachedRepo     │               │
│                           │   (Decorator)   │               │
│                           └─────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                               ▲
                               │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│                   (Models - Phase 1 ✓)                       │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Implementation Plan

### 1. Repository Interface (`src/data/repositories/base.py`)

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Set, Dict, Any, Callable
from pathlib import Path
from ..models.preset import Preset

class PresetRepository(ABC):
    """
    Abstract base class defining the contract for preset data access.
    
    This interface allows for multiple implementations (JSON, Database, API, etc.)
    while maintaining a consistent API for the service layer.
    """
    
    @abstractmethod
    async def load_all(self) -> List[Preset]:
        """
        Load all presets from the data source.
        
        Returns:
            List of all presets
            
        Raises:
            RepositoryError: If data cannot be loaded
        """
        pass
    
    @abstractmethod
    async def load_by_id(self, cc0: int, pgm: int) -> Optional[Preset]:
        """
        Load a specific preset by its MIDI identifiers.
        
        Args:
            cc0: MIDI CC0 (bank select) value
            pgm: MIDI program change value
            
        Returns:
            Preset if found, None otherwise
            
        Raises:
            RepositoryError: If data access fails
        """
        pass
    
    @abstractmethod
    async def load_by_pack(self, pack: str) -> List[Preset]:
        """
        Load all presets from a specific pack.
        
        Args:
            pack: Pack name to filter by
            
        Returns:
            List of presets in the pack
            
        Raises:
            RepositoryError: If data access fails
        """
        pass
    
    @abstractmethod
    async def load_by_type(self, preset_type: str) -> List[Preset]:
        """
        Load all presets of a specific type.
        
        Args:
            preset_type: Type to filter by
            
        Returns:
            List of presets of the given type
            
        Raises:
            RepositoryError: If data access fails
        """
        pass
    
    @abstractmethod
    async def load_by_character(self, character: str) -> List[Preset]:
        """
        Load all presets with a specific character tag.
        
        Args:
            character: Character tag to filter by
            
        Returns:
            List of presets with the character tag
            
        Raises:
            RepositoryError: If data access fails
        """
        pass
    
    @abstractmethod
    async def save_all(self, presets: List[Preset]) -> None:
        """
        Save all presets to the data source.
        
        Args:
            presets: List of presets to save
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the preset collection.
        
        Returns:
            Dictionary containing:
                - total_count: Total number of presets
                - packs: List of unique pack names
                - types: List of unique preset types
                - characters: List of unique character tags
                - last_modified: Timestamp of last modification
                
        Raises:
            RepositoryError: If metadata cannot be retrieved
        """
        pass

class RepositoryError(Exception):
    """Base exception for repository operations."""
    pass

class DataNotFoundError(RepositoryError):
    """Raised when requested data is not found."""
    pass

class DataAccessError(RepositoryError):
    """Raised when data cannot be accessed (file, network, etc.)."""
    pass

class DataValidationError(RepositoryError):
    """Raised when data fails validation."""
    pass
```

### 2. JSON Repository Implementation (`src/data/repositories/json_repository.py`)

```python
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Set, Dict, Any
from datetime import datetime
import aiofiles
from ..models.preset import Preset
from .base import (
    PresetRepository, 
    RepositoryError,
    DataNotFoundError,
    DataAccessError,
    DataValidationError
)

logger = logging.getLogger(__name__)

class JSONPresetRepository(PresetRepository):
    """
    JSON file-based implementation of PresetRepository.
    
    Features:
    - Async file I/O for non-blocking operations
    - Built-in validation
    - Atomic write operations
    - Comprehensive error handling
    - Optional schema validation
    """
    
    def __init__(self, file_path: Path, validate_schema: bool = True):
        """
        Initialize JSON repository.
        
        Args:
            file_path: Path to JSON file
            validate_schema: Whether to validate JSON schema
        """
        self.file_path = file_path
        self.validate_schema = validate_schema
        self._lock = asyncio.Lock()  # For thread-safe operations
        
    async def load_all(self) -> List[Preset]:
        """Load all presets from JSON file."""
        try:
            async with aiofiles.open(self.file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                
            if self.validate_schema:
                self._validate_json_structure(data)
            
            presets = []
            for item in data:
                try:
                    preset = Preset.from_dict(item)
                    presets.append(preset)
                except Exception as e:
                    logger.warning(f"Failed to load preset: {e}, data: {item}")
                    if self.validate_schema:
                        raise DataValidationError(f"Invalid preset data: {e}")
            
            logger.info(f"Loaded {len(presets)} presets from {self.file_path}")
            return presets
            
        except FileNotFoundError:
            raise DataNotFoundError(f"Preset file not found: {self.file_path}")
        except json.JSONDecodeError as e:
            raise DataAccessError(f"Invalid JSON in preset file: {e}")
        except Exception as e:
            raise RepositoryError(f"Failed to load presets: {e}")
    
    async def load_by_id(self, cc0: int, pgm: int) -> Optional[Preset]:
        """Load a specific preset by MIDI identifiers."""
        presets = await self.load_all()
        for preset in presets:
            if preset.cc0 == cc0 and preset.pgm == pgm:
                return preset
        return None
    
    async def load_by_pack(self, pack: str) -> List[Preset]:
        """Load presets from a specific pack."""
        presets = await self.load_all()
        return [p for p in presets if p.pack == pack]
    
    async def load_by_type(self, preset_type: str) -> List[Preset]:
        """Load presets of a specific type."""
        presets = await self.load_all()
        return [p for p in presets if p.type == preset_type]
    
    async def load_by_character(self, character: str) -> List[Preset]:
        """Load presets with a specific character tag."""
        presets = await self.load_all()
        return [p for p in presets if character in p.chars]
    
    async def save_all(self, presets: List[Preset]) -> None:
        """
        Save all presets to JSON file with atomic write.
        
        Uses a temporary file and rename for atomic operation.
        """
        async with self._lock:  # Ensure thread-safe write
            try:
                # Convert presets to JSON
                data = [preset.to_dict() for preset in presets]
                json_content = json.dumps(data, indent=2, ensure_ascii=False)
                
                # Write to temporary file first
                temp_path = self.file_path.with_suffix('.tmp')
                async with aiofiles.open(temp_path, 'w', encoding='utf-8') as f:
                    await f.write(json_content)
                
                # Atomic rename
                temp_path.replace(self.file_path)
                
                logger.info(f"Saved {len(presets)} presets to {self.file_path}")
                
            except Exception as e:
                # Clean up temp file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                raise RepositoryError(f"Failed to save presets: {e}")
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the preset collection."""
        presets = await self.load_all()
        
        # Collect unique values
        packs = set()
        types = set()
        characters = set()
        
        for preset in presets:
            packs.add(preset.pack)
            types.add(preset.type)
            characters.update(preset.chars)
        
        # Get file modification time
        stat = self.file_path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        return {
            'total_count': len(presets),
            'packs': sorted(packs),
            'types': sorted(types),
            'characters': sorted(characters),
            'last_modified': last_modified,
            'file_size_bytes': stat.st_size,
            'file_path': str(self.file_path)
        }
    
    def _validate_json_structure(self, data: Any) -> None:
        """Validate JSON structure matches expected schema."""
        if not isinstance(data, list):
            raise DataValidationError("JSON root must be a list")
        
        required_fields = {'pack', 'type', 'cc0', 'pgm', 'preset'}
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise DataValidationError(f"Item {i} must be a dictionary")
            
            missing = required_fields - item.keys()
            if missing:
                raise DataValidationError(f"Item {i} missing fields: {missing}")
```

### 3. Cached Repository Decorator (`src/data/repositories/cached_repository.py`)

```python
import asyncio
import time
from typing import List, Optional, Dict, Any, Callable
from functools import wraps
import hashlib
import pickle
from ..models.preset import Preset
from .base import PresetRepository

class CachedRepository(PresetRepository):
    """
    Caching decorator for any PresetRepository implementation.
    
    Features:
    - LRU cache for query results
    - TTL (time-to-live) for cache entries
    - Cache invalidation strategies
    - Memory limit management
    - Cache statistics
    """
    
    def __init__(
        self,
        repository: PresetRepository,
        cache_ttl: int = 300,  # 5 minutes default
        max_cache_size: int = 100,  # Maximum number of cache entries
        enable_stats: bool = True
    ):
        """
        Initialize cached repository.
        
        Args:
            repository: Underlying repository to cache
            cache_ttl: Cache time-to-live in seconds
            max_cache_size: Maximum number of cache entries
            enable_stats: Whether to collect cache statistics
        """
        self._repository = repository
        self._cache_ttl = cache_ttl
        self._max_cache_size = max_cache_size
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self._lock = asyncio.Lock()
        
        # Statistics
        self._enable_stats = enable_stats
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'invalidations': 0
        }
    
    class CacheEntry:
        """Single cache entry with timestamp."""
        def __init__(self, data: Any, timestamp: float):
            self.data = data
            self.timestamp = timestamp
        
        def is_expired(self, ttl: int) -> bool:
            return time.time() - self.timestamp > ttl
    
    def _cache_key(self, method: str, *args, **kwargs) -> str:
        """Generate cache key from method and arguments."""
        key_data = f"{method}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_cached(self, key: str) -> Optional[Any]:
        """Get item from cache if valid."""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                if not entry.is_expired(self._cache_ttl):
                    # Move to end (most recently used)
                    self._access_order.remove(key)
                    self._access_order.append(key)
                    
                    if self._enable_stats:
                        self._stats['hits'] += 1
                    
                    return entry.data
                else:
                    # Remove expired entry
                    del self._cache[key]
                    self._access_order.remove(key)
            
            if self._enable_stats:
                self._stats['misses'] += 1
            
            return None
    
    async def _set_cached(self, key: str, data: Any) -> None:
        """Set item in cache with LRU eviction."""
        async with self._lock:
            # Check cache size limit
            if len(self._cache) >= self._max_cache_size:
                # Evict least recently used
                lru_key = self._access_order.pop(0)
                del self._cache[lru_key]
                
                if self._enable_stats:
                    self._stats['evictions'] += 1
            
            # Add new entry
            self._cache[key] = self.CacheEntry(data, time.time())
            self._access_order.append(key)
    
    async def invalidate_cache(self, pattern: Optional[str] = None) -> None:
        """
        Invalidate cache entries.
        
        Args:
            pattern: Optional pattern to match keys (None = clear all)
        """
        async with self._lock:
            if pattern is None:
                # Clear all
                count = len(self._cache)
                self._cache.clear()
                self._access_order.clear()
            else:
                # Clear matching keys
                keys_to_remove = [k for k in self._cache if pattern in k]
                count = len(keys_to_remove)
                
                for key in keys_to_remove:
                    del self._cache[key]
                    self._access_order.remove(key)
            
            if self._enable_stats:
                self._stats['invalidations'] += count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self._enable_stats:
            return {}
        
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            **self._stats,
            'hit_rate': f"{hit_rate:.2%}",
            'cache_size': len(self._cache),
            'max_size': self._max_cache_size,
            'ttl_seconds': self._cache_ttl
        }
    
    # Implement all repository methods with caching
    
    async def load_all(self) -> List[Preset]:
        """Load all presets with caching."""
        cache_key = self._cache_key('load_all')
        
        # Try cache first
        cached = await self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        # Load from repository
        result = await self._repository.load_all()
        
        # Cache result
        await self._set_cached(cache_key, result)
        
        return result
    
    async def load_by_id(self, cc0: int, pgm: int) -> Optional[Preset]:
        """Load preset by ID with caching."""
        cache_key = self._cache_key('load_by_id', cc0, pgm)
        
        cached = await self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        result = await self._repository.load_by_id(cc0, pgm)
        await self._set_cached(cache_key, result)
        
        return result
    
    async def load_by_pack(self, pack: str) -> List[Preset]:
        """Load by pack with caching."""
        cache_key = self._cache_key('load_by_pack', pack)
        
        cached = await self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        result = await self._repository.load_by_pack(pack)
        await self._set_cached(cache_key, result)
        
        return result
    
    async def load_by_type(self, preset_type: str) -> List[Preset]:
        """Load by type with caching."""
        cache_key = self._cache_key('load_by_type', preset_type)
        
        cached = await self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        result = await self._repository.load_by_type(preset_type)
        await self._set_cached(cache_key, result)
        
        return result
    
    async def load_by_character(self, character: str) -> List[Preset]:
        """Load by character with caching."""
        cache_key = self._cache_key('load_by_character', character)
        
        cached = await self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        result = await self._repository.load_by_character(character)
        await self._set_cached(cache_key, result)
        
        return result
    
    async def save_all(self, presets: List[Preset]) -> None:
        """Save all presets and invalidate cache."""
        await self._repository.save_all(presets)
        await self.invalidate_cache()  # Clear all cache after write
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get metadata with cache stats."""
        metadata = await self._repository.get_metadata()
        
        if self._enable_stats:
            metadata['cache_stats'] = self.get_cache_stats()
        
        return metadata
```

### 4. Query Builder (`src/data/repositories/query_builder.py`)

```python
from typing import List, Callable, Optional, Set
from dataclasses import dataclass, field
from ..models.preset import Preset

@dataclass
class QueryBuilder:
    """
    Fluent interface for building complex preset queries.
    
    Example:
        query = (QueryBuilder()
                .with_pack("factory")
                .with_type("bass")
                .with_any_character(["warm", "analog"])
                .exclude_character("digital")
                .limit(10))
        
        results = await repository.execute_query(query)
    """
    
    # Filter criteria
    packs: Optional[Set[str]] = None
    types: Optional[Set[str]] = None
    required_chars: Optional[Set[str]] = None
    any_chars: Optional[Set[str]] = None
    excluded_chars: Optional[Set[str]] = None
    search_term: Optional[str] = None
    
    # MIDI range filters
    cc0_min: Optional[int] = None
    cc0_max: Optional[int] = None
    pgm_min: Optional[int] = None
    pgm_max: Optional[int] = None
    
    # Result options
    limit_count: Optional[int] = None
    offset: int = 0
    sort_by: Optional[str] = None
    reverse_sort: bool = False
    
    def with_pack(self, pack: str) -> 'QueryBuilder':
        """Filter by pack name."""
        if self.packs is None:
            self.packs = set()
        self.packs.add(pack)
        return self
    
    def with_packs(self, packs: List[str]) -> 'QueryBuilder':
        """Filter by multiple pack names."""
        if self.packs is None:
            self.packs = set()
        self.packs.update(packs)
        return self
    
    def with_type(self, preset_type: str) -> 'QueryBuilder':
        """Filter by preset type."""
        if self.types is None:
            self.types = set()
        self.types.add(preset_type)
        return self
    
    def with_types(self, types: List[str]) -> 'QueryBuilder':
        """Filter by multiple preset types."""
        if self.types is None:
            self.types = set()
        self.types.update(types)
        return self
    
    def with_all_characters(self, chars: List[str]) -> 'QueryBuilder':
        """Require all specified character tags."""
        if self.required_chars is None:
            self.required_chars = set()
        self.required_chars.update(chars)
        return self
    
    def with_any_character(self, chars: List[str]) -> 'QueryBuilder':
        """Require at least one of the specified character tags."""
        if self.any_chars is None:
            self.any_chars = set()
        self.any_chars.update(chars)
        return self
    
    def exclude_character(self, char: str) -> 'QueryBuilder':
        """Exclude presets with specified character tag."""
        if self.excluded_chars is None:
            self.excluded_chars = set()
        self.excluded_chars.add(char)
        return self
    
    def with_search(self, search_term: str) -> 'QueryBuilder':
        """Add search term filter."""
        self.search_term = search_term
        return self
    
    def in_cc0_range(self, min_cc0: int, max_cc0: int) -> 'QueryBuilder':
        """Filter by CC0 range."""
        self.cc0_min = min_cc0
        self.cc0_max = max_cc0
        return self
    
    def in_pgm_range(self, min_pgm: int, max_pgm: int) -> 'QueryBuilder':
        """Filter by program range."""
        self.pgm_min = min_pgm
        self.pgm_max = max_pgm
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """Limit number of results."""
        self.limit_count = count
        return self
    
    def skip(self, count: int) -> 'QueryBuilder':
        """Skip first N results."""
        self.offset = count
        return self
    
    def sort(self, field: str, reverse: bool = False) -> 'QueryBuilder':
        """Sort results by field."""
        self.sort_by = field
        self.reverse_sort = reverse
        return self
    
    def build_filter(self) -> Callable[[Preset], bool]:
        """Build a filter function from the query criteria."""
        def filter_preset(preset: Preset) -> bool:
            # Pack filter
            if self.packs and preset.pack not in self.packs:
                return False
            
            # Type filter
            if self.types and preset.type not in self.types:
                return False
            
            # Required characters (must have all)
            if self.required_chars:
                preset_chars = set(preset.chars)
                if not self.required_chars.issubset(preset_chars):
                    return False
            
            # Any characters (must have at least one)
            if self.any_chars:
                preset_chars = set(preset.chars)
                if not preset_chars & self.any_chars:
                    return False
            
            # Excluded characters (must not have any)
            if self.excluded_chars:
                preset_chars = set(preset.chars)
                if preset_chars & self.excluded_chars:
                    return False
            
            # Search term
            if self.search_term and not preset.matches_search(self.search_term):
                return False
            
            # MIDI ranges
            if self.cc0_min is not None and preset.cc0 < self.cc0_min:
                return False
            if self.cc0_max is not None and preset.cc0 > self.cc0_max:
                return False
            if self.pgm_min is not None and preset.pgm < self.pgm_min:
                return False
            if self.pgm_max is not None and preset.pgm > self.pgm_max:
                return False
            
            return True
        
        return filter_preset
    
    def apply(self, presets: List[Preset]) -> List[Preset]:
        """Apply query to a list of presets."""
        # Apply filter
        filter_func = self.build_filter()
        results = [p for p in presets if filter_func(p)]
        
        # Apply sorting
        if self.sort_by:
            results.sort(
                key=lambda p: getattr(p, self.sort_by, ''),
                reverse=self.reverse_sort
            )
        
        # Apply pagination
        if self.offset:
            results = results[self.offset:]
        if self.limit_count:
            results = results[:self.limit_count]
        
        return results
```

### 5. Repository Factory (`src/data/repositories/factory.py`)

```python
from typing import Optional, Dict, Any
from pathlib import Path
from .base import PresetRepository
from .json_repository import JSONPresetRepository
from .cached_repository import CachedRepository

class RepositoryFactory:
    """
    Factory for creating repository instances with various configurations.
    
    Supports different backends and optional caching.
    """
    
    @staticmethod
    def create_json_repository(
        file_path: Path,
        enable_cache: bool = True,
        cache_ttl: int = 300,
        validate_schema: bool = True
    ) -> PresetRepository:
        """
        Create a JSON-based repository.
        
        Args:
            file_path: Path to JSON file
            enable_cache: Whether to enable caching
            cache_ttl: Cache time-to-live in seconds
            validate_schema: Whether to validate JSON schema
            
        Returns:
            Repository instance (possibly wrapped in cache)
        """
        # Create base repository
        repo = JSONPresetRepository(file_path, validate_schema)
        
        # Wrap in cache if requested
        if enable_cache:
            repo = CachedRepository(repo, cache_ttl=cache_ttl)
        
        return repo
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> PresetRepository:
        """
        Create repository from configuration dictionary.
        
        Args:
            config: Configuration dictionary with keys:
                - type: Repository type ('json', 'database', 'api')
                - cache: Cache configuration
                - Additional type-specific options
                
        Returns:
            Configured repository instance
        """
        repo_type = config.get('type', 'json')
        
        if repo_type == 'json':
            file_path = Path(config.get('file_path', 'OsmosePresets.json'))
            validate = config.get('validate_schema', True)
            repo = JSONPresetRepository(file_path, validate)
        elif repo_type == 'database':
            # Future: DatabaseRepository
            raise NotImplementedError("Database repository not yet implemented")
        elif repo_type == 'api':
            # Future: APIRepository
            raise NotImplementedError("API repository not yet implemented")
        else:
            raise ValueError(f"Unknown repository type: {repo_type}")
        
        # Apply caching if configured
        cache_config = config.get('cache', {})
        if cache_config.get('enabled', True):
            cache_ttl = cache_config.get('ttl', 300)
            max_size = cache_config.get('max_size', 100)
            repo = CachedRepository(
                repo,
                cache_ttl=cache_ttl,
                max_cache_size=max_size
            )
        
        return repo
```

## Testing Strategy

### Unit Tests (`tests/test_repositories.py`)

```python
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from src.data.repositories.json_repository import JSONPresetRepository
from src.data.repositories.cached_repository import CachedRepository
from src.data.repositories.query_builder import QueryBuilder

class TestJSONRepository:
    """Test JSON repository implementation."""
    
    @pytest.fixture
    async def repository(self, tmp_path):
        """Create repository with test data."""
        # Test implementation
        pass
    
    async def test_load_all(self, repository):
        """Test loading all presets."""
        pass
    
    async def test_load_by_id(self, repository):
        """Test loading by MIDI ID."""
        pass
    
    async def test_save_atomic(self, repository):
        """Test atomic save operation."""
        pass

class TestCachedRepository:
    """Test caching decorator."""
    
    async def test_cache_hit(self):
        """Test cache hit scenario."""
        pass
    
    async def test_cache_expiration(self):
        """Test TTL expiration."""
        pass
    
    async def test_lru_eviction(self):
        """Test LRU eviction policy."""
        pass

class TestQueryBuilder:
    """Test query builder."""
    
    def test_fluent_interface(self):
        """Test method chaining."""
        pass
    
    def test_complex_query(self):
        """Test complex filter combinations."""
        pass
```

## Migration Strategy

### Phase 2A: Parallel Implementation (Week 1)
1. Implement repository interfaces and JSON repository
2. Add comprehensive unit tests
3. Keep existing PresetData class functional

### Phase 2B: Integration (Week 2)
1. Create adapter layer for backward compatibility
2. Update service layer to use repositories
3. Add integration tests
4. Performance benchmarking

### Phase 2C: Cutover (Week 3)
1. Replace PresetData with repository calls
2. Update all UI components
3. Remove old static class
4. Documentation updates

## Benefits of Repository Pattern

### 1. **Separation of Concerns**
- Data access logic separated from business logic
- Clean interfaces between layers
- Single responsibility per class

### 2. **Testability**
- Easy to mock repositories for testing
- Can test business logic without data access
- Can test data access in isolation

### 3. **Flexibility**
- Easy to switch data sources (JSON → Database → API)
- Multiple implementations can coexist
- Runtime configuration possible

### 4. **Performance**
- Built-in caching layer
- Query optimization
- Async operations for non-blocking I/O
- Lazy loading capabilities

### 5. **Maintainability**
- Clear contracts via interfaces
- Consistent error handling
- Centralized data access logic
- Easy to add new query methods

### 6. **Scalability**
- Ready for distributed caching (Redis)
- Can add connection pooling
- Supports batch operations
- Prepared for microservices architecture

## Implementation Checklist

### Core Components
- [ ] Create repository interface (`base.py`)
- [ ] Implement JSON repository
- [ ] Add caching decorator
- [ ] Create query builder
- [ ] Implement repository factory
- [ ] Add error handling classes

### Testing
- [ ] Unit tests for JSON repository
- [ ] Unit tests for cache layer
- [ ] Integration tests with real data
- [ ] Performance benchmarks
- [ ] Error scenario tests

### Documentation
- [ ] API documentation
- [ ] Usage examples
- [ ] Migration guide
- [ ] Performance guidelines

### Optional Enhancements
- [ ] Database repository implementation
- [ ] API repository implementation
- [ ] Advanced query DSL
- [ ] Cache warming strategies
- [ ] Repository middleware system

## Example Usage

### Basic Repository Usage
```python
# Create repository
factory = RepositoryFactory()
repo = factory.create_json_repository(
    Path("OsmosePresets.json"),
    enable_cache=True,
    cache_ttl=600
)

# Simple queries
all_presets = await repo.load_all()
preset = await repo.load_by_id(cc0=34, pgm=35)
bass_presets = await repo.load_by_type("bass")

# Get metadata
metadata = await repo.get_metadata()
print(f"Total presets: {metadata['total_count']}")
print(f"Cache stats: {metadata['cache_stats']}")
```

### Using Query Builder
```python
# Complex query with builder
query = (QueryBuilder()
    .with_pack("factory")
    .with_types(["bass", "lead"])
    .with_any_character(["warm", "analog"])
    .exclude_character("digital")
    .with_search("vintage")
    .in_cc0_range(30, 32)
    .sort("preset", reverse=False)
    .limit(20))

# Execute query
results = query.apply(await repo.load_all())

# Or with custom repository method
results = await repo.execute_query(query)
```

### Cache Management
```python
# Create cached repository
cached_repo = CachedRepository(
    repository=json_repo,
    cache_ttl=300,
    max_cache_size=100
)

# Use normally - caching is transparent
presets = await cached_repo.load_all()  # Cache miss
presets = await cached_repo.load_all()  # Cache hit

# Check cache performance
stats = cached_repo.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']}")
print(f"Cache size: {stats['cache_size']}/{stats['max_size']}")

# Manual cache control
await cached_repo.invalidate_cache()  # Clear all
await cached_repo.invalidate_cache("load_by_type")  # Clear specific
```

### Error Handling
```python
try:
    presets = await repo.load_all()
except DataNotFoundError:
    # Handle missing file
    logger.error("Preset file not found")
except DataValidationError as e:
    # Handle validation errors
    logger.error(f"Invalid data: {e}")
except RepositoryError as e:
    # Handle general repository errors
    logger.error(f"Repository error: {e}")
```

## Performance Considerations

### Caching Strategy
- **TTL Selection**: Balance between freshness and performance
  - Short TTL (60s): Good for frequently changing data
  - Medium TTL (300s): Default, good balance
  - Long TTL (3600s): Good for static data

- **Cache Size**: Based on memory constraints
  - Small (50): Limited memory systems
  - Medium (100): Default, good for most cases
  - Large (500): High-memory systems with many queries

### Async Operations
- All repository methods are async for non-blocking I/O
- Can parallelize multiple queries with `asyncio.gather()`
- Supports concurrent reads with proper locking
- Write operations are atomic and thread-safe

### Query Optimization
- Use specific query methods when possible (`load_by_type` vs `load_all` + filter)
- Leverage query builder for complex filters
- Consider implementing indexes for large datasets
- Cache frequently used queries

## Comparison with Current Implementation

| Aspect | Current (PresetData) | New (Repository) |
|--------|---------------------|------------------|
| **Architecture** | Static class with class variables | Interface-based with DI |
| **Data Access** | Direct file I/O in class | Abstracted through repository |
| **Caching** | None | Built-in with TTL and LRU |
| **Testing** | Difficult to mock | Easy to mock and test |
| **Async** | Synchronous | Fully async |
| **Error Handling** | Basic | Comprehensive with typed exceptions |
| **Query Building** | Manual filter combinations | Fluent query builder |
| **Extensibility** | Hard to extend | Easy to add new implementations |
| **Performance** | Reloads file each time | Cached with optimizations |

## Future Enhancements (Phase 2+)

### 1. Database Backend
```python
class SQLiteRepository(PresetRepository):
    """SQLite implementation for local database storage."""
    async def load_all(self) -> List[Preset]:
        async with self.connection() as conn:
            rows = await conn.fetch("SELECT * FROM presets")
            return [Preset.from_dict(row) for row in rows]
```

### 2. API Backend
```python
class APIRepository(PresetRepository):
    """REST API implementation for remote data."""
    async def load_all(self) -> List[Preset]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/presets") as resp:
                data = await resp.json()
                return [Preset.from_dict(item) for item in data]
```

### 3. Repository Middleware
```python
class LoggingMiddleware:
    """Log all repository operations."""
    async def before_operation(self, operation: str, *args, **kwargs):
        logger.info(f"Starting {operation} with args={args}")
    
    async def after_operation(self, operation: str, result: Any):
        logger.info(f"Completed {operation}, returned {len(result)} items")
```

### 4. Advanced Caching
```python
class RedisRepository(CachedRepository):
    """Distributed caching with Redis."""
    async def _get_cached(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        return pickle.loads(value) if value else None
```

## Summary

Phase 2 introduces a robust repository layer that:

1. **Abstracts data access** behind clean interfaces
2. **Improves performance** with intelligent caching
3. **Enhances testability** through dependency injection
4. **Enables flexibility** with multiple backend support
5. **Provides better error handling** with typed exceptions
6. **Offers powerful querying** with the query builder
7. **Supports async operations** for better performance
8. **Maintains backward compatibility** during migration

This foundation will enable Phase 3 (Service Layer) to focus purely on business logic without concern for data access details, creating a clean, maintainable, and scalable architecture.