# Phase 2: Repository Pattern Architecture

## Visual Architecture Overview

```mermaid
graph TB
    subgraph "Application Layer"
        UI[UI Components<br/>PresetGrid, FilterSelector]
    end
    
    subgraph "Service Layer (Phase 3)"
        PS[PresetService]
        FS[FilterService]
        SS[SearchService]
    end
    
    subgraph "Repository Layer (Phase 2)"
        RI[Repository Interface<br/><<abstract>>]
        CR[CachedRepository<br/><<decorator>>]
        JR[JSONRepository]
        DR[DatabaseRepository<br/><<future>>]
        AR[APIRepository<br/><<future>>]
        QB[QueryBuilder]
        RF[RepositoryFactory]
    end
    
    subgraph "Data Layer (Phase 1)"
        PM[Preset Model]
        PT[PresetType Enum]
    end
    
    subgraph "External Storage"
        JSON[(JSON File)]
        DB[(Database)]
        API[REST API]
    end
    
    UI --> PS
    UI --> FS
    PS --> RI
    FS --> RI
    SS --> RI
    
    RF -.->|creates| CR
    RF -.->|creates| JR
    
    CR -->|decorates| RI
    JR -->|implements| RI
    DR -->|implements| RI
    AR -->|implements| RI
    
    QB -->|used by| RI
    
    JR --> JSON
    DR --> DB
    AR --> API
    
    JR --> PM
    DR --> PM
    AR --> PM
    
    style RI fill:#e1f5fe
    style CR fill:#fff3e0
    style JR fill:#c8e6c9
    style QB fill:#f3e5f5
    style RF fill:#fce4ec
```

## Component Responsibilities

### Repository Interface (Abstract Base)
```python
class PresetRepository(ABC):
    """Defines contract for all repository implementations"""
    
    @abstractmethod
    async def load_all() -> List[Preset]
    
    @abstractmethod
    async def load_by_id(cc0: int, pgm: int) -> Optional[Preset]
    
    @abstractmethod
    async def save_all(presets: List[Preset]) -> None
```

### JSON Repository (Concrete Implementation)
```python
class JSONPresetRepository(PresetRepository):
    """File-based storage implementation"""
    
    - Async file I/O
    - Schema validation
    - Atomic writes
    - Error handling
```

### Cached Repository (Decorator Pattern)
```python
class CachedRepository(PresetRepository):
    """Adds caching to any repository"""
    
    - LRU cache with TTL
    - Cache statistics
    - Invalidation strategies
    - Memory management
```

### Query Builder (Fluent Interface)
```python
class QueryBuilder:
    """Build complex queries programmatically"""
    
    query = QueryBuilder()
        .with_pack("factory")
        .with_type("bass")
        .with_search("warm")
        .limit(10)
```

## Data Flow Sequences

### 1. Loading Presets (Cache Miss)
```mermaid
sequenceDiagram
    participant UI as UI Component
    participant S as Service
    participant C as CachedRepo
    participant J as JSONRepo
    participant F as File System
    
    UI->>S: getFilteredPresets()
    S->>C: load_all()
    C->>C: check cache
    Note over C: Cache miss
    C->>J: load_all()
    J->>F: read JSON file
    F-->>J: file content
    J->>J: parse & validate
    J->>J: create Preset objects
    J-->>C: List[Preset]
    C->>C: store in cache
    C-->>S: List[Preset]
    S->>S: apply filters
    S-->>UI: filtered results
```

### 2. Loading Presets (Cache Hit)
```mermaid
sequenceDiagram
    participant UI as UI Component
    participant S as Service
    participant C as CachedRepo
    
    UI->>S: getFilteredPresets()
    S->>C: load_all()
    C->>C: check cache
    Note over C: Cache hit!
    C-->>S: List[Preset] (from cache)
    S->>S: apply filters
    S-->>UI: filtered results
```

### 3. Saving Presets
```mermaid
sequenceDiagram
    participant UI as UI Component
    participant S as Service
    participant C as CachedRepo
    participant J as JSONRepo
    participant F as File System
    
    UI->>S: savePreset(preset)
    S->>C: save_all(presets)
    C->>J: save_all(presets)
    J->>J: validate data
    J->>J: serialize to JSON
    J->>F: write to temp file
    F-->>J: write complete
    J->>F: atomic rename
    J-->>C: success
    C->>C: invalidate cache
    C-->>S: success
    S-->>UI: save complete
```

## Cache Strategy

### Cache Layers
```
┌─────────────────────────────────────────┐
│          Query Results Cache            │
│         (Complex filter results)        │
├─────────────────────────────────────────┤
│           Entity Cache                  │
│        (Individual presets)             │
├─────────────────────────────────────────┤
│          Collection Cache               │
│         (Full preset list)              │
├─────────────────────────────────────────┤
│           Metadata Cache                │
│    (Packs, types, characters lists)     │
└─────────────────────────────────────────┘
```

### Cache Invalidation Rules

| Operation | Invalidates |
|-----------|------------|
| `save_all()` | All caches |
| `update_preset()` | Specific preset + collections |
| `delete_preset()` | Specific preset + collections |
| TTL expiration | Individual entry |
| Memory pressure | LRU entries |

## Error Handling Hierarchy

```
RepositoryError
├── DataNotFoundError
│   ├── FileNotFoundError
│   └── PresetNotFoundError
├── DataAccessError
│   ├── PermissionError
│   ├── NetworkError
│   └── TimeoutError
└── DataValidationError
    ├── SchemaValidationError
    ├── MissingFieldError
    └── InvalidValueError
```

## Performance Characteristics

### Time Complexity

| Operation | Without Cache | With Cache (Hit) | With Cache (Miss) |
|-----------|--------------|------------------|-------------------|
| `load_all()` | O(n) | O(1) | O(n) |
| `load_by_id()` | O(n) | O(1) | O(n) |
| `load_by_pack()` | O(n) | O(1) | O(n) |
| `save_all()` | O(n) | O(n) | O(n) |
| Query Builder | O(n×m) | O(1) | O(n×m) |

Where:
- n = number of presets
- m = number of filter conditions

### Space Complexity

| Component | Space Usage |
|-----------|------------|
| JSON Repository | O(n) - full dataset in memory during operations |
| Cached Repository | O(k) - where k is cache size limit |
| Query Builder | O(1) - minimal overhead |
| Preset Model | O(n) - linear with dataset size |

## Configuration Options

### Repository Configuration
```yaml
repository:
  type: json
  file_path: "OsmosePresets.json"
  validate_schema: true
  encoding: utf-8
  
cache:
  enabled: true
  ttl_seconds: 300
  max_entries: 100
  eviction_policy: lru
  enable_stats: true
  
performance:
  batch_size: 100
  async_io: true
  connection_pool_size: 5
```

### Environment-Specific Settings

| Environment | Cache TTL | Max Cache | Validation |
|------------|-----------|-----------|------------|
| Development | 60s | 50 | Full |
| Testing | 0s (disabled) | 0 | Full |
| Staging | 300s | 100 | Full |
| Production | 3600s | 500 | Minimal |

## Migration Path

### Phase 2A: Parallel Implementation
- Repository interfaces created
- JSON implementation complete
- Tests passing
- Old PresetData still active

### Phase 2B: Adapter Layer
```python
# Temporary adapter for backward compatibility
class PresetDataAdapter:
    def __init__(self, repository: PresetRepository):
        self._repo = repository
    
    @staticmethod
    def get_presets():
        # Delegate to repository
        return asyncio.run(repo.load_all())
```

### Phase 2C: Complete Migration
- All components use repository
- PresetData removed
- Full async/await throughout
- Performance optimized

## Testing Strategy

### Unit Tests
- Mock repository for service tests
- Test cache hit/miss scenarios
- Verify error handling
- Check query builder logic

### Integration Tests
- Real file I/O testing
- Cache behavior validation
- Concurrent access testing
- Performance benchmarks

### Load Tests
- 10,000+ presets
- 100+ concurrent requests
- Cache effectiveness
- Memory usage monitoring

## Future Extensions

### 1. Multi-tier Caching
```
Application → L1 Cache (Memory) → L2 Cache (Redis) → Repository
```

### 2. Read-Through/Write-Through Cache
- Automatic cache population
- Transparent write propagation
- Background refresh

### 3. Repository Plugins
- Audit logging
- Metrics collection
- Data transformation
- Encryption/decryption

### 4. Advanced Querying
- Full-text search
- Fuzzy matching
- Regular expressions
- SQL-like syntax

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cache hit rate | > 80% | Via cache stats |
| Query response time | < 10ms (cached) | Performance monitoring |
| Memory usage | < 100MB | Resource monitoring |
| Test coverage | > 90% | Coverage reports |
| Error rate | < 0.1% | Error logs |

## Key Decisions

### Why Async?
- Non-blocking I/O for better performance
- Supports concurrent operations
- Future-proof for network operations
- Compatible with modern Python frameworks

### Why Repository Pattern?
- Separation of concerns
- Testability
- Flexibility to change storage
- Consistent data access API

### Why Decorator for Caching?
- Single Responsibility Principle
- Can add/remove caching without changing repository
- Reusable across different repositories
- Configurable per instance

### Why Query Builder?
- Type-safe query construction
- Reusable query logic
- Prevents SQL injection-like issues
- Self-documenting code