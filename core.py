
import pandas as pd
import numpy as np
import functools
from functools import partial
from string_evaluation import s


def pipe(original):
    """
    Wraps a function that takes a dataframe as its first
    argument, and outputs a dataframe. The '>>' operator
    passes the output dataframe from the first function
    to the second function as its first argument.

    """
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


def get_non_numeric_vars(df):
    df = df.select_dtypes(include=['bool', 'category', 'object'])
    string_values = []
    for column in df:
        string_values += list(df[column].unique())
    return string_values


@pipe
def filter(df, *args):
    """
    Take a dataframe and return only rows who meet the conditions
    provided in the arguments.

    :param df: dataframe
    :param args: strings containing dataframe column names, math functions,
    and logical operators. The strings are evaluated using the 'simpleeval'
    package.
    :return: dataframe
    """
    var_lis = df.columns.values.tolist()
    names_dict = {}
    for var in var_lis:
        names_dict[var] = df[var]

    # Get all distinct, non-numeric dataframe column values
    # in order to define them for simpleeval.
    value_vars = get_non_numeric_vars(df)
    for var in value_vars:
        names_dict[var] = var

    # Define variables for SimpleEval class object.
    s.names = names_dict
    for arg in args:
        df = df[s.eval(arg)]
    df.reset_index()
    return df


@pipe
def mutate(df, **kwargs):
    """
    Take a dataframe, add new columns defined by keyword arguments,
    and output the dataframe.

    :param df: dataframe
    :param kwargs: keyword arguments, whose keys define each new
    column name, and whose values are strings evaluated by the
    'simpleeval' package. Strings contain only column names,
    math functions, integers, and logical operators.
    :return: dataframe
    """
    # Get column names.
    var_lis = df.columns.values.tolist()
    names_dict = {}
    for var in var_lis:
        names_dict[var] = df[var]
    # Define variables for SimpleEval class object so that they are
    # recognized during evaluation.
    s.names = names_dict
    key_lis = kwargs.keys()
    num_mutations = len(key_lis)
    completed = 0
    check = 0
    # The below loop handles possible argument ordering errors (a "new" column being called before it's defined).
    # Python does not "order" keyword arguments in terms of their input positioning.
    while completed < num_mutations:
        # Try evaluating a given string.
        try:
            df[key_lis[check]] = s.eval(kwargs[key_lis[check]])
            s.names[key_lis[check]] = df[key_lis[check]]
            completed += 1
            check += 1
            if check > num_mutations:
                check = 0
        # If there is an error, move on to another string first.
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
def select(df, *args):
    df = df[args]
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

    def mean(var):
        return {'type': 'mean', 'var': var}

    aggregations = dict()

    target_variables = [target_var(kwargs[key]) for key in kwargs]

    print target_variables

    for var in target_variables:
        aggregations[var] = dict()

    for key in kwargs:
        aggregations[target_var(kwargs[key])][key] = agg_type(kwargs[key])

    df = df.agg(aggregations).reset_index()

    df.columns = [''.join(t) for t in df.columns]

    return df


@pipe
def wide_to_long(df,**kwargs):
    df = pd.melt(df, **kwargs)
    return df


@pipe
def long_to_wide(df,**kwargs):
    df = pd.melt(df, **kwargs)
    return df

