import os
import sys
from pathlib import Path
path = Path(__file__)
root_path = path.parent.absolute().parent
sys.path.append(str(root_path / 'src'))
print(root_path)

from src.settings import para
import pandas as pd
import time
from src.parser import args
import src.test1 as test1

def delete_cases(path):
    if os.path.exists(path):
        for fpath, _, file_list in os.walk(path):
            for fname in file_list:
                if fname.endswith('.smt2'):
                    os.remove(os.path.join(fpath, fname))
        print('DELET: ', path)

def main():
    parameter = para()
    parameter.type = args.type
    parameter.solvers = args.solvers
    parameter.root_path = root_path
    parameter.timeout = args.timeout
    parameter.time0 = time.time()
    delete_cases(str(parameter.root_path / 'results' / 'Regression_cases'))
    finder = test1.Fuzzer(parameter)
    finder.run()

if __name__ == '__main__':
    df = pd.DataFrame(columns=['time', 'case_number'])
    df.to_csv('./results/Statistics/Total_number.csv')
    df1 = pd.DataFrame(columns=['case', 'solver1', 'solver2', 'solver3', 'var_num',
                                'assert_num', 'nax_str_len', 'max_depth'])
    df1.to_csv('./results/Statistics/Results_for_cases.csv')
    df1.to_csv('./Results.csv', mode='a', header=True)
    main()
