#!/bin/bash
# filter_std_calls.sh
# Filters out all std:: function calls from gprof output

if [ $# -ne 2 ]; then
  echo "Usage: $0 <input_gprof_file> <output_filtered_file>"
  echo "Example: $0 gprof_output.txt gprof_filtered.txt"
  exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: Input file '$INPUT_FILE' not found"
  exit 1
fi

echo "Filtering std:: calls from $INPUT_FILE..."

# Use sed to remove lines containing std:: functions
# This preserves the structure but removes std:: entries
sed '/std::/d' "$INPUT_FILE" >"$OUTPUT_FILE"

# Count removed lines
ORIGINAL_LINES=$(wc -l <"$INPUT_FILE")
FILTERED_LINES=$(wc -l <"$OUTPUT_FILE")
REMOVED_LINES=$((ORIGINAL_LINES - FILTERED_LINES))

echo "Filtering complete!"
echo "Original lines: $ORIGINAL_LINES"
echo "Filtered lines: $FILTERED_LINES"
echo "Removed lines: $REMOVED_LINES"
echo "Output written to: $OUTPUT_FILE"
