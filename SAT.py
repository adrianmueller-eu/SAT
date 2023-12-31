import json
import itertools
import sys
import os

if __name__ == "SAT": # Is there a better way?
    from logic import * #ATOM, AND, OR, NOT, IMPL, EQVI, XOR, NAND
    from solvers import * #dpll, z3wrapper, z3available
else: # "SAT.SAT"
    from .logic import *
    from .solvers import *

class SAT:

    def __init__(self, useDPLL=False):
        self.debug = False

        if useDPLL or not z3available():
            self.delegate = dpll
        else:
            self.delegate = z3wrapper

    def solve(self, formula):
        clauses = self.cnf(formula)
        return self.delegate(clauses)

    def table(self, formula, verbose=True, trueOnly=False):
        original = formula
        formula = self._parse(formula)
        variables = formula.vars()
        variables = sorted(variables)

        if verbose:
            res = "%s | %s\n" % (" ".join(variables), original)
            res += "-" * len(res)
            print(res)

        data = {}
        for valuation in itertools.product([0, 1], repeat=len(variables)):
            v_dict = generateValuationDict(valuation, variables)
            sat = formula.is_satisfiable(v_dict)
            if not trueOnly or sat:
                key = valuation
                data[key] = sat
                if verbose:
                    print("%s | %s" % (" ".join([str(i) for i in key]), "\033[1m*True\033[0m" if sat else "False"))

        return data, variables

    def valid(self, f):
        f = "~(%s)" % f
        result, _ = self.solve(f)
        return not result

    # returns whether f1 is logical consequence of f2
    def logCon(self, f1, f2):
        f = "(%s) & ~(%s)" % (f1, f2)
        result, _ = self.solve(f)
        return not result

    def logEq(self, f1, f2):
        return self.logCon(f1, f2) and self.logCon(f2, f1)

    def modelCnt(self, f):
        table, _ = self.table(f, verbose=False, trueOnly=True)
        return len(table)

    def _parse(self, formula):
        def getFormula(f):
            if "operator" in f:
                o = f["operator"]
                if o == "∧":
                    sub1 = getFormula(f["sub1"])
                    sub2 = getFormula(f["sub2"])
                    return AND([sub1, sub2])
                elif o == "∨":
                    sub1 = getFormula(f["sub1"])
                    sub2 = getFormula(f["sub2"])
                    return OR([sub1, sub2])
                elif o == "¬":
                    sub = getFormula(f["sub"])
                    return NOT(sub)
                elif o == "^":
                    sub1 = getFormula(f["sub1"])
                    sub2 = getFormula(f["sub2"])
                    return XOR(sub1, sub2)
                elif o == "→":
                    sub1 = getFormula(f["sub1"])
                    sub2 = getFormula(f["sub2"])
                    return IMPL(sub1, sub2)
                elif o == "←":
                    sub1 = getFormula(f["sub1"])
                    sub2 = getFormula(f["sub2"])
                    return IMPL(sub2, sub1)
                elif o == "↔":
                    sub1 = getFormula(f["sub1"])
                    sub2 = getFormula(f["sub2"])
                    return EQVI(sub1, sub2)
                elif o == "⊼":
                    sub1 = getFormula(f["sub1"])
                    sub2 = getFormula(f["sub2"])
                    return NAND(sub1, sub2)
            else:
                name = f["string"]
                return ATOM(name)

        path = os.path.dirname(__file__)
        parser = ["node", path + "/parser.js", formula]
        returncode, f = call(parser)
        if returncode != 0:
            raise ValueError("Have you written the formula correctly?")
        f = json.loads(f)[1]
        if self.debug:
            print("node output:", f)
        f = getFormula(f)
        if self.debug:
            print("formatted:", f)
        return f

    def cnf(self, formula, verbose=False):
        formula = self._parse(formula)
        clauses = formula.clauses()
        if verbose or self.debug:
            res = []
            for clause in clauses:
                res_c = []
                for x,val in clause:
                    if val:
                        res_c.append(x)
                    else:
                        res_c.append("¬"+x)
                if len(res_c) > 1:
                    res.append("("+" ∨ ".join(res_c)+")")
                else:
                    res.append(res_c[0])
            print(" ∧ ".join(res))
        return clauses

##############################
### convenience functions
##############################

def solve(formula, useDPLL=True):
    sat = SAT(useDPLL)
    return sat.solve(formula)

def table(formula, verbose=True, trueOnly=False): # no solver needed
    sat = SAT(True) # "True" just because faster init
    return sat.table(formula, verbose, trueOnly=trueOnly)

def valid(formula, useDPLL=True):
    sat = SAT(useDPLL)
    return sat.valid(formula)

# returns whether f1 is a logical consequence of f2
def logCon(f1, f2, useDPLL=True):
    sat = SAT(useDPLL)
    return sat.logCon(f1, f2)

def logEq(f1, f2, useDPLL=True):
    sat = SAT(useDPLL)
    return sat.logEq(f1, f2)

def modelCnt(formula): # no solver needed
    sat = SAT(True) # "True" just because faster init
    return sat.modelCnt(formula)

def cnf(formula, verbose=False):
    sat = SAT(True) # "True" just because faster init
    return sat.cnf(formula, verbose)

##############################
### helper functions
##############################

def call(cmd):
    import subprocess

    sub = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if sub.stderr:
        print(sub.stderr.decode('utf-8'), file=sys.stderr)
    return sub.returncode, sub.stdout.decode('utf-8')

def generateValuationDict(bitvector, variables):
    res = {}
    for b,v in zip(bitvector, variables):
        res[v] = b == 1
    return res
