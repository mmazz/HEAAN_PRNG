#!/usr/bin/env python3
import csv, subprocess, sys, re

def extract_disassembly(binary, func_name):
    pattern = re.escape(func_name)
    try:
        output = subprocess.check_output(
            ["objdump", "-d", "--demangle", binary],
            text=True, errors="ignore"
        )
    except subprocess.CalledProcessError as e:
        return f";; error running objdump: {e}\n"

    regex = re.compile(rf"([0-9a-f]+) <{pattern}>:\n((?:\s+[0-9a-f]+:.*\n)*)", re.MULTILINE)
    match = regex.search(output)
    return match.group(0) if match else f";; not found {func_name}\n"

def main(csv_file, binary):
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            func_name = row["func_name"]
            print(f"\n; ===== {func_name} =====")
            print(extract_disassembly(binary, func_name))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <functions.csv> <binary>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

