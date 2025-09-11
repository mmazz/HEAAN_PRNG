import duckdb
import os
import subprocess
import sys
from datetime import datetime

### Config
BIN_DIR = "../bin/"
COMPILER = "g++"
COMPILER_FLAGS = "-O2 -Wall -g"
LINKER_FLAGS = "-lgmp -lntl -lm"
RUN_FLAGS = ""  
BINARY_NAME = "pepito"  

connection = duckdb.connect("heaan-data.duckdb")

def init_db():
    connection.execute("""
        CREATE TABLE IF NOT EXISTS binaries (
            binary_id INTEGER PRIMARY KEY,
            binary_name TEXT NOT NULL,
            compiler TEXT,
            compiler_flags TEXT,
            running_flags TEXT,
            run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            binary_id INTEGER NOT NULL,
            func_id INTEGER NOT NULL,
            func_name TEXT NOT NULL,
            total_calls INTEGER,
            PRIMARY KEY (binary_id, func_id),
            FOREIGN KEY (binary_id) REFERENCES binaries(binary_id)
        );
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            binary_id INTEGER NOT NULL,
            caller_id INTEGER NOT NULL,
            callee_id INTEGER NOT NULL,
            call_count INTEGER,
            PRIMARY KEY (binary_id, caller_id, callee_id),
            FOREIGN KEY (binary_id) REFERENCES binaries(binary_id),
            FOREIGN KEY (binary_id, callee_id) REFERENCES functions(binary_id, func_id)
        );
    """)

def run_and_parse(binary_path, binary_id_param):

    binary_name = os.path.basename(binary_path)

    # 1. Run binary to generate gmon.out
    subprocess.run([binary_path] + RUN_FLAGS.split(), check=True)

    # 2. Run gprof
    gprof_output = f"{binary_name}_gprof.txt"
    with open(gprof_output, "w") as f:
        subprocess.run(["gprof", "-b", "-q", binary_path, "gmon.out"], stdout=f, check=True)

    # 3. Parse calls and functions
    calls_csv = f"{binary_name}_calls.csv"
    functions_csv = f"{binary_name}_functions.csv"

    subprocess.run(["python3", "parse_calls.py", gprof_output], check=True)
    os.rename("callgraph_edges_correct.csv", calls_csv)  # parse_calls writes this file

    subprocess.run(["python3", "parse_functions.py", gprof_output], check=True)
    os.rename("functions.csv", functions_csv)  # parse_functions writes this file

    # Insert binary metadata
    result = connection.execute("""
        INSERT INTO binaries (binary_id, binary_name, compiler, compiler_flags, running_flags)
        VALUES (?, ?, ?, ?, ?)
        RETURNING binary_id;
    """, [binary_id_param, BINARY_NAME, COMPILER, COMPILER_FLAGS, RUN_FLAGS]).fetchone()
    binary_id = result[0]

    
    # 5. Load functions
    connection.execute(f"""
        INSERT INTO functions
        SELECT {binary_id}, func_id, func_name, total_calls, instructions_executed
        FROM read_csv('{functions_csv}', AUTO_DETECT=TRUE);
    """)

    # 6. Load calls
    connection.execute(f"""
        INSERT INTO calls
        SELECT {binary_id}, source AS caller_id, target AS callee_id, call_count, total_calls
        FROM read_csv('{calls_csv}', AUTO_DETECT=TRUE);
    """)
##
##
##
##    # Load functions.csv
##    connection.execute(f"""
##        INSERT INTO functions
##        SELECT {binary_id}, func_id, func_name, total_calls
##        FROM read_csv('{functions}', AUTO_DETECT=TRUE);
##    """)
##
##    # Load calls.csv
##    connection.execute(f"""
##        INSERT INTO calls
##        SELECT {binary_id}, caller_id, callee_id, call_count
##        FROM read_csv('{calls}', AUTO_DETECT=TRUE);
##    """)
##
    print(f"✅ Inserted values into database")

def main():
    init_db()
    
    binary_id = 1
    for fname in os.listdir(BIN_DIR):
        fpath = os.path.join(BIN_DIR, fname)
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            try:
                run_and_parse(fpath, binary_id)
                binary_id += 1
            except subprocess.CalledProcessError as e:
                print(f"❌ Error processing {fname}: {e}")

if __name__ == "__main__":
    main()

