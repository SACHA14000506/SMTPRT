import os, random, time
import src.settings as settings
from src.solver import run_solver
import subprocess
import pandas as pd

def par2(x):
    if x < settings.timeout:
        return x
    else:
        return settings.timeout

def generate_file(ast, path, name):
    if not os.path.exists(path):
        os.mkdir(path)
    file = open(os.path.join(path, name), 'w+')
    file.write(ast)
    file.close()

class Instance():
    def __init__(self, val=None, statistics=None):
        if settings.theory == 'QF_logic':
            assert isinstance(val, str)
        else:
            assert isinstance(val, list)
        super().__init__()
        self.primaries = val
        self.times = {}
        self.results = {}
        self.name = str(time.time()).replace(".", "") + str(os.getpid()) + str(random.randint(0, 99999999)) + ".smt2"
        self.err_log = {}
        self._score = None
        self.coverage = {}
        self._cov = None
        self.time_list = [0, 0, 0]
        self._fitness = None

    def solve(self):
        for solver in settings.solvers:
            out, time, dump, cov = run_solver(self, solver)
            self.results[solver] = out
            self.times[solver] = par2(time)
            print("self.times[solver]:", self.times[solver])
            self.coverage[solver] = cov
            if out == 'err':
                self.err_log[solver] = dump

    def score_time(self):
        if self._score != None: return self._score
        if self.inconsistent():
            self._score = par2(self.times[settings.solvers[0]]) - min(
                [par2(self.times[solver]) for solver in settings.solvers if solver != settings.solvers[0]])
        elif settings.BugMode:
            self._score = -9.9
        elif len(self.err_log) > 0:
            self._score = 0.0
        elif len(self.times) == 1:
            self._score = par2(self.times[settings.solvers[0]]) if settings.solvers[0] not in self.err_log else float(
                '-inf')
        else:
            self._score = par2(self.times[settings.solvers[0]]) - min([par2(self.times[solver]) for solver in settings.solvers if solver != settings.solvers[0]])
        return self._score

    def score_cov(self):
        if self._cov != None: return self._cov
        if self.inconsistent():
            self._cov = max(self.coverage[settings.solvers[1]] + self.coverage[settings.solvers[2]])
        return self._cov

    def fitness(self):
        self._fitness = 0.85 * self._score + 0.15 * self.score_cov()
        return self._fitness

    def score3(self):
        if self._score != None: return self._score
        if self.inconsistent():
            self._score = par2(self.times[settings.solvers[0]]) - min(
                [par2(self.times[solver]) for solver in settings.solvers if solver != settings.solvers[0]])
        elif settings.BugMode:
            self._score = -9.9
        elif len(self.err_log) > 0:
            self._score = 0.0
        elif len(self.times) == 1:
            self._score = par2(self.times[settings.solvers[0]]) if settings.solvers[0] not in self.err_log else float(
                '-inf')
        else:
            self._score = par2(self.times[settings.solvers[0]]) - min([par2(self.times[solver]) for solver in settings.solvers if solver != settings.solvers[0]])
        return self._score

    def __lt__(self, other):
        return self.score() < other.score()

    def __str__(self):
        return self.primaries

    __repr__ = __str__

    def inconsistent(self):
        for solver in self.results:
            clean = ""
            for i in range(len(self.results[solver])):
                if self.results[solver][i].isalpha():
                    clean = clean + self.results[solver][i]
            self.results[solver] = clean
        ans = ""
        says_sat = False
        says_unsat = False
        for solver in self.results:
            if self.results[solver] == "sat":
                says_sat = True
            if self.results[solver] == "unsat":
                says_unsat = True
        return says_sat and says_unsat
