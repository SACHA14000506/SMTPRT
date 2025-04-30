import os
import src.settings as settings
from src.instance import Instance
import re
import random
import mutate_ml
import gen_ml
import json


class Generator_Str:
    num = 0

    def gen(self):
        folder_path = "/home/cass/Webstorm_project/SMTPRT/folder"
        smt2_files = [file for file in os.listdir(folder_path) if file.endswith(".smt2")]

        if not smt2_files:
            print("NOTFOUND")
        else:
            selected_file = random.choice(smt2_files)
            file_path = os.path.join(folder_path, selected_file)

            with open(file_path, "r", encoding="utf-8") as file:
                smt = file.read()
        assert smt.count('assert') > 0, smt
        return Instance(smt)

    def mutate(self, to_mutate):
        input = to_mutate.primaries
        mutated_output = mutate_ml.generate_mutated_smt2_v2(input)

        if isinstance(mutated_output, str):
            try:
                mutated_dict = json.loads(mutated_output)
            except json.JSONDecodeError:
                print("error:", mutated_output)
                return []
        elif isinstance(mutated_output, dict):
            mutated_dict = mutated_output
        else:
            print("error:", type(mutated_output))
            return []

        instances = []
        for smt_str in mutated_dict.values():
            processed_smt = smt_str.replace('\\n', '\n')
            if 'assert' not in processed_smt:
                continue
            instances.append(Instance(processed_smt))
        return instances


def mk_gen():
    return Generator_Str()
