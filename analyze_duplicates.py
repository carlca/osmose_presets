#!/usr/bin/env python3
"""
Analyze duplicate CC0/PGM combinations in the Osmose preset data.

This script investigates the duplicate MIDI identifiers to understand
if this is a data issue or intentional design.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data.models.preset import Preset


class DuplicateAnalyzer:
    """Analyzes duplicate CC0/PGM combinations in preset data."""
    
    def __init__(self, data_file: Path):
        """Initialize with path to preset data file."""
        self.data_file = data_file
        self.presets: List[Preset] = []
        self.raw_data: List[Dict[str, Any]] = []
        self.duplicates: Dict[Tuple[int, int], List[Preset]] = defaultdict(list)
        
    def load_data(self) -> None:
        """Load preset data from JSON file."""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        
        # Convert to Preset objects
        for item in self.raw_data:
            try:
                preset = Preset.from_dict(item)
                self.presets.append(preset)
            except Exception as e:
                print(f"Error loading preset: {e}")
                print(f"Data: {item}")
    
    def find_duplicates(self) -> None:
        """Find all duplicate CC0/PGM combinations."""
        seen = {}
        
        for preset in self.presets:
            key = (preset.cc0, preset.pgm)
            
            if key in seen:
                # Add both presets to duplicates if this is the first duplicate
                if key not in self.duplicates:
                    self.duplicates[key].append(seen[key])
                self.duplicates[key].append(preset)
            else:
                seen[key] = preset
    
    def analyze_duplicates(self) -> None:
        """Analyze and report on duplicate combinations."""
        if not self.duplicates:
            print("✅ No duplicate CC0/PGM combinations found!")
            return
        
        print(f"⚠️  Found {len(self.duplicates)} duplicate CC0/PGM combinations:\n")
        print("=" * 80)
        
        for idx, ((cc0, pgm), presets) in enumerate(self.duplicates.items(), 1):
            print(f"\n🔍 Duplicate #{idx}: CC0={cc0}, PGM={pgm}")
            print(f"   MIDI Message: Bank Select {cc0}, Program Change {pgm}")
            print(f"   Affects {len(presets)} presets:\n")
            
            for preset in presets:
                print(f"   📍 Preset: {preset.preset}")
                print(f"      Pack: {preset.pack}")
                print(f"      Type: {preset.type}")
                print(f"      Characters: {preset.display_chars}")
                
                # Check if presets are identical or different
                if idx == 1:  # Store first preset for comparison
                    first_preset = presets[0]
                
            # Analyze differences between duplicates
            print(f"\n   📊 Analysis:")
            
            # Check if all presets in this group are identical
            all_identical = all(
                p.preset == presets[0].preset and
                p.pack == presets[0].pack and
                p.type == presets[0].type and
                p.chars == presets[0].chars
                for p in presets
            )
            
            if all_identical:
                print(f"      ✅ All duplicate entries are identical (true duplicates)")
                print(f"      💡 Recommendation: Remove duplicate entries from data file")
            else:
                # Find what's different
                different_fields = []
                
                if len(set(p.preset for p in presets)) > 1:
                    different_fields.append("preset names")
                if len(set(p.pack for p in presets)) > 1:
                    different_fields.append("packs")
                if len(set(p.type for p in presets)) > 1:
                    different_fields.append("types")
                if len(set(tuple(p.chars) for p in presets)) > 1:
                    different_fields.append("characteristics")
                
                print(f"      ⚠️  Duplicate entries have different: {', '.join(different_fields)}")
                print(f"      💡 Recommendation: Assign unique CC0/PGM values to each preset")
        
        print("\n" + "=" * 80)
    
    def check_midi_range_usage(self) -> None:
        """Analyze how the MIDI range is being used."""
        print("\n📈 MIDI Range Usage Analysis:")
        print("=" * 80)
        
        cc0_values = set()
        pgm_values = set()
        combinations = set()
        
        for preset in self.presets:
            cc0_values.add(preset.cc0)
            pgm_values.add(preset.pgm)
            combinations.add((preset.cc0, preset.pgm))
        
        print(f"   CC0 (Bank Select) values used: {len(cc0_values)} out of 128 possible")
        print(f"   PGM (Program Change) values used: {len(pgm_values)} out of 128 possible")
        print(f"   Unique CC0/PGM combinations used: {len(combinations)} out of 16,384 possible")
        print(f"   Total presets: {len(self.presets)}")
        
        # Show CC0 distribution
        cc0_distribution = defaultdict(int)
        for preset in self.presets:
            cc0_distribution[preset.cc0] += 1
        
        print(f"\n   📊 Bank (CC0) Distribution:")
        for cc0 in sorted(cc0_distribution.keys()):
            count = cc0_distribution[cc0]
            print(f"      Bank {cc0:3d}: {count:3d} presets {'█' * (count // 10)}")
        
        # Check for gaps in numbering
        all_combinations = sorted(combinations)
        print(f"\n   🔢 CC0/PGM Range:")
        print(f"      First: CC0={all_combinations[0][0]}, PGM={all_combinations[0][1]}")
        print(f"      Last:  CC0={all_combinations[-1][0]}, PGM={all_combinations[-1][1]}")
        
        # Check if numbering is sequential or has gaps
        expected_sequential = len(self.presets)
        if len(combinations) < expected_sequential:
            print(f"\n   ⚠️  Numbering has gaps or duplicates")
            print(f"      Expected {expected_sequential} unique combinations")
            print(f"      Found {len(combinations)} unique combinations")
    
    def suggest_fix(self) -> None:
        """Suggest how to fix the duplicate issue."""
        if not self.duplicates:
            return
        
        print("\n💡 Suggested Fixes:")
        print("=" * 80)
        
        for (cc0, pgm), presets in self.duplicates.items():
            print(f"\n   For CC0={cc0}, PGM={pgm} duplicates:")
            
            # Check if they're identical
            all_identical = all(
                p.preset == presets[0].preset and
                p.pack == presets[0].pack and
                p.type == presets[0].type and
                p.chars == presets[0].chars
                for p in presets
            )
            
            if all_identical:
                print(f"   1. Remove duplicate entry for '{presets[0].preset}'")
                print(f"      Keep only one instance in the JSON file")
            else:
                print(f"   1. Assign unique CC0/PGM values:")
                # Find next available combinations
                used_combinations = {(p.cc0, p.pgm) for p in self.presets}
                
                suggestions = []
                for i, preset in enumerate(presets[1:], 1):  # Skip first, keep it as is
                    # Try to find next available PGM in same bank
                    new_pgm = pgm
                    while (cc0, new_pgm) in used_combinations:
                        new_pgm += 1
                        if new_pgm > 127:
                            # Move to next bank
                            cc0 += 1
                            new_pgm = 0
                    
                    suggestions.append((preset, cc0, new_pgm))
                    used_combinations.add((cc0, new_pgm))
                
                for preset, new_cc0, new_pgm in suggestions:
                    print(f"      '{preset.preset}' -> CC0={new_cc0}, PGM={new_pgm}")
    
    def export_fixed_data(self) -> None:
        """Export a fixed version of the data without duplicates."""
        if not self.duplicates:
            print("\n✅ No fixes needed - data is already unique!")
            return
        
        print("\n📝 Exporting Fixed Data:")
        print("=" * 80)
        
        # Create a mapping of presets to their new CC0/PGM values
        fixes = {}
        used_combinations = {(p.cc0, p.pgm) for p in self.presets}
        
        for (cc0, pgm), presets in self.duplicates.items():
            # Keep the first preset as-is
            for preset in presets[1:]:
                # Find next available combination
                new_cc0, new_pgm = cc0, pgm
                while (new_cc0, new_pgm) in used_combinations:
                    new_pgm += 1
                    if new_pgm > 127:
                        new_cc0 += 1
                        new_pgm = 0
                
                fixes[preset] = (new_cc0, new_pgm)
                used_combinations.add((new_cc0, new_pgm))
        
        # Create fixed data
        fixed_data = []
        seen_presets = set()
        
        for item in self.raw_data:
            preset = Preset.from_dict(item)
            
            # Skip true duplicates (identical presets)
            preset_key = (preset.preset, preset.pack, preset.type, tuple(preset.chars))
            if preset_key in seen_presets:
                print(f"   Removing duplicate: {preset.preset}")
                continue
            seen_presets.add(preset_key)
            
            # Apply fixes for different presets with same CC0/PGM
            if preset in fixes:
                new_cc0, new_pgm = fixes[preset]
                item = item.copy()
                item['cc0'] = new_cc0
                item['pgm'] = new_pgm
                print(f"   Fixed: {preset.preset} -> CC0={new_cc0}, PGM={new_pgm}")
            
            fixed_data.append(item)
        
        # Save to new file
        output_file = self.data_file.parent / "OsmosePresets_fixed.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n   ✅ Fixed data saved to: {output_file}")
        print(f"   Original presets: {len(self.raw_data)}")
        print(f"   Fixed presets: {len(fixed_data)}")
        print(f"   Removed: {len(self.raw_data) - len(fixed_data)} duplicate entries")
    
    def run(self) -> None:
        """Run the complete analysis."""
        print("\n🔍 Osmose Preset Duplicate CC0/PGM Analysis")
        print("=" * 80)
        
        print(f"\n📁 Loading data from: {self.data_file}")
        self.load_data()
        print(f"   Loaded {len(self.presets)} presets")
        
        print("\n🔎 Searching for duplicates...")
        self.find_duplicates()
        
        self.analyze_duplicates()
        self.check_midi_range_usage()
        self.suggest_fix()
        
        # Uncomment the following to export a fixed version:
        # if self.duplicates:
        #     print("\n" + "=" * 80)
        #     self.export_fixed_data()


def main():
    """Main entry point."""
    data_file = Path(__file__).parent / "src" / "OsmosePresets.json"
    
    if not data_file.exists():
        print(f"❌ Error: Data file not found at {data_file}")
        sys.exit(1)
    
    analyzer = DuplicateAnalyzer(data_file)
    analyzer.run()


if __name__ == "__main__":
    main()