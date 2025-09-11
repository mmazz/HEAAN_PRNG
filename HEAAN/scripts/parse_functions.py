#!/usr/bin/env python3
import re
import csv
import sys

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <gprof_output.txt>")
    sys.exit(1)

filename = sys.argv[1]

func_re = re.compile(
    r"^\[(\d+)\]\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)(?:\s+(\d+))?\s+(.*) \[\d+\]"
)
functions = {}

with open(filename) as f:
    current_func = None
    for line in f:
        line = line.rstrip()

        # Function header line
        m = func_re.match(line)
        if m:
            fid = int(m.group(1))
            functions[fid] = {
                "id": fid,
                "name": m.group(6).strip(),
                "total_calls": int(m.group(5) or 0),
                "instructions": None
            }
            current_func = fid
            continue

# Write functions.csv
with open("functions.csv", "w", newline="") as fcsv:
    writer = csv.DictWriter(fcsv, fieldnames=["func_id", "func_name", "total_calls", "instructions_executed"])
    writer.writeheader()
    for func in functions.values():
        writer.writerow({
            "func_id": func["id"],
            "func_name": func["name"],
            "total_calls": func["total_calls"],
            "instructions_executed": func["instructions"] or ""
        })

print("✅ Exported functions.csv")

