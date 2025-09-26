# Phase 3 Preview: Business Logic Layer

## Overview
Phase 3 introduces a thin service layer that centralizes business logic, making the UI components simpler and the application easier to maintain. No over-engineering - just practical separation of concerns.

## Current Problems to Solve

1. **Business logic scattered in UI components** - Filtering logic mixed with display code
2. **State management is complex** - Each component manages its own filter state
3. **Duplicate logic** - Similar filtering code in multiple places
4. **Hard to add new features** - Need to modify multiple components

## Simple Solution: Service Layer

### Core Design - Three Simple Services

```
┌─────────────────────────────────────────────────┐
│                UI Components                     │
│         (PresetGrid, FilterSelector)             │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              Service Layer (Phase 3)             │
├───────────────────────────────────────────────────┤
│  PresetService    FilterService    SearchService │
│  (Main logic)     (Filter state)   (Search logic)│
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│           Data Layer (Phase 2 - Done)            │
│         (PresetDataManager, AppContext)          │
└─────────────────────────────────────────────────┘
```

## Implementation Plan

### 1. FilterService - Manages Filter State
```python
# src/services/filter_service.py

from typing import Set, Optional
from dataclasses import dataclass, field

@dataclass
class FilterState:
    """Current filter selections."""
    packs: Set[str] = field(default_factory=set)
    types: Set[str] = field(default_factory=set)
    chars: Set[str] = field(default_factory=set)
    search_term: str = ""
    
    def clear(self):
        """Clear all filters."""
        self.packs.clear()
        self.types.clear()
        self.chars.clear()
        self.search_term = ""
    
    def is_active(self) -> bool:
        """Check if any filters are active."""
        return bool(self.packs or self.types or self.chars or self.search_term)

class FilterService:
    """Manages application-wide filter state."""
    
    def __init__(self):
        self.state = FilterState()
        self._listeners = []
    
    def set_pack_filter(self, packs: Set[str]):
        """Update pack filter."""
        self.state.packs = packs
        self._notify_listeners()
    
    def set_type_filter(self, types: Set[str]):
        """Update type filter."""
        self.state.types = types
        self._notify_listeners()
    
    def set_char_filter(self, chars: Set[str]):
        """Update character filter."""
        self.state.chars = chars
        self._notify_listeners()
    
    def set_search(self, search_term: str):
        """Update search term."""
        self.state.search_term = search_term
        self._notify_listeners()
    
    def clear_filters(self):
        """Clear all filters."""
        self.state.clear()
        self._notify_listeners()
    
    def add_listener(self, callback):
        """Add a callback for filter changes."""
        self._listeners.append(callback)
    
    def _notify_listeners(self):
        """Notify all listeners of filter change."""
        for callback in self._listeners:
            callback(self.state)
```

### 2. PresetService - Main Business Logic
```python
# src/services/preset_service.py

from typing import List, Optional
from data.preset_manager import PresetDataManager
from data.models.preset import Preset
from .filter_service import FilterService

class PresetService:
    """Main service for preset operations."""
    
    def __init__(self, preset_manager: PresetDataManager, filter_service: FilterService):
        self.preset_manager = preset_manager
        self.filter_service = filter_service
        
        # Listen to filter changes
        self.filter_service.add_listener(self._on_filter_change)
        self._listeners = []
        
    def get_filtered_presets(self) -> List[Preset]:
        """Get presets based on current filters."""
        state = self.filter_service.state
        
        return self.preset_manager.get_filtered_presets(
            packs=state.packs or None,
            types=state.types or None,
            chars=state.chars or None,
            search_term=state.search_term
        )
    
    def get_preset_by_midi(self, cc0: int, pgm: int) -> Optional[Preset]:
        """Get a specific preset by MIDI values."""
        return self.preset_manager.get_preset_by_midi(cc0, pgm)
    
    def get_available_packs(self) -> List[str]:
        """Get all available pack names."""
        return self.preset_manager.get_unique_packs()
    
    def get_available_types(self) -> List[str]:
        """Get all available preset types."""
        return self.preset_manager.get_unique_types()
    
    def get_available_chars(self) -> List[str]:
        """Get all available character tags."""
        return self.preset_manager.get_unique_chars()
    
    def add_listener(self, callback):
        """Add a callback for preset changes."""
        self._listeners.append(callback)
    
    def _on_filter_change(self, filter_state):
        """Handle filter changes."""
        # Notify listeners that presets may have changed
        for callback in self._listeners:
            callback()
```

### 3. Updated AppContext - Wire Services Together
```python
# src/services/app_services.py

from pathlib import Path
from data.app_context import AppContext
from .preset_service import PresetService
from .filter_service import FilterService

class AppServices:
    """Container for all application services."""
    
    def __init__(self, preset_file: Path = None):
        # Create data layer
        self.app_context = AppContext(preset_file)
        
        # Create services
        self.filter_service = FilterService()
        self.preset_service = PresetService(
            self.app_context.get_preset_manager(),
            self.filter_service
        )
    
    def get_preset_service(self) -> PresetService:
        return self.preset_service
    
    def get_filter_service(self) -> FilterService:
        return self.filter_service
```

## Updated UI Components

### Simplified PresetGrid
```python
# src/preset_grid.py - Simplified with services

class PresetGrid(Vertical):
    def __init__(self, preset_service: PresetService, **kwargs):
        super().__init__(**kwargs)
        self.preset_service = preset_service
        
        # Listen for changes
        self.preset_service.add_listener(self.refresh)
    
    def refresh(self):
        """Refresh display with current presets."""
        presets = self.preset_service.get_filtered_presets()
        
        self.table.clear(columns=False)
        for preset in presets:
            self.table.add_row(*preset.to_tuple())
    
    # No more filter management here! Much simpler!
```

### Simplified FilterSelector
```python
# src/filter_selector.py - Simplified with services

class FilterSelector(VerticalScroll):
    def __init__(self, preset_service: PresetService, 
                 filter_service: FilterService,
                 filter_type: Filters, **kwargs):
        super().__init__(**kwargs)
        self.preset_service = preset_service
        self.filter_service = filter_service
        self.filter_type = filter_type
    
    def on_checkbox_changed(self, event: Checkbox.Changed):
        """Handle checkbox changes."""
        selected = self.get_selected_filters()
        
        # Update filter service based on type
        if self.filter_type == Filters.PACK:
            self.filter_service.set_pack_filter(set(selected))
        elif self.filter_type == Filters.TYPE:
            self.filter_service.set_type_filter(set(selected))
        elif self.filter_type == Filters.CHAR:
            self.filter_service.set_char_filter(set(selected))
        
        # That's it! Service handles the rest
```

### Updated Main App
```python
# src/osmose_presets.py

from services.app_services import AppServices

class OsmosePresetsApp(App):
    def __init__(self):
        super().__init__()
        # Create all services
        self.services = AppServices()
        
    def compose(self) -> ComposeResult:
        preset_service = self.services.get_preset_service()
        filter_service = self.services.get_filter_service()
        
        # Pass services to components
        yield PresetGrid(
            preset_service=preset_service,
            id="preset-grid"
        )
        yield FilterSelector(
            preset_service=preset_service,
            filter_service=filter_service,
            filter_type=Filters.PACK,
            id="pack-container"
        )
        # etc...
```

## Benefits of This Approach

### 1. **Cleaner UI Components**
- Components only handle display
- No complex filter state management
- No business logic

### 2. **Centralized State**
- Single source of truth for filters
- Easy to add filter persistence
- Simple to debug

### 3. **Easier Testing**
```python
def test_filter_service():
    service = FilterService()
    
    # Test filter updates
    service.set_pack_filter({'factory'})
    assert service.state.packs == {'factory'}
    
    # Test clear
    service.clear_filters()
    assert not service.state.is_active()
```

### 4. **Easy to Extend**
Want to add filter presets? Just add to FilterService:
```python
def save_filter_preset(self, name: str):
    """Save current filter state as a preset."""
    self.presets[name] = copy.deepcopy(self.state)

def load_filter_preset(self, name: str):
    """Load a saved filter preset."""
    if name in self.presets:
        self.state = copy.deepcopy(self.presets[name])
        self._notify_listeners()
```

## What We're NOT Doing

❌ Complex event bus systems
❌ Abstract service interfaces
❌ Dependency injection frameworks
❌ Complex state management libraries
❌ Over-abstracted patterns

## Implementation Steps

### Day 1: Create Services
1. Create `FilterService` class
2. Create `PresetService` class
3. Create `AppServices` container
4. Write tests

### Day 2: Update UI Components
1. Update `PresetGrid` to use services
2. Update `FilterSelector` to use services
3. Update main app

### Day 3: Testing & Polish
1. Integration tests
2. Fix any issues
3. Documentation

## Testing Strategy

```python
# tests/test_filter_service.py

def test_filter_state():
    """Test filter state management."""
    service = FilterService()
    
    # Test individual filters
    service.set_pack_filter({'factory'})
    assert service.state.packs == {'factory'}
    
    # Test listeners
    called = False
    def callback(state):
        nonlocal called
        called = True
    
    service.add_listener(callback)
    service.set_type_filter({'bass'})
    assert called

# tests/test_preset_service.py

def test_preset_service():
    """Test preset service operations."""
    mock_manager = Mock()
    filter_service = FilterService()
    
    service = PresetService(mock_manager, filter_service)
    
    # Test filter integration
    filter_service.set_pack_filter({'factory'})
    service.get_filtered_presets()
    
    mock_manager.get_filtered_presets.assert_called_with(
        packs={'factory'},
        types=None,
        chars=None,
        search_term=""
    )
```

## Migration Path

1. **Create services alongside existing code**
2. **Update components one at a time**
3. **Remove old filter logic from components**
4. **Clean up and document**

## Summary

Phase 3 adds a thin service layer that:
- **Centralizes business logic** in one place
- **Simplifies UI components** significantly
- **Makes testing easier** with clear responsibilities
- **Enables new features** without touching UI code
- **Stays simple and practical** - no over-engineering

The result is cleaner, more maintainable code that's easier to understand and extend.