import re
import csv
import sys

def parse_gprof_callgraph_correct(file_path, output_csv):
    """
    Correctly parse gprof callgraph output following the proper structure:
    - Callers are listed BEFORE the function header line
    - Callees (children) are listed AFTER the function header line
    - Each entry is separated by dashed lines
    """
    
    edges = []
    current_function = None
    callers = []
    callees = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for separator line (start of new entry)
        if line.startswith('---'):
            # Process the previous entry if we have one
            if current_function is not None:
                # Add edges from callers to current function
                for caller_info in callers:
                    edges.append({
                        'source': caller_info['caller_index'],
                        'target': current_function,
                        'call_count': caller_info['call_count'],
                        'total_calls': caller_info['total_calls'],
                        'type': 'caller'
                    })
                
                # Add edges from current function to callees
                for callee_info in callees:
                    edges.append({
                        'source': current_function,
                        'target': callee_info['callee_index'],
                        'call_count': callee_info['call_count'],
                        'total_calls': callee_info['total_calls'],
                        'type': 'callee'
                    })
            
            # Reset for new entry
            current_function = None
            callers = []
            callees = []
            i += 1
            continue
        
        # Check if this is a function header line (e.g., [7] ... [7])
        header_match = re.match(r'^\[(\d+)\].*\[(\d+)\]$', line)
        if header_match:
            current_function = header_match.group(1)
            
            # Now look backwards for callers and forwards for callees
            # Look backwards for callers (lines before the header)
            j = i - 1
            while j >= 0 and not lines[j].strip().startswith('---') and lines[j].strip():
                caller_line = lines[j].strip()
                caller_info = parse_call_line(caller_line)
                if caller_info:
                    callers.append(caller_info)
                j -= 1
            
            # Look forwards for callees (lines after the header)
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('---') and lines[j].strip():
                callee_line = lines[j].strip()
                callee_info = parse_call_line(callee_line)
                if callee_info:
                    callees.append(callee_info)
                j += 1
            
            i = j
            continue
        
        i += 1
    
    # Process the last entry
    if current_function is not None:
        for caller_info in callers:
            edges.append({
                'source': caller_info['caller_index'],
                'target': current_function,
                'call_count': caller_info['call_count'],
                'total_calls': caller_info['total_calls'],
                'type': 'caller'
            })
        
        for callee_info in callees:
            edges.append({
                'source': current_function,
                'target': callee_info['callee_index'],
                'call_count': callee_info['call_count'],
                'total_calls': callee_info['total_calls'],
                'type': 'callee'
            })
    
    # Write edges to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['source', 'target', 'call_count', 'total_calls', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for edge in edges:
            writer.writerow(edge)
    
    return edges

def parse_call_line(line):
    """
    Parse a single caller or callee line to extract:
    - Function index (in brackets)
    - Call count (format: calls/total)
    """
    # Pattern to match: 0.00    0.00  639108/639367      FunctionName [6]
    pattern = r'^\s*[\d.]+\s+[\d.]+\s+(\d+)/(\d+)\s+.*?\[(\d+)\]$'
    match = re.match(pattern, line)
    
    if match:
        call_count = int(match.group(1))
        total_calls = int(match.group(2))
        func_index = match.group(3)
        
        return {
            'caller_index' if 'caller' in line else 'callee_index': func_index,
            'call_count': call_count,
            'total_calls': total_calls
        }
    
    return None

# Alternative simpler version focusing only on the relationships you need
def parse_gprof_simple_relationships(file_path, output_csv):
    """
    Simplified parser that only extracts the call relationships between functions
    (ignoring the caller information if not needed)
    """
    
    edges = []
    current_function = None
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for separator line
        if line.startswith('---'):
            i += 1
            continue
        
        # Check for function header line
        header_match = re.match(r'^\[(\d+)\].*\[(\d+)\]$', line)
        if header_match:
            current_function = header_match.group(1)
            
            # Look for callees after the header
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('---') and lines[j].strip():
                callee_line = lines[j].strip()
                callee_info = parse_call_line(callee_line)
                if callee_info:
                    edges.append({
                        'source': current_function,
                        'target': callee_info['callee_index'],
                        'call_count': callee_info['call_count'],
                        'total_calls': callee_info['total_calls']
                    })
                j += 1
            
            i = j
        else:
            i += 1
    
    # Write to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['source', 'target', 'call_count', 'total_calls'])
        for edge in edges:
            writer.writerow([edge['source'], edge['target'], edge['call_count'], edge['total_calls']])
    
    return edges

# Example usage
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python callgrind_parser.py <path_to_callgrind_output>")
        print("Example: python callgrind_parser.py callgrind.out.12345")
        sys.exit(1)
    
    gprof_file = sys.argv[1]

    # Parse with the correct structure
    edges = parse_gprof_simple_relationships(gprof_file, 'callgraph_edges_correct.csv')
    
    # Print the edges found
    print("Correct callgraph edges:")
    for edge in edges:
        print(f"{edge['source']} -> {edge['target']}: {edge['call_count']}/{edge['total_calls']} calls")
