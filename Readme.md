A simple [SAT solver](https://en.wikipedia.org/wiki/SAT_solver). Can be used from command line or in a python script.

# Requirements
- python >= 3.8
- [`node`](https://nodejs.org/en/download/)
- optional: `pip install [z3-solver](https://github.com/z3prover/z3)`

# Installation
Copy this directory to your custom python site-packages, which you can find by executing
```
python -m site --user-site
```

# Usage
Then, import in python as
```
from SAT import solve, table

res = solve('a -> b')
print(res)

print() # newline

table('(a -> b) & (b <-> c) <-> (b & ~c)')
```

Or execute it directly from command line
```
python -m SAT '(a -> b) & (b <-> c) <-> (b & ~c)'
```

The command line help message gives more details
```
A SAT solver.
Usage: sat [-h | -t | -tt | -c | --cnf] formula
	-t, --table         Show the whole truth table.
	-tt, --table-true   Show the rows of the truth table where formula is satiesfied
	-c, --count         Count the world in which formula is satisfied.
	--cnf               Output formula in CNF.
	--dpll              Use python dpll solver instead of z3-solver.

Examples:
	sat "a and b"
	sat "(~a | b) & (a -> c) & (b -> ~c) & a"
	sat -t "a <-> b and a -> ~b"
	sat -tt "(a -> b) & (b <-> c) <-> (b & ~c)"
	sat -c "a <- not b and not c and b"
	sat --cnf "r and not q or not t"
```

# TODO
- Rewrite parser to python
