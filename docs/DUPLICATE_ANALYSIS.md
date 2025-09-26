# Duplicate CC0/PGM Analysis Report

## Executive Summary

The Osmose preset data contains **1 duplicate CC0/PGM combination** affecting 2 presets. This is a data integrity issue that should be resolved to ensure proper MIDI preset selection.

## The Duplicate

### MIDI Identifiers
- **CC0 (Bank Select):** 34
- **PGM (Program Change):** 34
- **Combined MIDI Message:** Bank 34, Program 34

### Affected Presets

| Preset Name | Pack | Type | Characteristics | 
|------------|------|------|-----------------|
| fragilkey | expansion_01 | mallets | lofi |
| feelgood resonator | expansion_01 | plucked | clean, intimate |

## Why This Is a Problem

1. **MIDI Ambiguity**: When a MIDI controller sends CC0=34, PGM=34, the system cannot determine which preset to load
2. **User Experience**: Users may get unexpected presets when selecting via MIDI
3. **Data Integrity**: Violates the principle that CC0/PGM should uniquely identify a preset

## Analysis Results

### MIDI Range Usage
- **Banks Used**: 5 out of 128 possible (CC0 values: 30-34)
- **Programs Used**: 128 out of 128 possible (PGM values: 0-127)
- **Total Presets**: 607
- **Unique Combinations**: 606 (should be 607)

### Bank Distribution
```
Bank 30: 128 presets (full)
Bank 31: 127 presets
Bank 32: 128 presets (full)
Bank 33: 127 presets
Bank 34:  97 presets (including the duplicate)
```

### Pattern Analysis
- Both duplicates are from the same pack: `expansion_01`
- They are different preset types (mallets vs plucked)
- They have different characteristics
- This appears to be an **unintentional data entry error**

## Root Cause

The duplicate likely occurred during the creation of the `expansion_01` pack. Possible scenarios:
1. Copy-paste error when adding presets
2. Manual data entry mistake
3. Automated import process that didn't validate uniqueness

## Recommended Solution

### Immediate Fix
Change `feelgood resonator` from CC0=34, PGM=34 to CC0=34, PGM=35:

```json
{
  "pack": "expansion_01",
  "type": "plucked",
  "cc0": 34,
  "pgm": 35,  // Changed from 34 to 35
  "preset": "feelgood resonator",
  "chars": ["clean", "intimate"]
}
```

**Why this fix:**
- PGM=35 in Bank 34 is currently unused
- Minimal change (only increment program number)
- Maintains preset ordering within the bank
- Keeps both presets in the same expansion pack bank

### Alternative Solutions

1. **Move to next available slot in Bank 34**
   - CC0=34, PGM=97 (next sequential available)
   - Pros: Groups at end of bank
   - Cons: Breaks any existing ordering

2. **Move to different bank**
   - CC0=35, PGM=0 (start new bank)
   - Pros: Clean separation
   - Cons: Uses a new bank for just one preset

3. **Remove one preset**
   - Not recommended as they are different presets
   - Would result in data loss

## Impact Assessment

### Current Impact
- **Low**: Only affects MIDI-based preset selection
- **Medium**: Could cause confusion during live performance
- **High**: Data integrity issue for future development

### Fix Impact
- **Backward Compatibility**: Users who have saved CC0=34, PGM=34 in their controllers will need to update
- **Documentation**: Any preset lists or manuals need updating
- **Testing**: Both presets should be tested after the fix

## Prevention Strategies

### Short Term
1. Add validation to prevent duplicate CC0/PGM combinations
2. Create unit tests to verify uniqueness
3. Add pre-commit hooks to check data integrity

### Long Term
1. Implement a preset management system with automatic CC0/PGM assignment
2. Use database constraints to enforce uniqueness
3. Create a preset editor UI with validation

## Implementation Code

### Validation Function
```python
def validate_unique_midi_identifiers(presets: List[Preset]) -> bool:
    """Validate that all CC0/PGM combinations are unique."""
    seen = set()
    duplicates = []
    
    for preset in presets:
        key = (preset.cc0, preset.pgm)
        if key in seen:
            duplicates.append(preset)
        seen.add(key)
    
    if duplicates:
        raise ValueError(f"Duplicate CC0/PGM found: {duplicates}")
    return True
```

### Automated Fix Script
```python
def fix_duplicate(data: List[dict]) -> List[dict]:
    """Fix the known duplicate in the preset data."""
    for preset in data:
        if (preset['preset'] == 'feelgood resonator' and 
            preset['cc0'] == 34 and preset['pgm'] == 34):
            preset['pgm'] = 35
            print(f"Fixed: {preset['preset']} -> CC0=34, PGM=35")
    return data
```

## Testing Requirements

After applying the fix:

1. **Load Test**: Verify both presets load correctly
2. **MIDI Test**: Send CC0=34, PGM=34 and CC0=34, PGM=35 to verify correct preset selection
3. **Integration Test**: Ensure no other systems depend on the old values
4. **Regression Test**: Verify all 607 presets still load properly

## Conclusion

The duplicate CC0/PGM combination is a clear data entry error that should be fixed. The recommended solution (changing `feelgood resonator` to PGM=35) is:
- ✅ Simple to implement
- ✅ Minimally disruptive
- ✅ Maintains data organization
- ✅ Preserves both presets

This issue highlights the need for:
1. Data validation in the preset management system
2. Automated testing for data integrity
3. Clear documentation of MIDI mapping conventions

## Action Items

- [ ] Apply the fix to change PGM from 34 to 35 for "feelgood resonator"
- [ ] Update any documentation referencing this preset's MIDI values
- [ ] Add validation to prevent future duplicates
- [ ] Create unit test to verify CC0/PGM uniqueness
- [ ] Consider implementing automated preset numbering system