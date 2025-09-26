# Phase 2 Simplified: Practical Data Layer Refactoring

## Overview
A pragmatic refactoring that replaces the static `PresetData` class with a simple, testable data manager - no over-engineering, just clean code that solves the actual problems.

## Current Problems to Solve

1. **Static class with global state** - Hard to test and maintain
2. **No separation of concerns** - Data loading mixed with filtering logic
3. **Difficult to mock** - Makes testing UI components harder
4. **No error handling** - File errors crash the app

## Simple Solution: PresetDataManager

### Core Design (One Simple Class)

```python
# src/data/preset_manager.py

from pathlib import Path
from typing import List, Set, Optional
import json
import logging
from .models.preset import Preset

logger = logging.getLogger(__name__)

class PresetDataManager:
    """
    Simple data manager for preset operations.
    No fancy patterns, just clean, testable code.
    """
    
    def __init__(self, file_path: Path):
        """Initialize with path to JSON file."""
        self.file_path = file_path
        self._presets: List[Preset] = []
        self._loaded = False
        
    def load_data(self) -> None:
        """Load presets from JSON file."""
        if self._loaded:
            return
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self._presets = [Preset.from_dict(item) for item in data]
            self._loaded = True
            logger.info(f"Loaded {len(self._presets)} presets")
            
        except FileNotFoundError:
            logger.error(f"Preset file not found: {self.file_path}")
            self._presets = []
        except Exception as e:
            logger.error(f"Error loading presets: {e}")
            self._presets = []
    
    def get_all_presets(self) -> List[Preset]:
        """Get all presets."""
        if not self._loaded:
            self.load_data()
        return self._presets
    
    def get_filtered_presets(
        self,
        packs: Optional[Set[str]] = None,
        types: Optional[Set[str]] = None,
        chars: Optional[Set[str]] = None,
        search_term: str = ""
    ) -> List[Preset]:
        """Get filtered presets - simple and straightforward."""
        presets = self.get_all_presets()
        
        # Apply filters
        if packs:
            presets = [p for p in presets if p.pack in packs]
        if types:
            presets = [p for p in presets if p.type in types]
        if chars:
            presets = [p for p in presets if set(p.chars) & chars]
        if search_term:
            presets = [p for p in presets if p.matches_search(search_term)]
        
        return presets
    
    def get_preset_by_midi(self, cc0: int, pgm: int) -> Optional[Preset]:
        """Get a specific preset by MIDI values."""
        for preset in self.get_all_presets():
            if preset.cc0 == cc0 and preset.pgm == pgm:
                return preset
        return None
    
    def get_unique_packs(self) -> List[str]:
        """Get sorted list of unique pack names."""
        packs = {p.pack for p in self.get_all_presets()}
        return sorted(packs)
    
    def get_unique_types(self) -> List[str]:
        """Get sorted list of unique preset types."""
        types = {p.type for p in self.get_all_presets()}
        return sorted(types)
    
    def get_unique_chars(self) -> List[str]:
        """Get sorted list of unique character tags."""
        chars = set()
        for preset in self.get_all_presets():
            chars.update(preset.chars)
        return sorted(chars)
    
    def reload(self) -> None:
        """Force reload of data from file."""
        self._loaded = False
        self.load_data()
```

### Integration with UI Components

```python
# src/data/app_context.py

from pathlib import Path
from .preset_manager import PresetDataManager

class AppContext:
    """Simple application context to share data manager."""
    
    def __init__(self, preset_file: Path):
        self.preset_manager = PresetDataManager(preset_file)
        self.preset_manager.load_data()
    
    def get_preset_manager(self) -> PresetDataManager:
        return self.preset_manager
```

### Updated UI Component Example

```python
# src/preset_grid.py (simplified example)

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
    
    def update_display(self):
        """Update the grid with filtered presets."""
        presets = self.preset_manager.get_filtered_presets(
            packs=self.current_filters['packs'],
            types=self.current_filters['types'],
            chars=self.current_filters['chars'],
            search_term=self.current_filters['search']
        )
        
        self.table.clear()
        for preset in presets:
            self.table.add_row(*preset.to_tuple())
    
    def set_filter(self, filter_type: str, values: List[str]):
        """Set a filter and update display."""
        if filter_type == 'pack':
            self.current_filters['packs'] = set(values)
        elif filter_type == 'type':
            self.current_filters['types'] = set(values)
        elif filter_type == 'char':
            self.current_filters['chars'] = set(values)
        
        self.update_display()
```

### Main App Initialization

```python
# src/osmose_presets.py

class OsmosePresetsApp(App):
    def __init__(self):
        super().__init__()
        # Create single data manager instance
        preset_file = Path(__file__).parent / "OsmosePresets.json"
        self.context = AppContext(preset_file)
    
    def compose(self) -> ComposeResult:
        preset_manager = self.context.get_preset_manager()
        
        # Pass data manager to components that need it
        yield PresetGrid(preset_manager, id="preset-grid")
        yield FilterSelector(preset_manager, Filters.PACK, id="pack-filter")
        # ... etc
```

## Testing Strategy

### Simple Unit Tests

```python
# tests/test_preset_manager.py

import pytest
from pathlib import Path
from src.data.preset_manager import PresetDataManager
from src.data.models.preset import Preset

class TestPresetManager:
    @pytest.fixture
    def manager(self, tmp_path):
        """Create manager with test data."""
        test_file = tmp_path / "test_presets.json"
        test_data = [
            {
                "pack": "factory",
                "type": "bass",
                "cc0": 30,
                "pgm": 0,
                "preset": "Deep Bass",
                "chars": ["warm", "analog"]
            },
            {
                "pack": "expansion_01",
                "type": "lead",
                "cc0": 30,
                "pgm": 1,
                "preset": "Bright Lead",
                "chars": ["bright", "digital"]
            }
        ]
        test_file.write_text(json.dumps(test_data))
        return PresetDataManager(test_file)
    
    def test_load_data(self, manager):
        """Test loading presets."""
        manager.load_data()
        presets = manager.get_all_presets()
        assert len(presets) == 2
        assert presets[0].preset == "Deep Bass"
    
    def test_filter_by_pack(self, manager):
        """Test filtering by pack."""
        filtered = manager.get_filtered_presets(packs={"factory"})
        assert len(filtered) == 1
        assert filtered[0].pack == "factory"
    
    def test_filter_by_type(self, manager):
        """Test filtering by type."""
        filtered = manager.get_filtered_presets(types={"bass"})
        assert len(filtered) == 1
        assert filtered[0].type == "bass"
    
    def test_combined_filters(self, manager):
        """Test multiple filters."""
        filtered = manager.get_filtered_presets(
            packs={"factory"},
            chars={"warm"}
        )
        assert len(filtered) == 1
        assert filtered[0].preset == "Deep Bass"
    
    def test_get_by_midi(self, manager):
        """Test getting preset by MIDI values."""
        preset = manager.get_preset_by_midi(30, 0)
        assert preset is not None
        assert preset.preset == "Deep Bass"
    
    def test_file_not_found(self, tmp_path):
        """Test handling of missing file."""
        manager = PresetDataManager(tmp_path / "missing.json")
        manager.load_data()
        assert manager.get_all_presets() == []
```

### Mocking for UI Tests

```python
# tests/test_ui_components.py

from unittest.mock import Mock
from src.preset_grid import PresetGrid

def test_preset_grid_filtering():
    """Test grid filtering without real data."""
    # Create mock manager
    mock_manager = Mock()
    mock_manager.get_filtered_presets.return_value = [
        create_test_preset("Test Bass", type="bass")
    ]
    
    # Test the grid
    grid = PresetGrid(mock_manager)
    grid.set_filter('type', ['bass'])
    
    # Verify the manager was called correctly
    mock_manager.get_filtered_presets.assert_called_with(
        packs=set(),
        types={'bass'},
        chars=set(),
        search_term=''
    )
```

## Migration Steps

### Step 1: Create New Files
1. Create `PresetDataManager` class
2. Create `AppContext` class
3. Add tests for new classes

### Step 2: Update Components
1. Modify `PresetGrid` to accept data manager
2. Update `FilterSelector` to use data manager
3. Update main app to create context

### Step 3: Remove Old Code
1. Delete static `PresetData` class
2. Remove global state
3. Clean up imports

## Benefits of This Approach

✅ **Simple** - One class does the job, no complex patterns
✅ **Testable** - Easy to mock and test
✅ **Maintainable** - Clear responsibilities
✅ **Practical** - Solves actual problems without over-engineering
✅ **Fast** - Data loads once, filters are quick
✅ **Flexible** - Easy to add new filter methods as needed

## What We're NOT Doing

❌ Abstract repository interfaces (YAGNI)
❌ Database support (not needed)
❌ Complex caching layers (file is small)
❌ Async operations (adds complexity for no benefit here)
❌ Multiple backend support (just JSON is fine)
❌ Query builders (simple filter methods work great)

## Timeline

- **Day 1**: Create `PresetDataManager` and tests
- **Day 2**: Create `AppContext` and update main app
- **Day 3**: Update UI components to use manager
- **Day 4**: Remove old static class
- **Day 5**: Final testing and cleanup

## Summary

This simplified Phase 2 focuses on practical improvements:
- Replace static class with instance-based manager
- Add proper error handling
- Make code testable with dependency injection
- Keep it simple and maintainable

No over-engineering, no unnecessary abstractions, just clean code that solves the real problems.