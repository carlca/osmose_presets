# Phase 2 Migration Guide: From Static PresetData to PresetDataManager

## Overview
This guide explains how to migrate from the static `PresetData` class to the new `PresetDataManager` with dependency injection.

## What's Changed

### Old Architecture (Static Class)
```python
# Global state with static methods
class PresetData:
    cached_presets = []  # Class variable
    pack_filters = []    # Class variable
    
    @staticmethod
    def get_presets():
        # Operates on class variables
```

### New Architecture (Dependency Injection)
```python
# Instance-based with no global state
class PresetDataManager:
    def __init__(self, file_path: Path):
        self._presets = []  # Instance variable
    
    def get_filtered_presets(...):
        # Operates on instance variables
```

## Migration Options

### Option 1: Quick Migration (Using Compatibility Layer)

**When to use**: For immediate migration with minimal code changes.

1. Replace import:
```python
# Old
from preset_data import PresetData

# New (compatibility mode)
from preset_data_compat import PresetData
```

2. Continue using existing code - it will work with the compatibility layer.

### Option 2: Proper Migration (Recommended)

**When to use**: For new code or when refactoring components.

#### Step 1: Update Main Application

```python
# src/osmose_presets.py

from data import AppContext
from pathlib import Path

class OsmosePresetsApp(App):
    def __init__(self):
        super().__init__()
        # Create application context
        preset_file = Path(__file__).parent / "OsmosePresets.json"
        self.app_context = AppContext(preset_file)
        
    def compose(self) -> ComposeResult:
        # Get the preset manager
        preset_manager = self.app_context.get_preset_manager()
        
        # Pass to components that need it
        yield PresetGrid(preset_manager=preset_manager, id="preset-grid")
        yield FilterSelector(
            preset_manager=preset_manager,
            filter_type=Filters.PACK,
            id="pack-container"
        )
```

#### Step 2: Update PresetGrid Component

```python
# src/preset_grid.py

from data.preset_manager import PresetDataManager

class PresetGrid(Vertical):
    def __init__(self, preset_manager: PresetDataManager, **kwargs):
        super().__init__(**kwargs)
        self.preset_manager = preset_manager
        self.current_filters = {
            'packs': set(),
            'types': set(), 
            'chars': set(),
            'search': ''
        }
    
    def set_filter(self, filter_type: str, selected_filters: list[str]):
        """Apply filters using the preset manager."""
        if filter_type == "pack":
            self.current_filters['packs'] = set(selected_filters)
        elif filter_type == "type":
            self.current_filters['types'] = set(selected_filters)
        elif filter_type == "char":
            self.current_filters['chars'] = set(selected_filters)
        
        self.update_display()
    
    def set_search_filter(self, search_term: str):
        """Apply search filter."""
        self.current_filters['search'] = search_term
        self.update_display()
    
    def update_display(self):
        """Update table with filtered presets."""
        # Get filtered presets from manager
        presets = self.preset_manager.get_filtered_presets(
            packs=self.current_filters['packs'] or None,
            types=self.current_filters['types'] or None,
            chars=self.current_filters['chars'] or None,
            search_term=self.current_filters['search']
        )
        
        # Update table
        self.table.clear(columns=False)
        for preset in presets:
            self.table.add_row(*preset.to_tuple())
```

#### Step 3: Update FilterSelector Component

```python
# src/filter_selector.py

from data.preset_manager import PresetDataManager

class FilterSelector(VerticalScroll):
    def __init__(self, preset_manager: PresetDataManager, 
                 filter_type: Filters, select_all=False, **kwargs):
        super().__init__(**kwargs)
        self.preset_manager = preset_manager
        self.filter = filter_type
        self.select_all = select_all
    
    def get_filter_names(self) -> list[str]:
        """Get available filter options from preset manager."""
        match self.filter:
            case Filters.PACK:
                return self.preset_manager.get_unique_packs()
            case Filters.TYPE:
                return self.preset_manager.get_unique_types()
            case Filters.CHAR:
                return self.preset_manager.get_unique_chars()
            case _:
                return []
```

## Migration Mapping

| Old Method | New Method |
|------------|------------|
| `PresetData.get_presets()` | `manager.get_filtered_presets(...)` |
| `PresetData.get_all_presets()` | `manager.get_all_presets()` |
| `PresetData.get_packs()` | `manager.get_unique_packs()` |
| `PresetData.get_types()` | `manager.get_unique_types()` |
| `PresetData.get_chars()` | `manager.get_unique_chars()` |
| `PresetData.add_pack_filter(...)` | Pass to `get_filtered_presets(packs=...)` |
| `PresetData.add_type_filter(...)` | Pass to `get_filtered_presets(types=...)` |
| `PresetData.add_char_filter(...)` | Pass to `get_filtered_presets(chars=...)` |
| `PresetData.set_search_filter(...)` | Pass to `get_filtered_presets(search_term=...)` |
| `PresetData.preset_to_tuple(p)` | `preset.to_tuple()` |
| `PresetData.get_presets_as_tuples()` | `manager.get_presets_as_tuples(...)` |

## Testing with the New Architecture

### Unit Testing Components

```python
# tests/test_preset_grid.py

from unittest.mock import Mock, MagicMock
from src.preset_grid import PresetGrid
from data.models.preset import Preset

def test_preset_grid_filtering():
    # Create mock manager
    mock_manager = Mock()
    mock_preset = Preset(
        pack="factory",
        type="bass",
        cc0=30,
        pgm=0,
        preset="Test Bass",
        chars=["warm"]
    )
    mock_manager.get_filtered_presets.return_value = [mock_preset]
    
    # Test the grid
    grid = PresetGrid(preset_manager=mock_manager)
    grid.set_filter('type', ['bass'])
    
    # Verify manager was called correctly
    mock_manager.get_filtered_presets.assert_called_with(
        packs=None,
        types={'bass'},
        chars=None,
        search_term=''
    )
```

### Integration Testing

```python
# tests/test_integration.py

from pathlib import Path
from data import AppContext
import json

def test_app_context_integration(tmp_path):
    # Create test data
    test_file = tmp_path / "test.json"
    test_data = [{
        "pack": "factory",
        "type": "bass",
        "cc0": 30,
        "pgm": 0,
        "preset": "Test",
        "chars": ["warm"]
    }]
    test_file.write_text(json.dumps(test_data))
    
    # Create context and test
    context = AppContext(test_file)
    manager = context.get_preset_manager()
    
    presets = manager.get_all_presets()
    assert len(presets) == 1
    assert presets[0].preset == "Test"
```

## Common Migration Issues and Solutions

### Issue 1: Global State Dependencies
**Problem**: Code relies on global `PresetData.pack_filters` being set elsewhere.

**Solution**: Pass filters explicitly to components or store in component state:
```python
# Instead of relying on global PresetData.pack_filters
# Store filters in component and pass to manager
self.current_filters = {'packs': set(['factory'])}
presets = self.manager.get_filtered_presets(packs=self.current_filters['packs'])
```

### Issue 2: Import Errors
**Problem**: `ImportError: cannot import name 'PresetData'`

**Solution**: Use compatibility layer during migration:
```python
# Temporary fix
from preset_data_compat import PresetData

# Or update to new import
from data import PresetDataManager
```

### Issue 3: Missing Preset Manager
**Problem**: Component expects preset manager but doesn't receive it.

**Solution**: Ensure manager is passed from parent:
```python
# In parent component
manager = self.app.app_context.get_preset_manager()
yield ChildComponent(preset_manager=manager)
```

## Benefits After Migration

✅ **Testability**: Easy to mock preset manager for unit tests
✅ **No Global State**: Each component gets its own manager reference
✅ **Error Handling**: Graceful handling of missing/invalid files
✅ **Type Safety**: Full type hints for better IDE support
✅ **Performance**: Data loads once, no repeated file I/O
✅ **Flexibility**: Easy to switch data sources in the future

## Migration Checklist

- [ ] Create `PresetDataManager` and `AppContext` classes
- [ ] Add comprehensive tests for new classes
- [ ] Update main app to create `AppContext`
- [ ] Update `PresetGrid` to accept preset manager
- [ ] Update `FilterSelector` to accept preset manager
- [ ] Update `HeaderPanel` if it uses preset data
- [ ] Remove static filter state from components
- [ ] Run all tests to ensure nothing is broken
- [ ] Remove old `PresetData` class
- [ ] Remove compatibility layer (after full migration)
- [ ] Update documentation

## Timeline Estimate

- **Day 1**: Implement PresetDataManager and tests ✅
- **Day 2**: Implement AppContext and tests ✅
- **Day 3**: Update main app and PresetGrid
- **Day 4**: Update FilterSelector and other components
- **Day 5**: Testing, cleanup, and documentation

## Next Steps

After completing Phase 2, the codebase will be ready for:
- Phase 3: Service layer for business logic
- Phase 4: UI component improvements
- Future: Alternative data sources (database, API)