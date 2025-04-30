import src.utils as utils
import sys, os, random, time
from gen import mk_gen
import pandas as pd
import src.settings as settings
import datetime


class Fuzzer:
    def __init__(self, parameter):
        self.init_time = parameter.time0
        self.time0 = parameter.time0
        self.it = 0
        self.find = False
        self.num_pop = 50
        self.max_iterations = 10
        self.gen = mk_gen()
        self.all_solved = set()
        self.pop = []
        self.all_achived = set()

    def initialize_population(self):
        print("Initializing population...\n")
        for i in range(self.num_pop):
            inst = self.gen.gen()
            while str(inst) in self.all_solved:
                inst = self.gen.gen()
            inst.solve()
            self.pop.append(inst)
            self.all_solved.add(str(inst))

    def print_instance_info(self, index, label, inst):
        print("(%d/%-d)%-15sTimes = %-25s Score = %-7f IsSat = %-25s" % (
            index + 1, self.num_pop, label, utils.roundedmap(inst.times, 3), inst.score_time(), inst.results,
        ))
        print("score:", inst._score)

    def fitness_function(self, inst):
        return inst._score

    def mutate(self, individual):
        valid_mutants = []
        mutated_list = self.gen.mutate(individual)

        for mutated in mutated_list:
            if str(mutated) not in self.all_solved:
                mutated.solve()
                self.all_solved.add(str(mutated))
                valid_mutants.append(mutated)

        if not valid_mutants:
            print("No new mutants in this batch")
        return valid_mutants

    def pick(self, pop):
        is_find = False
        for i in range(len(pop)):
            print("pop[i]._score: ", pop[i]._score)
            if pop[i]._score >= 5:
                is_find = True
                if str(pop[i].primaries) not in self.all_achived:
                    settings.reg_num += 1
                    utils.generate_file(pop[i].primaries,
                                        settings.reg_path, settings.mode + str(settings.reg_num) + '.smt2')
                    settings.file_num += 1
                    df1 = pd.DataFrame({
                        'File': [settings.mode + str(settings.reg_num) + '.smt2'],
                        'Solver1_Time': [pop[i].times[settings.solvers[0]]],
                        'Solver2_Time': [pop[i].times[settings.solvers[1]]],
                        'Solver3_Time': [pop[i].times[settings.solvers[2]]],
                        'Time': [datetime.datetime.now().strftime("%Y-%m-%d %H:%M")]
                    })
                    df1.to_csv('./Results.csv', mode='a', header=False, index=False)
                    pop[i] = self.gen.gen()
                    pop[i].solve()
                    settings.found_time_list.append(
                        [pop[i].times[settings.solvers[0]],
                         pop[i].times[settings.solvers[1]], pop[i].times[settings.solvers[2]]])
        return pop, is_find

    def evolve(self):
        iteration = 0
        print("Evolving population...")

        while iteration < self.max_iterations:
            iteration += 1
            print("--------------------------------------------------------------------------------")
            print(f"Iteration: {iteration}/{self.max_iterations}")
            print("--------------------------------------------------------------------------------")

            next_generation = []
            item = 0
            for individual in self.pop:
                item += 1
                mutants = self.mutate(individual)

                for idx, mutated in enumerate(mutants, 1):
                    mutated._fitness = mutated.score_time()
                    print("score_time:", mutated._score)
                    mutated.score_cov()
                    mutated.fitness()
                    print(f"第{iteration}轮，第{idx}次变异得分:", mutated._fitness)

                if mutants:
                    best_mutant = max(mutants, key=lambda x: x._fitness)
                    print(f"第{iteration}轮第{item}个，最佳score：{best_mutant._fitness}")
                    next_generation.append(best_mutant)
                else:
                    print(f"第{iteration}轮第{item}个未生成有效变异体，保留原个体")
                    next_generation.append(individual)

            self.pop = next_generation[:self.num_pop]

            self.pop, is_find = self.pick(self.pop)

    def run(self):
        print("Starting Fuzzer...")
        max_restarts = 100
        restart_count = 0

        while restart_count <= max_restarts:
            restart_info = {
                'Restart Count': restart_count,
                'Max Restarts': max_restarts,
                'Time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Info': f"=== 重启进化循环 ({restart_count}/{max_restarts}) ==="
            }

            df_restart_info = pd.DataFrame([restart_info])
            df_restart_info.to_csv('./Results.csv', mode='a', header=False, index=False)
            print(f"\n=== 循环 ({restart_count}/{max_restarts}) ===")

            self.initialize_population()
            self.evolve()

            restart_count += 1
