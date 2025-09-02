#!/bin/bash
# gprof_analysis_pipeline.sh
# Complete pipeline for gprof analysis with assembly extraction and instruction counting

set -e # Exit on any error

# Default values
UTILS_DIR="../utils"
DEPTH=2
BINARY_NAME=""
CLEAN_BUILD=false
VERBOSE=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
  echo -e "${BLUE}[STEP $1]${NC} $2"
}

print_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
  cat <<EOF
Usage: $0 [OPTIONS] <binary_name> <call_graph_depth>

Complete pipeline for gprof analysis with assembly extraction and instruction counting.

Arguments:
    binary_name         Name of the binary to analyze
    call_graph_depth    Depth of call graph to extract (0=root only, 1=root+children, etc.)

Options:
    -u, --utils-dir DIR     Utils directory path (default: ../utils)
    -c, --clean             Clean build (make clean first)
    -v, --verbose           Verbose output
    -h, --help              Show this help message

Example:
    $0 HEAAN-o0 2                    # Analyze HEAAN-o0 with depth 2
    $0 -c -v my_program 1            # Clean build, verbose, depth 1
    $0 --utils-dir ./scripts HEAAN-o0 3    # Custom utils directory

Pipeline steps:
    1. Compile binary with make
    2. Run binary to generate gmon.out
    3. Generate gprof output (filtered)
    4. Extract assembly code
    5. Count instructions per function
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  -u | --utils-dir)
    UTILS_DIR="$2"
    shift 2
    ;;
  -c | --clean)
    CLEAN_BUILD=true
    shift
    ;;
  -v | --verbose)
    VERBOSE=true
    shift
    ;;
  -h | --help)
    usage
    exit 0
    ;;
  -*)
    print_error "Unknown option: $1"
    usage
    exit 1
    ;;
  *)
    if [ -z "$BINARY_NAME" ]; then
      BINARY_NAME="$1"
    elif [ -z "$DEPTH" ]; then
      DEPTH="$1"
    else
      print_error "Too many arguments"
      usage
      exit 1
    fi
    shift
    ;;
  esac
done

# Validate arguments
if [ -z "$BINARY_NAME" ]; then
  print_error "Binary name is required"
  usage
  exit 1
fi

if [ -z "$DEPTH" ] || ! [[ "$DEPTH" =~ ^[0-9]+$ ]]; then
  print_error "Call graph depth must be a non-negative integer"
  usage
  exit 1
fi

# Validate utils directory
if [ ! -d "$UTILS_DIR" ]; then
  print_error "Utils directory '$UTILS_DIR' not found"
  exit 1
fi

# Check for required scripts
GPROF_EXTRACTOR="$UTILS_DIR/gprof_asm_extractor.py"
INSTRUCTION_COUNTER="$UTILS_DIR/instruction-count.py"

if [ ! -f "$GPROF_EXTRACTOR" ]; then
  print_error "gprof_asm_extractor.py not found in $UTILS_DIR"
  exit 1
fi

if [ ! -f "$INSTRUCTION_COUNTER" ]; then
  print_error "instruction-count.py not found in $UTILS_DIR"
  exit 1
fi

# Check for required tools
for tool in make gprof objdump python3; do
  if ! command -v $tool &>/dev/null; then
    print_error "$tool is required but not installed"
    exit 1
  fi
done

# Define output files
GPROF_OUTPUT="${BINARY_NAME}_gprof"
ASM_OUTPUT="${BINARY_NAME}_asm"
INSTRUCTION_OUTPUT="${BINARY_NAME}_instruction_counts.txt"

echo "Gprof Analysis Pipeline"
echo "======================"
echo "Binary: $BINARY_NAME"
echo "Call graph depth: $DEPTH"
echo "Utils directory: $UTILS_DIR"
echo ""

# Step 1: Compile binary
print_step "1" "Compiling binary with make"

if [ "$CLEAN_BUILD" = true ]; then
  if [ "$VERBOSE" = true ]; then
    make clean
  else
    make clean >/dev/null 2>&1
  fi
  print_success "Clean completed"
fi

if [ "$VERBOSE" = true ]; then
  make "$BINARY_NAME"
else
  make "$BINARY_NAME" >/dev/null 2>&1
fi

if [ ! -f "$BINARY_NAME" ]; then
  print_error "Binary '$BINARY_NAME' was not created by make"
  exit 1
fi

print_success "Binary compiled successfully"

# Step 2: Run binary to generate gmon.out
print_step "2" "Running binary to generate profiling data"

# Remove old gmon.out if it exists
[ -f gmon.out ] && rm gmon.out callgrind*

if [ "$VERBOSE" = true ]; then
  valgrind --tool=callgrind --dump-instr=yes ./"$BINARY_NAME"
else
  valgrind --tool=callgrind --dump-instr=yes ./"$BINARY_NAME" >/dev/null 2>&1
fi

if [ ! -f gmon.out ]; then
  print_error "gmon.out was not generated. Make sure the binary was compiled with -pg flag"
  exit 1
fi

print_success "Profiling data generated (gmon.out)"

# Step 3: Generate filtered gprof output
print_step "3" "Generating filtered gprof output"

gprof -b -q "$BINARY_NAME" gmon.out | grep -v "std::__" | grep -v "~" >"$GPROF_OUTPUT"

if [ ! -s "$GPROF_OUTPUT" ]; then
  print_error "No gprof data generated or all functions were filtered out"
  exit 1
fi

GPROF_LINES=$(wc -l <"$GPROF_OUTPUT")
print_success "Gprof output generated ($GPROF_LINES lines) -> $GPROF_OUTPUT"

# Step 4: Extract assembly code
print_step "4" "Extracting assembly code (depth: $DEPTH)"

if [ "$VERBOSE" = true ]; then
  python3 "$GPROF_EXTRACTOR" "$BINARY_NAME" "$GPROF_OUTPUT" "$DEPTH" >"$ASM_OUTPUT"
else
  python3 "$GPROF_EXTRACTOR" "$BINARY_NAME" "$GPROF_OUTPUT" "$DEPTH" >"$ASM_OUTPUT" 2>/dev/null
fi

if [ ! -s "$ASM_OUTPUT" ]; then
  print_error "No assembly output generated"
  exit 1
fi

ASM_LINES=$(wc -l <"$ASM_OUTPUT")
print_success "Assembly code extracted ($ASM_LINES lines) -> $ASM_OUTPUT"

# Step 5: Count instructions per function
print_step "5" "Counting instructions per function"

python3 "$INSTRUCTION_COUNTER" "$ASM_OUTPUT" >"$INSTRUCTION_OUTPUT"

if [ ! -s "$INSTRUCTION_OUTPUT" ]; then
  print_error "No instruction count output generated"
  exit 1
fi

print_success "Instruction analysis completed -> $INSTRUCTION_OUTPUT"

# Final summary
echo ""
echo "Pipeline completed successfully!"
echo "================================"
echo "Generated files:"
echo "  - Gprof output:       $GPROF_OUTPUT"
echo "  - Assembly output:    $ASM_OUTPUT"
echo "  - Instruction counts: $INSTRUCTION_OUTPUT"
echo ""

# Display a preview of the instruction counts
echo "Preview of instruction analysis:"
echo "--------------------------------"
head -20 "$INSTRUCTION_OUTPUT"

if [ $(wc -l <"$INSTRUCTION_OUTPUT") -gt 20 ]; then
  echo ""
  echo "... (see $INSTRUCTION_OUTPUT for full results)"
fi

# Optional: Show file sizes
echo ""
echo "File sizes:"
echo "  - Binary:            $(ls -lh "$BINARY_NAME" | awk '{print $5}')"
echo "  - Gprof output:      $(ls -lh "$GPROF_OUTPUT" | awk '{print $5}')"
echo "  - Assembly output:   $(ls -lh "$ASM_OUTPUT" | awk '{print $5}')"
echo "  - Instruction count: $(ls -lh "$INSTRUCTION_OUTPUT" | awk '{print $5}')"

# Cleanup option
echo ""
read -p "Remove intermediate files (gmon.out, ${GPROF_OUTPUT}, ${ASM_OUTPUT})? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  rm -f gmon.out "$GPROF_OUTPUT" "$ASM_OUTPUT"
  print_success "Intermediate files cleaned up"
  echo "Kept: $BINARY_NAME and $INSTRUCTION_OUTPUT"
fi
