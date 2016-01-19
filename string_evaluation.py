from simpleeval import simple_eval, SimpleEval
from numpy import *
import pandas as pd
import ast
import operator


math_functions = {
    "exp": exp,
    "log": log,
    "log10": log10,
    "pow": pow,
    "cos": cos,
    "hypot": hypot,
    "sin": sin,
    "tan": tan,
    "mean": mean,
    "std": std,
    "sum": sum,
}

# url = 'http://127.0.0.1:8000/media/data/admin/LifeCycleSavings1.csv'

# df = pd.read_csv(url)

s = SimpleEval(functions=math_functions)

s.operators[ast.BitOr] = operator.or_


