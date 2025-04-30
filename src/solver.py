import subprocess, time, tempfile
import src.settings as settings
import tempfile
import os
import datetime

import coverage

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

custom_temp_dir = r"/home/cass/Webstorm_project/SMTPRT/results/Regression_cases"  # 临时目录
if not os.path.exists(custom_temp_dir):
    os.makedirs(custom_temp_dir)


def run_command(command):
    start = time.time()
    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')
    proc_stdout, proc_stderr = process.communicate()
    wall_time = time.time() - start
    # print(command)
    out_lines = str(proc_stdout)
    err_lines = str(proc_stderr)
    if wall_time > settings.timeout:
        err_lines += str(" timeout expired ")
    return out_lines, err_lines, wall_time

def run_solver(instance, solver):
    tfile = tempfile.NamedTemporaryFile(delete=False, dir=custom_temp_dir, suffix=".smt2")
    case_former = str(instance)
    if "4.8.9" not in solver:
        case_former = case_former.replace('str.from_int', 'str.from.int')
        case_former = case_former.replace('str.in_re', 'str.in.re')
        case_former = case_former.replace('str.to_int', 'str.to.int')
        case_former = case_former.replace('str.to_re', 'str.to.re')
        case_former = case_former.replace('str.from_int', 'str.from.int')

        case_former = case_former.replace('str.from-int', 'str.from.int')
        case_former = case_former.replace('str.in-re', 'str.in.re')
        case_former = case_former.replace('str.to-int', 'str.to.int')
        case_former = case_former.replace('str.to-re', 'str.to.re')

    outFile = open(tfile.name, 'w')
    outFile.write(str(case_former))
    outFile.close()
    out, err, time = run_command(
        "timeout " + str(settings.timeout + 1) + " bash -c \'/home/cass/Webstorm_project/solvers/" + solver + "/bin/cvc5" + " "+ "--strings-exp " + " "+ outFile.name + "\'")

    print('solver:', solver)
    print('run time:', time)
    print('out:', out)
    cov = 0
    print('cov:', cov)

    if time > settings.timeout:
        return 'timeout', time, out + err, cov

    if out.lower().find('sat') != -1 or out.lower().find('unsat') != -1:
        return out.lower(), time, out + err, cov

    return 'err', time, out + err, cov
