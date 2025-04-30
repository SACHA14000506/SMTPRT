import os
import subprocess
import re
import xml.etree.ElementTree as ET
import time
from typing import List, Tuple

EXCLUDE_PATTERNS = [
    "tests/.*",
    "third_party/.*",
    ".*/mock_.*",
]
PARALLEL_JOBS = 4

def delete_gcda_files(folder_path: str) -> None:
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file in files:
            if file.endswith(".gcda"):
                os.remove(os.path.join(root, file))


def run_command(command: str, cwd: str = None) -> Tuple[str, str]:
    print(f"Running command: {command} in directory: {cwd}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        encoding='utf-8',
        cwd=cwd
    )
    stdout, stderr = process.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    return stdout, stderr


def read_keywords(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def delete_lines(target_file: str, keywords: List[str]) -> None:
    pattern = re.compile('|'.join(map(re.escape, keywords)), re.IGNORECASE)
    with open(target_file, 'r+', encoding='utf-8') as f:
        filtered = [line for line in f if not pattern.search(line)]
        f.seek(0)
        f.writelines(filtered)
        f.truncate()


def count_matching_lines(file1_path: str, file2_path: str) -> float:
    with open(file1_path, 'r', encoding='utf-8') as f1, \
            open(file2_path, 'r', encoding='utf-8') as f2:
        set1 = set(line.strip() for line in f1)
        set2 = set(line.strip() for line in f2)

    common = set1 & set2
    total = len(set2)
    return len(common) / total if total > 0 else 0.0


def parse_coverage_xml(xml_path: str, output_file: str) -> None:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    pairs = []
    for class_elem in root.findall('.//class'):
        filename = class_elem.get('filename')
        for line_elem in class_elem.findall('.//lines/line'):
            line_number = line_elem.get('number')
            pairs.append(f"{filename} {line_number}\n")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(pairs)


def coverage_fun(solver: str, file_name: str) -> float:
    folder_path = f"/home/cass/Webstorm_project/SMTPRT/{solver}/build"
    xml_path = os.path.join(folder_path, f'coverage_{solver}.xml')
    pairs_file = f"coverage_{solver}_pairs.txt"
    target_file = f"{solver}_diff_filtered.txt"

    delete_gcda_files(folder_path)

    run_command(f"timeout 21 {folder_path}/z3 {file_name}")

    gcovr_path = "/home/cass/miniconda3/bin/gcovr"
    gcovr_cmd = (
        f"{gcovr_path} -r .. "
        f"--jobs {PARALLEL_JOBS} "
        f"--exclude '{' --exclude '.join(EXCLUDE_PATTERNS)}' "
        "--xml "
        f"-o coverage_{solver}.xml"
    )
    start_time = time.time()
    run_command(f"{gcovr_path} -r .. --xml-pretty -o coverage_{solver}.xml", cwd=folder_path)
    elapsed = time.time() - start_time

    print(f"time: {elapsed:.2f}秒")
    parse_coverage_xml(xml_path, pairs_file)

    delete_lines(pairs_file, read_keywords("keywords.txt"))

    return 0.0 if solver == "z3-version" else count_matching_lines(pairs_file, target_file)
