import csv
import json
import io
import os

# Determine the absolute path to the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(SCRIPT_DIR, "OsmosePresetsResources.txt")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "OsmosePresetsResources.json")

# Content of lines to skip (after stripping whitespace from the line in the file)
SKIP_LINES_CONTENT = [
    "nada",
    '31, 15, "empty", "UNASSIGNED"',
    '33, 88, "testbench", "UNASSIGNED"'
]

# Mapping from internal descriptive names to final JSON key names
JSON_KEYS = {
    "pack": "pack",
    "type": "type",
    "cc0": "cc0",
    "pgm": "pgm",
    "preset_name": "preset name",
    "characters": "characters"
}

def parse_characters_list(char_string):
    """
    Parses the character string (e.g., "tag1 + tag2 + tag3") into a list of strings.
    Handles "UNASSIGNED" and empty strings.
    """
    char_string = char_string.strip() # Ensure no leading/trailing whitespace on the whole string
    if not char_string: # Handles empty string from CSV like ""
        return []
    if char_string == "UNASSIGNED":
        return ["UNASSIGNED"]
    # Split by '+' and strip whitespace from each individual tag
    return [tag.strip() for tag in char_string.split('+') if tag.strip()]

def main():
    all_presets = []
    lines_for_csv_processing = []
    
    original_line_number = 0
    skipped_for_content = 0
    
    # --- Stage 1: Read file and filter out lines to be skipped entirely ---
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
            for raw_line in infile:
                original_line_number += 1
                stripped_line = raw_line.strip()
                
                if not stripped_line: # Skip blank lines
                    skipped_for_content += 1
                    continue
                if stripped_line in SKIP_LINES_CONTENT:
                    skipped_for_content += 1
                    continue
                
                lines_for_csv_processing.append({"content": stripped_line, "original_line": original_line_number})
                
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading input file: {e}")
        return

    # --- Stage 2: Process valid lines using CSV parsing ---
    processed_items = 0
    warning_count = 0

    # Use io.StringIO to feed the list of valid lines to csv.reader
    # Each item in lines_for_csv_processing is a dictionary
    csv_text_input = "\n".join([item["content"] for item in lines_for_csv_processing])
    csv_file_like_object = io.StringIO(csv_text_input)
    
    # skipinitialspace=True handles potential spaces after delimiters, e.g., "field1", "field2"
    csv_reader = csv.reader(csv_file_like_object, delimiter=',', quotechar='"', skipinitialspace=True)

    for idx, raw_fields in enumerate(csv_reader):
        # Get original line number for accurate error reporting
        current_line_meta = lines_for_csv_processing[idx]
        line_num_for_reporting = current_line_meta["original_line"]
        original_content_for_reporting = current_line_meta["content"]

        # Strip whitespace from each field that csv.reader parsed
        fields = [field.strip() for field in raw_fields]
        
        preset_data = {}
        try:
            num_fields = len(fields)
            
            # Standard case: "pack", "type", cc0, pgm, "name", "characters_string"
            if num_fields == 6:
                pack_val = fields[0]
                type_val = fields[1]
                cc0_val = int(fields[2])
                pgm_val = int(fields[3])
                name_val = fields[4]
                characters_list = parse_characters_list(fields[5])
            # Case where 'type' might be split: "pack", "type_part1", "type_part2_unquoted", cc0, pgm, "name", "characters_string"
            elif num_fields == 7:
                pack_val = fields[0]
                type_val = f"{fields[1]} {fields[2]}" # Combine type parts
                cc0_val = int(fields[3])
                pgm_val = int(fields[4])
                name_val = fields[5]
                characters_list = parse_characters_list(fields[6])
            # Case where 'characters_string' might be missing: "pack", "type", cc0, pgm, "name"
            elif num_fields == 5:
                pack_val = fields[0]
                type_val = fields[1]
                cc0_val = int(fields[2])
                pgm_val = int(fields[3])
                name_val = fields[4]
                characters_list = [] # Assume empty characters list
            else:
                print(f"Warning (L{line_num_for_reporting}): Unexpected number of fields ({num_fields}). Line: '{original_content_for_reporting}'. Parsed fields: {fields}")
                warning_count +=1
                continue

            preset_data[JSON_KEYS["pack"]] = pack_val
            preset_data[JSON_KEYS["type"]] = type_val
            preset_data[JSON_KEYS["cc0"]] = cc0_val
            preset_data[JSON_KEYS["pgm"]] = pgm_val
            preset_data[JSON_KEYS["preset_name"]] = name_val
            preset_data[JSON_KEYS["characters"]] = characters_list
            
            all_presets.append(preset_data)
            processed_items += 1

        except ValueError as e: # For int() conversion errors
            print(f"Warning (L{line_num_for_reporting}): Type conversion error. Line: '{original_content_for_reporting}'. Fields: {fields}. Error: {e}")
            warning_count +=1
            continue
        except IndexError as e: # If a field is unexpectedly missing
            print(f"Warning (L{line_num_for_reporting}): Index error (missing field). Line: '{original_content_for_reporting}'. Fields: {fields}. Error: {e}")
            warning_count +=1
            continue
        except Exception as e: # Catch any other unexpected errors during field processing
            print(f"Warning (L{line_num_for_reporting}): Unexpected error processing fields. Line: '{original_content_for_reporting}'. Fields: {fields}. Error: {e}")
            warning_count +=1
            continue
            
    # --- Stage 3: Write the collected data to JSON file ---
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
            # ensure_ascii=False to allow non-ASCII characters directly in JSON
            # indent=4 for pretty printing
            json.dump(all_presets, outfile, indent=4, ensure_ascii=False)
        
        print(f"Successfully converted {processed_items} presets to '{OUTPUT_FILE}'.")
        if skipped_for_content > 0:
            print(f"Skipped {skipped_for_content} lines based on content (blank or in skip list).")
        if warning_count > 0:
            print(f"Encountered {warning_count} warnings during processing. Please check console output for details.")
            
    except Exception as e:
        print(f"An error occurred while writing JSON file '{OUTPUT_FILE}': {e}")

if __name__ == "__main__":
    main()