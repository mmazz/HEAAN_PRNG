#!/usr/bin/env python3
"""
Modified Analyzer to parse assembly output from gprof extractor.
Parses assembly output and counts instruction usage per function.
"""

import re
from collections import Counter
import sys

def parse_assembly(file_path):
    """
    Parse assembly file and extract functions with their instructions.
    
    Args:
        file_path (str): Path to the assembly file
        
    Returns:
        dict: Dictionary mapping function names to instruction counters
    """
    functions = {}
    current_function = None
    
    # Regex patterns for the gprof extractor output format
    function_pattern = r'^Function: (.*)$'
    instruction_pattern = r'^\s*([0-9a-fA-F]+):\s+[0-9a-fA-F\s]+\s+([a-zA-Z][a-zA-Z0-9]*)'
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip()
                
                # Check for "Not found" lines and skip them
                if "not found" in line.lower():
                    current_function = None
                    continue

                # Check if this is a function header
                func_match = re.match(function_pattern, line)
                if func_match:
                    function_name = func_match.group(1).strip()
                    current_function = function_name
                    functions[current_function] = Counter()
                    continue
                
                # Check if this is an instruction line
                if current_function:
                    instr_match = re.match(instruction_pattern, line)
                    if instr_match:
                        instruction = instr_match.group(2).lower()
                        functions[current_function][instruction] += 1
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}
    
    return functions

def display_results(functions):
    """
    Displays the instruction count for each function.
    
    Args:
        functions (dict): Dictionary from parse_assembly
    """
    for func_name, instructions in functions.items():
        total_instructions = sum(instructions.values())
        print(f"Function: '{func_name}'")
        print(f"Total instructions: {total_instructions}")
        if total_instructions > 0:
            print("Instruction breakdown:")
            for instr, count in instructions.most_common():
                print(f"  - {instr}: {count}")
        print("-" * 40)

def display_summary(functions):
    """
    Displays a total summary of all instructions.
    
    Args:
        functions (dict): Dictionary from parse_assembly
    """
    total_instructions_all_funcs = 0
    all_instructions = Counter()
    for instructions in functions.values():
        total_instructions_all_funcs += sum(instructions.values())
        all_instructions.update(instructions)
    
    print("=" * 40)
    print("Overall Summary")
    print("=" * 40)
    print(f"Total functions analyzed: {len(functions)}")
    print(f"Total instructions across all functions: {total_instructions_all_funcs}")
    print("\nMost common instructions overall:")
    for instr, count in all_instructions.most_common(10):
        print(f"  - {instr}: {count}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python instruction-count.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    functions = parse_assembly(file_path)
    
    if functions:
        display_results(functions)
        display_summary(functions)
    else:
        print("No functions were parsed from the file.")

if __name__ == "__main__":
    main()
