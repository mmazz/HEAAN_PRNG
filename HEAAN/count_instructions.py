#!/usr/bin/env python3
import re
import sys
import pandas as pd

instr_regex = re.compile(r"^\s+[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s+([a-z][a-z0-9]+)")

def parse_disassembly(disasm_file):
    rows = []
    current_func = None

    with open(disasm_file) as f:
        for line in f:
            line = line.rstrip()

            if line.startswith("; ===== "):
                current_func = line[len("; ===== "):-len(" =====")]
            else:
                m = instr_regex.match(line)
                if m and current_func:
                    rows.append((current_func, m.group(1)))

    df = pd.DataFrame(rows, columns=["func_name", "instr"])
    df = df.value_counts().reset_index(name="count")  # counts per (func, instr)
    return df

def main(disasm_file, functions_csv, out_csv):
    # Parse disassembly → (func_name, instr, count)
    disasm_df = parse_disassembly(disasm_file)

    # Load call counts
    funcs_df = pd.read_csv(functions_csv, usecols=["func_name", "total_calls"])

    # Merge
    merged = disasm_df.merge(funcs_df, on="func_name", how="left")
    merged["executed_count"] = merged["count"] * merged["total_calls"]

    # Save
    merged.to_csv(out_csv, index=False)

    # Also print summary
    for func, group in merged.groupby("func_name"):
        total_per_call = group["count"].sum()
        calls = group["total_calls"].iloc[0]
        total_exec = group["executed_count"].sum()

        print(f"Function: '{func}'")
        print(f"Instructions per call: {total_per_call}")
        print(f"Total calls: {calls}")
        print(f"Total executed instructions: {total_exec}")
        print("Instruction breakdown:")
        for _, row in group.sort_values("count", ascending=False).iterrows():
            print(f"  - {row.instr}: {row['count']} × {row.total_calls} = {row.executed_count}")
        print()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <disassembly.s> <functions.csv> <output.csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])

