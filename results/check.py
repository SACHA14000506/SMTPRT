import os
import time
import subprocess

base_path = ""
versions = []
op = 'smt.string_solver=' + 'z3str3'
output_file = "0checkout.csv"

smt_files = [f for f in os.listdir('.') if f.endswith('.smt2')]

results = {}

for file_name in smt_files:
    results[file_name] = []
    for version in versions:
        solver_path = os.path.join(base_path, version, "bin", "z3")
        cmd = [
            "timeout", "20",
            "bash", "-c",
            f"'{solver_path}' \"{file_name}\""
        ]

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
        except subprocess.TimeoutExpired:
            end_time = time.time()
            runtime = end_time - start_time
            exit_code = 124
            results[file_name].append([runtime, exit_code])
            continue

        end_time = time.time()
        runtime = end_time - start_time
        exit_code = result.returncode

        results[file_name].append([runtime, exit_code])

with open(output_file, "w") as f:
    f.write("File Name | " + " | ".join([f"{version} (s/e)" for version in versions]) + "\n")
