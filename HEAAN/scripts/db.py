import duckdb
import numpy
import sys
import subprocess

### Variables 
BINARY_PATH = "./bin/"
COMPILER_FLAGS = ["-O2", "-Wall", "-g"]
LINKER_FLAGS = ["-lgmp", "-lntl", "-lm"]
connection = duckdb.connect("heaan-data.duckdb")

### functions


### La tabla de binarios va a tener informacion sobre los binarios que van a servir
### para el analisis de instrucciones.
### Nota: La biblioteca HEAAN deberia compilarse con los mismos flags (I believe)
connection.execute("""
    CREATE TABLE binaries (
        binary_id INTEGER PRIMARY KEY,
        binary_name TEXT NOT NULL,      -- e.g., 'my_app_optimized'
        compiler TEXT,                  -- e.g., 'g++'
        compiler_flags TEXT,            -- e.g., '-O3 -march=native'
        running_flags TEXT,             -- e.g., '-n=18'
        run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    );
""")

### La tabla _functions_ posee un identificador para cada funcion dentro de un 
### binario. Luego, por cada funcion, se tiene la cantidad de veces que dicha funcion
### fue llamada
connection.execute("""
    CREATE TABLE functions (
        binary_id INTEGER NOT NULL,
        func_id INTEGER NOT NULL,           -- Note: func_id is only unique WITHIN a binary
        func_name TEXT NOT NULL,
        total_calls INTEGER,
        PRIMARY KEY (binary_id, func_id),   -- Composite primary key!
        FOREIGN KEY (binary_id) REFERENCES binaries(binary_id) ON DELETE CASCADE
    );
""")

### La tabla _calls_ posee la informacion sobre que funcion fue llamada por otra en 
### un binario en particular, y la cantidad de veces que la funcion llamadora la 
### invoco.
connection.execute("""
    CREATE TABLE calls (
        binary_id INTEGER NOT NULL,
        caller_id INTEGER NOT NULL,
        callee_id INTEGER NOT NULL,
        call_count INTEGER,
        PRIMARY KEY (binary_id, caller_id, callee_id), -- Composite primary key
        FOREIGN KEY (binary_id) REFERENCES binaries(binary_id) ON DELETE CASCADE,
        -- The caller and callee must exist in the 'functions' table for THIS binary
        FOREIGN KEY (binary_id, caller_id) REFERENCES functions(binary_id, func_id),
        FOREIGN KEY (binary_id, callee_id) REFERENCES functions(binary_id, func_id)
    );
""")

result = connection.execute("""
    SELECT * 
    FROM read_csv('./moving/functions.csv', skip=1, header=True, columns={
        'func_id': 'INTEGER',
        'func_name': 'VARCHAR',
        'total_calls': 'INTEGER',
        'instructions_executed': 'INTEGER'
    })
    ORDER BY total_calls DESC 
    LIMIT 5
""").fetchdf() # .fetchdf() returns a Pandas DataFrame!


for fname in os.listdir(BIN_DIR):
      fpath = os.path.join(BIN_DIR, fname)
      if os.path.isfile(fpath) and os.access(fpath, os.X_OK):  # only executables
          info = run_binary(fpath, run_flags=RUN_FLAGS)
          runs.append(info)
          print(info)



print(result)
