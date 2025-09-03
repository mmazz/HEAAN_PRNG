#!/usr/bin/env python3
"""
Simple test version of the instruction analyzer
"""

import re
from collections import Counter

def parse_instruction_file(filename):
    """Parse the instruction count file"""
    functions = {}
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by function separators (lines of dashes) or function headers
    function_blocks = re.split(r'-{20,}', content)
    
    for block in function_blocks:
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        
        if not lines:
            continue
            
        # Skip the overall summary section if it exists
        if any('Overall Summary' in line or 'Total functions analyzed' in line for line in lines):
            continue
        
        current_function = None
        
        for i, line in enumerate(lines):
            # Look for function header
            func_match = re.match(r"Function: '(.+)'", line)
            if func_match:
                current_function = func_match.group(1)
                functions[current_function] = {'total': 0, 'instructions': {}}
                continue
            
            # Look for total instructions
            total_match = re.match(r"Total instructions: (\d+)", line)
            if total_match and current_function:
                functions[current_function]['total'] = int(total_match.group(1))
                continue
            
            # Parse instruction breakdown
            if line == "Instruction breakdown:" and current_function:
                # Parse instructions from following lines
                for j in range(i + 1, len(lines)):
                    inst_line = lines[j]
                    inst_match = re.match(r"\s*-\s*(\w+):\s*(\d+)", inst_line)
                    if inst_match:
                        instruction = inst_match.group(1)
                        count = int(inst_match.group(2))
                        functions[current_function]['instructions'][instruction] = count
                break
    
    return functions

def generate_summary(functions_data):
    """Generate overall summary statistics"""
    # Filter out functions with 0 instructions
    valid_functions = {name: data for name, data in functions_data.items() if data['total'] > 0}
    
    total_functions = len(valid_functions)
    total_instructions = sum(func_data['total'] for func_data in valid_functions.values())
    
    # Aggregate all instruction counts
    overall_instructions = Counter()
    for func_data in valid_functions.values():
        for instruction, count in func_data['instructions'].items():
            overall_instructions[instruction] += count
    
    return {
        'total_functions': total_functions,
        'total_instructions': total_instructions,
        'instruction_counts': overall_instructions
    }

def print_summary(summary):
    """Print the formatted summary"""
    print("=" * 40)
    print("Overall Summary")
    print("=" * 40)
    print(f"Total functions analyzed: {summary['total_functions']}")
    print(f"Total instructions across all functions: {summary['total_instructions']}")
    print("Most common instructions overall:")
    
    # Sort instructions by count (descending)
    for instruction, count in summary['instruction_counts'].most_common():
        print(f"  - {instruction}: {count}")

# Test with the provided file
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python3 test_analyzer.py <instruction_count_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        print(f"Parsing file: {filename}")
        functions_data = parse_instruction_file(filename)
        
        print(f"Found {len(functions_data)} functions")
        
        # Debug: show first few functions
        print("\nFirst few functions found:")
        for i, (name, data) in enumerate(list(functions_data.items())[:3]):
            print(f"  {i+1}. {name} - {data['total']} instructions")
        
        print()
        
        summary = generate_summary(functions_data)
        print_summary(summary)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
