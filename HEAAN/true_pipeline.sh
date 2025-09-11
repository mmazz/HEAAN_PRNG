#!/usr/bin/env bash
set -euo pipefail

BIN_DIR=./bin

for bin in "$BIN_DIR"/*; do
  name=$(basename "$bin")
  echo "▶ Running $name ..."

  # Run binary (produces gmon.out)
  ./"$bin" >/dev/null 2>&1

  # Run gprof
  gprof "$bin" gmon.out >"${name}_gprof"

  # Parse call graph
  python3 ./scripts/parse_calls.py "${name}_gprof" >/dev/null
  mv callgraph_edges_correct.csv "${name}_calls.csv"

  # Parse functions
  python3 ./scripts/parse_functions.py "${name}_gprof" >/dev/null
  mv functions.csv "${name}_functions.csv"

  # Extract disassembly
  python3 extract_asm.py "${name}_functions.csv" "$bin" >"${name}_disassembly.s"

  # Count instructions
  python3 count_instructions.py "${name}_disassembly.s" "${name}_functions.csv" "${name}_instructions"

  mv "${name}_instructions" ./instruction_count/.

  rm test*

  echo "✅ Done with $name"
done
