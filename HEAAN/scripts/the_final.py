#!/usr/bin/env python3
import re
import csv
import sys

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <gprof_output.txt>")
    sys.exit(1)

filename = sys.argv[1]

# Regular expressions for parsing - more flexible to handle gprof format
func_re = re.compile(
    r"^\[(\d+)\].*?\[(\d+)\]$"
)
call_re = re.compile(
    r"^\s*[\d.]+\s+[\d.]+\s+(\d+)/(\d+)\s+.*?\[(\d+)\]$"
)

functions = {}
calls = []

with open(filename) as f:
    lines = f.readlines()

i = 0
while i < len(lines):
    line = lines[i].strip()
    
    # Skip empty lines
    if not line:
        i += 1
        continue
    
    # Check for separator line
    if line.startswith('---'):
        i += 1
        continue
    
    # Check for function header line (e.g., [7] ... [7])
    if line.startswith('[') and line.endswith(']'):
        # Extract function ID from the last [number] in the line
        func_match = re.findall(r'\[(\d+)\]', line)
        if func_match:
            fid = int(func_match[-1])  # Get the last [number] which is the function ID
            
            # Extract function name and total calls if available
            parts = line.split()
            total_calls = 0
            func_name = "unknown"
            
            # Try to find total calls (the number before the function name)
            for j, part in enumerate(parts):
                if part.isdigit() and j > 0 and parts[j-1].replace('.', '').isdigit():
                    total_calls = int(part)
                    func_name = ' '.join(parts[j+1:-1])
                    break
            else:
                # If no explicit total calls, use the function name from the middle
                func_name = ' '.join(parts[1:-1])
            
            functions[fid] = {
                "id": fid,
                "name": func_name,
                "total_calls": total_calls,
                "instructions": None
            }
            current_func = fid
            
            # Look backwards for callers (functions that call this function)
            j = i - 1
            while j >= 0 and not lines[j].strip().startswith('---') and lines[j].strip():
                caller_line = lines[j].strip()
                caller_match = call_re.match(caller_line)
                if caller_match:
                    call_count = int(caller_match.group(1))
                    total_caller_calls = int(caller_match.group(2))
                    caller_id = int(caller_match.group(3))
                    
                    calls.append({
                        "caller_id": caller_id,
                        "callee_id": current_func,
                        "call_count": call_count,
                        "total_calls": total_caller_calls
                    })
                j -= 1
            
            # Look forwards for callees (functions that this function calls)
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('---') and lines[j].strip():
                callee_line = lines[j].strip()
                callee_match = call_re.match(callee_line)
                if callee_match:
                    call_count = int(callee_match.group(1))
                    total_callee_calls = int(callee_match.group(2))
                    callee_id = int(callee_match.group(3))
                    
                    calls.append({
                        "caller_id": current_func,
                        "callee_id": callee_id,
                        "call_count": call_count,
                        "total_calls": total_callee_calls
                    })
                j += 1
            
            i = j
        else:
            i += 1
    else:
        i += 1

# Debug output to see what was parsed
print(f"Found {len(functions)} functions")
print(f"Found {len(calls)} call relationships")

# Write functions.csv
with open("functions.csv", "w", newline="") as fcsv:
    writer = csv.DictWriter(fcsv, fieldnames=["func_id", "func_name", "total_calls", "instructions_executed"])
    writer.writeheader()
    for func_id, func_data in sorted(functions.items()):
        writer.writerow({
            "func_id": func_data["id"],
            "func_name": func_data["name"],
            "total_calls": func_data["total_calls"],
            "instructions_executed": func_data["instructions"] or ""
        })

# Write calls.csv with additional total_calls field
with open("calls.csv", "w", newline="") as fcsv:
    writer = csv.DictWriter(fcsv, fieldnames=["caller_id", "callee_id", "call_count", "total_calls"])
    writer.writeheader()
    for call in calls:
        writer.writerow(call)

print(f"✅ Exported functions.csv with {len(functions)} functions")
print(f"✅ Exported calls.csv with {len(calls)} call relationships")
