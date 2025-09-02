#!/usr/bin/env python3
"""
Gprof Assembly Extractor

This script parses gprof output and extracts assembly code for functions
at specified call graph depths using objdump.

Usage:
    python gprof_asm_extractor.py <binary_path> <gprof_output> <depth> [root_function]

Arguments:
    binary_path: Path to the binary executable
    gprof_output: Path to the gprof output file
    depth: Number of levels deep to extract (0 = only root, 1 = root + children, etc.)
    root_function: Optional root function name (default: "main")
"""

import re
import subprocess
import sys
import argparse
from typing import Dict, List, Set, Optional
from collections import defaultdict, deque


class CallGraphNode:
    def __init__(self, function_name: str, index: int):
        self.function_name = function_name
        self.index = index
        self.children = []
        self.parents = []
    
    def __repr__(self):
        return f"CallGraphNode({self.function_name}, {self.index})"


class GprofParser:
    def __init__(self, gprof_output_path: str):
        self.gprof_output_path = gprof_output_path
        self.nodes = {}  # index -> CallGraphNode
        self.function_to_node = {}  # function_name -> CallGraphNode
        
    def parse(self):
        """Parse the gprof output and build the call graph."""
        with open(self.gprof_output_path, 'r') as f:
            content = f.read()
        
        # Find the call graph section
        call_graph_start = content.find("Call graph")
        if call_graph_start == -1:
            raise ValueError("Could not find 'Call graph' section in gprof output")
        
        # Extract the call graph section
        call_graph_section = content[call_graph_start:]
        
        # Split into entries separated by lines of dashes
        entries = re.split(r'\n-{20,}\n', call_graph_section)
        
        for entry in entries:
            self._parse_entry(entry)
    
    def _parse_entry(self, entry: str):
        """Parse a single call graph entry."""
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        
        if not lines:
            return
        
        # Find the main function line (contains [index])
        main_line = None
        main_line_idx = -1
        
        for i, line in enumerate(lines):
            if re.search(r'\[\d+\]', line) and not line.startswith('0.00'):
                main_line = line
                main_line_idx = i
                break
        
        if not main_line:
            return
        
        # Extract function info from main line
        main_match = re.search(r'\[(\d+)\]\s+[\d.]+\s+[\d.]+\s+[\d.]+(?:\s+\d+)?\s+(.+?)\s+\[(\d+)\]', main_line)
        if not main_match:
            return
        
        index = int(main_match.group(1))
        function_name = main_match.group(2).strip()
        
        # Create or get the node
        if index not in self.nodes:
            self.nodes[index] = CallGraphNode(function_name, index)
            self.function_to_node[function_name] = self.nodes[index]
        
        node = self.nodes[index]
        
        # Parse children (lines after the main line)
        for line in lines[main_line_idx + 1:]:
            if not line or line.startswith('-------') or 'Call graph' in line:
                continue
            
            # Extract child function info
            child_match = re.search(r'(.+?)\s+\[(\d+)\]', line)
            if child_match:
                child_name = child_match.group(1).strip()
                child_index = int(child_match.group(2))
                
                # Remove call count information from function name
                child_name = re.sub(r'^\s*[\d.]+\s+[\d.]+\s+\d+/\d+\s+', '', child_name)
                
                # Create child node if it doesn't exist
                if child_index not in self.nodes:
                    self.nodes[child_index] = CallGraphNode(child_name, child_index)
                    self.function_to_node[child_name] = self.nodes[child_index]
                
                child_node = self.nodes[child_index]
                
                # Add relationship
                if child_node not in node.children:
                    node.children.append(child_node)
                if node not in child_node.parents:
                    child_node.parents.append(node)


class AssemblyExtractor:
    def __init__(self, binary_path: str):
        self.binary_path = binary_path
    
    def get_function_assembly(self, function_name: str) -> str:
        """Extract assembly code for a specific function using objdump."""
        try:
            # Use objdump to disassemble the specific function
            cmd = ['objdump', '-d', '--demangle', self.binary_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the objdump output to find the specific function
            lines = result.stdout.split('\n')
            function_lines = []
            in_function = False
            
            # Pattern to match function headers
            function_pattern = re.compile(r'<(.+?)>:')
            
            for line in lines:
                # Check if this line starts a new function
                match = function_pattern.search(line)
                if match:
                    found_function = match.group(1)
                    # Check if this is our target function (handle C++ name mangling)
                    if self._function_matches(function_name, found_function):
                        in_function = True
                        function_lines = [line]
                    else:
                        in_function = False
                elif in_function:
                    # Stop if we hit another function or empty line after assembly
                    if (function_pattern.search(line) or 
                        (line.strip() == '' and len(function_lines) > 1)):
                        break
                    function_lines.append(line)
            
            return '\n'.join(function_lines) if function_lines else f"Function '{function_name}' not found"
            
        except subprocess.CalledProcessError as e:
            return f"Error running objdump: {e}"
        except FileNotFoundError:
            return "objdump not found. Please install binutils."
    
    def _function_matches(self, target: str, candidate: str) -> bool:
        """Check if two function names match, handling C++ mangling."""
        # Direct match
        if target == candidate:
            return True
        
        # Check if target is contained in candidate (for mangled names)
        if target in candidate:
            return True
        
        # Handle C++ function signatures - extract just the function name
        target_clean = re.sub(r'\(.*\)', '', target).split('::')[-1]
        candidate_clean = re.sub(r'\(.*\)', '', candidate).split('::')[-1]
        
        return target_clean == candidate_clean


def get_functions_at_depth(parser: GprofParser, root_function: str, max_depth: int) -> Set[str]:
    """Get all functions reachable within max_depth levels from root_function."""
    if root_function not in parser.function_to_node:
        available_functions = list(parser.function_to_node.keys())
        raise ValueError(f"Root function '{root_function}' not found. Available functions: {available_functions[:10]}...")
    
    root_node = parser.function_to_node[root_function]
    visited = set()
    result = set()
    
    # BFS to find all functions within max_depth
    queue = deque([(root_node, 0)])
    
    while queue:
        node, depth = queue.popleft()
        
        if node.index in visited:
            continue
        
        visited.add(node.index)
        result.add(node.function_name)
        
        # Add children if we haven't reached max depth
        if depth < max_depth:
            for child in node.children:
                if child.index not in visited:
                    queue.append((child, depth + 1))
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Extract assembly code from gprof call graph')
    parser.add_argument('binary_path', help='Path to the binary executable')
    parser.add_argument('gprof_output', help='Path to the gprof output file')
    parser.add_argument('depth', type=int, help='Number of levels deep to extract')
    parser.add_argument('--root', default='main', help='Root function name (default: main)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    try:
        # Parse gprof output
        print(f"Parsing gprof output from {args.gprof_output}...", file=sys.stderr)
        gprof_parser = GprofParser(args.gprof_output)
        gprof_parser.parse()
        
        print(f"Found {len(gprof_parser.nodes)} functions in call graph", file=sys.stderr)
        
        # Get functions at specified depth
        print(f"Finding functions reachable within {args.depth} levels from '{args.root}'...", file=sys.stderr)
        target_functions = get_functions_at_depth(gprof_parser, args.root, args.depth)
        
        print(f"Found {len(target_functions)} functions to disassemble", file=sys.stderr)
        
        # Extract assembly for each function
        extractor = AssemblyExtractor(args.binary_path)
        
        output_lines = []
        output_lines.append(f"Assembly code for functions reachable within {args.depth} levels from '{args.root}':")
        output_lines.append("=" * 80)
        
        for i, function_name in enumerate(sorted(target_functions)):
            print(f"Extracting assembly for function {i+1}/{len(target_functions)}: {function_name}", file=sys.stderr)
            
            output_lines.append(f"\nFunction: {function_name}")
            output_lines.append("-" * 40)
            
            assembly = extractor.get_function_assembly(function_name)
            output_lines.append(assembly)
            output_lines.append("")
        
        # Write output
        output_text = '\n'.join(output_lines)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_text)
            print(f"Assembly code written to {args.output}", file=sys.stderr)
        else:
            print(output_text)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
