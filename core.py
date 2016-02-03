
import pandas as pd
import numpy as np
import functools
from functools import partial
from string_evaluation import s


def pipe(original):
    """
    Wraps a function that takes a dataframe as its first
    argument, and outputs a dataframe. The '>>' operator
    passes the returned dataframe from the first function
    to the second function as its first argument.

    :param original: the function on the left-hand side of the '>>' operator.
    The function must output a dataframe so that it can be passed to the
    "next" function.

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
def keep(df, *args):
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
def create(df, **kwargs):
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
    # Create a dictionary mapping each variable to its matching
    # dataframe column.
    for var in var_lis:
        names_dict[var] = df[var]
    # Define variables for SimpleEval class object so that they are
    # recognized during evaluation.
    s.names = names_dict
    key_lis = kwargs.keys()
    num_mutations = len(key_lis)
    completed = 0
    check_next = 0
    # The below loop handles possible argument ordering errors (a "new" column being called before it's defined).
    # This is required because Python does not "order" keyword arguments in terms of their given input ordering.
    while completed < num_mutations:
        # Try evaluating a given string.
        try:
            df[key_lis[check_next]] = s.eval(kwargs[key_lis[check_next]])
            s.names[key_lis[check_next]] = df[key_lis[check_next]]
            completed += 1
            check_next += 1
            if check_next > num_mutations:
                check_next = 0
        # If there is an error, move on to another string.
        except:
            if check_next > num_mutations:
                check_next = 0
            else:
                check_next += 1
    return df


@pipe
def select(df, *args):
    """
    Take a dataframe and return a subset dataframe with only the columns
    specified by the givearguments.

    :param df: dataframe
    :param args: each argument is a string containing a single column name.
    :return: dataframe.
    """
    df = df[args]
    return df


@pipe
def slice_rows(df, n, m):
    return df[n:m]


@pipe
def arrange(df, *args, **kwargs):
    if kwargs:
        for key in kwargs:
            asc_lis = kwargs[key]
        if len(args) == 1:
            return df.sort(args[0], ascending=asc_lis)
        else:
            return df.sort(args, ascending=asc_lis)
    if len(args) == 1:
        df.sort()
    df.sort(args)
    return df


@pipe
def rename(df, **kwargs):
    """
    Take a dataframe and change column names as instructed in the
    given keyword arguments.

    :param df: dataframe
    :param kwargs: keyword arguments, each key representing an
    "old" dataframe column, and each key value a string containing
    the "new" column name.
    :return: dataframe
    """
    for name, value in kwargs.items():
        df = df.rename(columns={'%s' % name: '%s' % value})
    return df


@pipe
def distinct(df, *args):
    """
    Take a dataframe and return only distinct values for each
    given column.

    :param df: dataframe
    :param args: each argument is a string containing a single column name.
    :return: dataframe
    """
    for arg in args:
        df = df.drop_duplicates(arg)
    return df


@pipe
def sample_n(df, sample_size):
    """
    Take a dataframe return a subset of random rows as given
    by the "sample_size" argument.

    :param df: dataframe
    :param sample_size: integer: the number of random rows to return.
    :return: dataframe
    """
    return df.sample(n=sample_size)


@pipe
def check(df):
    print df.head()
    continue_process = raw_input("Continue? [y/n]")
    if continue_process == 'y':
        return df
    else:
        exit()


@pipe
def group_by(df, *args):
    df = df.groupby(args, as_index=False)
    return df


@pipe
def summarise(df, **kwargs):

    aggregations = dict()
    target_variables = [kwargs[key]['var'] for key in kwargs]

    for var in target_variables:
        aggregations[var] = dict()
    for key in kwargs:
        aggregations[kwargs[key]['var']][key] = kwargs[key]['type']
    df = df.agg(aggregations)

    mi = df.columns
    new_index_lis = []
    for e in mi.tolist():
        if e[1] == '':
            new_index_lis.append(e[0])
        else:
            new_index_lis.append(e[1])

    ind = pd.Index(new_index_lis)
    df.columns = ind
    return df


@pipe
def wide_to_long(df, **kwargs):
    df = pd.melt(df, **kwargs)
    return df


@pipe
def long_to_wide(df,**kwargs):
    df = pd.melt(df, **kwargs)
    return df


@pipe
def merge_with(df, *args, **kwargs):
    # Map the "expressive" join type labels to their corresponding pandas join type.
    join_types_dict = {'outer_join': 'outer',
                       'inner_join': 'inner',
                       'right_join': 'right',
                       'left_join': 'left'}
    join_type = join_types_dict[kwargs['using']]
    source_df = args[0]
    on = kwargs['on']
    return pd.merge(df, source_df, on=on, how=join_type)



