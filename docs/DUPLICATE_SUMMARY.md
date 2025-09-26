# Duplicate CC0/PGM Issue Summary

## Quick Facts
- **Issue**: 1 duplicate MIDI identifier (CC0=34, PGM=34)
- **Affected Presets**: 2 different presets from `expansion_01` pack
- **Impact**: MIDI ambiguity - system cannot determine which preset to load
- **Resolution**: DO NOT modify data without explicit permission

## The Duplicate

| CC0 | PGM | Preset Name | Pack | Type | Characters |
|-----|-----|-------------|------|------|------------|
| 34 | 34 | fragilkey | expansion_01 | mallets | lofi |
| 34 | 34 | feelgood resonator | expansion_01 | plucked | clean, intimate |

## Why This Matters

When a MIDI device sends Bank Select (CC0) = 34 and Program Change (PGM) = 34:
- The system receives an ambiguous command
- Either "fragilkey" or "feelgood resonator" could be loaded
- Behavior is unpredictable and may vary by implementation

## Additional Findings

### MIDI Space Usage
- **607 total presets** using **606 unique combinations**
- Banks used: 30-34 (5 out of 128 possible)
- Programs used: 0-127 (all available per bank)
- Available slot for fix: CC0=34, PGM=35 is unused

### Gaps in Numbering
The following PGM numbers are unused (not errors, just gaps):
- Bank 31: PGM 15 is unused
- Bank 33: PGM 88 is unused  
- Bank 34: PGM 35 is unused (perfect for the fix)

## Test Coverage

Created comprehensive data integrity tests that:
- ✅ Detect the duplicate (test marked as expected failure)
- ✅ Verify all MIDI values are in valid range (0-127)
- ✅ Confirm suggested fix location is available
- ✅ Document bank organization and gaps
- ✅ Validate data completeness

## Recommended Solution

**When authorized to modify data:**

Change "feelgood resonator" from PGM=34 to PGM=35:
```json
{
  "pack": "expansion_01",
  "type": "plucked", 
  "cc0": 34,
  "pgm": 35,  // Changed from 34
  "preset": "feelgood resonator",
  "chars": ["clean", "intimate"]
}
```

This is the minimal change that:
- Resolves the ambiguity
- Uses an available slot in the same bank
- Maintains logical ordering
- Requires only a single value change

## Current Status

- **Data**: Unchanged (no modifications made)
- **Tests**: Implemented and passing (duplicate test expected to fail)
- **Documentation**: Complete analysis available
- **Action Required**: Authorization to apply fix to JSON data