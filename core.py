
import pandas as pd
import numpy as np
import functools
from functools import partial
from string_evaluation import s


def pipe(original):
    class PipeInto(object):
        data = {'function': original}

        def __init__(self, *args, **kwargs):
            self.data['args'] = args
            self.data['kwargs'] = kwargs

        def __rrshift__(self, other):
            return self.data['function'](
                other,
                *self.data['args'],
                **self.data['kwargs']
            )

    return PipeInto


def conjunction(*conditions):
    return functools.reduce(np.logical_and, conditions)


@pipe
def filter(df, *args):
    var_lis = df.columns.values.tolist()
    names_dict = {}
    for var in var_lis:
        names_dict[var] = df[var]
    # Define variables for SimpleEval class object.
    s.names = names_dict
    for arg in args:
        df = df[s.eval(arg)]
    df.reset_index()
    return df


@pipe
def mutate(df, **kwargs):
    var_lis = df.columns.values.tolist()
    names_dict = {}
    for var in var_lis:
        names_dict[var] = df[var]
    # Define variables for SimpleEval class object.
    s.names = names_dict
    key_lis = kwargs.keys()
    num_mutations = len(key_lis)
    completed = 0
    check = 0
    # The below loop handles possible argument ordering errors (a "new" column being called before it's defined).
    # Python does not "order" keyword arguments in terms of their input positioning.
    while completed < num_mutations:
        try:
            df[key_lis[check]] = s.eval(kwargs[key_lis[check]])
            s.names[key_lis[check]] = df[key_lis[check]]
            completed += 1
            check += 1
            if check > num_mutations:
                check = 0
        except:
            if check > num_mutations:
                check = 0
            else:
                check += 1
    return df

@pipe
def transmute(df, **kwargs):
    var_lis = df.columns.values.tolist()
    names_dict = {}
    for var in var_lis:
        names_dict[var] = df[var]
    # Define variables for SimpleEval class object.
    s.names = names_dict
    key_lis = kwargs.keys()
    num_mutations = len(key_lis)
    completed = 0
    check = 0
    new_vars = []
    while completed < num_mutations:
        try:
            df[key_lis[check]] = s.eval(kwargs[key_lis[check]])
            s.names[key_lis[check]] = df[key_lis[check]]
            new_vars.append(key_lis[check])
            completed += 1
            check += 1
            if check > num_mutations:
                check = 0
        except:
            if check > num_mutations:
                check = 0
            else:
                check += 1
    return df[new_vars]

@pipe
def filter_old(df, *args):
    for arg in args:
        c = arg
        df = df[conjunction(c)]
    return df


@pipe
def select(df, *args):
    cols = [x for x in args]
    df = df[cols]
    return df


@pipe
def rename(df, **kwargs):
    """ SOME COMMENT LOL"""
    for name, value in kwargs.items():
        df = df.rename(columns={'%s' % name: '%s' % value})
    return df


@pipe
def distinct(df, *args):
    for arg in args:
        df = df.drop_duplicates(arg)
    return df


@pipe
def sample_n(df, sample_size):
    return df.sample(n=sample_size)


@pipe
def preview(df):
    print df.head()
    continue_process = raw_input("Continue? [y/n]")
    if continue_process == 'y':
        return df
    else:
        exit()


@pipe
def group_by(df, *args):
    df = df.groupby(args, as_index=False)
    print df
    return df


@pipe
def summarise_temp(df, **kwargs):
    var_lis = df.columns.values.tolist()
    names_dict = {}
    for var in var_lis:
        names_dict[var] = df[var]
    # Define variables for SimpleEval class object.
    s.names = names_dict
    summary_df = pd.DataFrame(index=df.index)
    for key in kwargs:
        summary_df[key] = s.eval(kwargs[key])


@pipe
def summarise_temp1(df, **kwargs):
    mapping_dict = {'mean': np.mean, 'sum': np.sum}
    for key in kwargs:
        func = mapping_dict[kwargs[key]]
        kwargs[key] = func
    return df.agg(kwargs)


@pipe
def summarise(df, **kwargs):

    def target_var(s):
        return s[s.find("(")+1:s.find(")")]

    def agg_type(s):
        return s[:s.find("(")]

    aggregations = dict()

    target_variables = [target_var(kwargs[key]) for key in kwargs]

    print target_variables

    for var in target_variables:
        aggregations[var] = dict()

    for key in kwargs:
        aggregations[target_var(kwargs[key])][key] = agg_type(kwargs[key])

    df = df.agg(aggregations).reset_index()

    print list(df.columns.get_level_values(1))

    df.columns = [''.join(t) for t in df.columns]

    print df

    return df

