#!/bin/bash

# Define the directory containing your binaries
BIN_DIR="./bin/"

# Define the script you want to run for each binary
SCRIPT_TO_RUN="./pipeline.sh"

# Ensure the directory exists
if [ ! -d "$BIN_DIR" ]; then
  echo "Error: Directory '$BIN_DIR' not found."
  exit 1
fi

# Loop through each file in the specified directory
for file in "$BIN_DIR"/*; do
  # Check if the file is an executable (binary)
  if [ -x "$file" ]; then
    echo "Executing '$SCRIPT_TO_RUN' for binary: '$file'"
    "$SCRIPT_TO_RUN" "$file"
  fi
done

echo "Finished processing all files."
