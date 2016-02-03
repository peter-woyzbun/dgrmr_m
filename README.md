# dgrmr (Data Grammar)

`dgrmr` is a small package for data manipulation in Python, using `pandas`, inspired by (an imitation of) Hadley Wickham's 
R package `dplyr`. The goal is to make for more structured, readable, and intuitive data manipulation code. Internally, it is 
 essentially a collection of functions layered over `pandas`, and a new "pipe" operator.

The "pipe" operator, `>>`, turns `x >> f(y)`into `f(x,y)`. It allows for the chaining together of any number of `dgrmr` 
functions. That is, it passes the dataframe output from one function to the next. The idea is to manipulate a dataframe 
with a clear, concise, ordered set of instructions.

### Example
```python
df = df >> keep('origin == JFK', 'dest == SFO') \
        >> create(speed='distance / air_time * 60',
                  log_speed = 'log(speed)') \
        >> merge_with(df_n, on='carrier', using='outer_join') \
        >> group_by('carrier') \
        >> summarise(mean_t_delay=('mean', 't_delay'),
                     max_t_delay_hrs=('max', 't_delay_hrs')) \
        >> order_by('mean_t_delay')
```

## Installation

You can either copy `dgrmr.py` into your project folder, or use pip:

```
pip install dgrmr
```


## Comparison: `dgrmr` vs. `pandas`

To show how `dgrmr` works, the following examples use the `nycflights13` dataset
that comes built in with `dplyr`. It consists of all 336776 flights that
departed NYC in 2013 - the first five rows are shown below. Each example 
shows how a data manipulation task would be accomplished with `pandas`, 
and then with the equivalent `dgrmr` approach.

#### `nycflights13`

```python
     Unnamed: 0  year  month  day  dep_time  dep_delay  arr_time  arr_delay  \
0           1  2013      1    1       517          2       830         11   
1           2  2013      1    1       533          4       850         20   
2           3  2013      1    1       542          2       923         33   
3           4  2013      1    1       544         -1      1004        -18   
4           5  2013      1    1       554         -6       812        -25   

  carrier tailnum  flight origin dest  air_time  distance  hour  minute  
0      UA  N14228    1545    EWR  IAH       227      1400     5      17  
1      UA  N24211    1714    LGA  IAH       227      1416     5      33  
2      AA  N619AA    1141    JFK  MIA       160      1089     5      42  
3      B6  N804JB     725    JFK  BQN       183      1576     5      44  
4      DL  N668DN     461    LGA  ATL       116       762     5      54  
```

Suppose we want to compare delay times between carriers, and specifically
flights between JFK and SFO. Using `pandas`, the code is:

```python
df = df[(df.origin == 'JFK') & (df.dest == 'SFO')]
df['t_delay'] = df['arr_delay'] / df['dep_delay']
df['t_delay_hrs'] = df['t_delay'] / 60
gf = df.groupby('carrier')
gf = gf.agg({'t_delay': {'mean_t_delay': mean,
                         'max_t_delay_hrs': max}})
gf.sort('mean_t_delay', ascending=False)                         
```

Using `dgrmr`:
```python
df = df >> keep('origin == JFK', 'dest == SFO') \
        >> create(t_delay='arr_delay + dep_delay',
                  t_delay_hrs='t_delay / 60')\
        >> group_by('carrier') \
        >> summarise(mean_t_delay=('mean', 't_delay'),
                     max_t_delay_hrs=('max', 't_delay_hrs')) \
        >> order_by('mean_t_delay', ascending=False)
```

## Basic Functions

Each of the basic `dgrmr` functions performs a fundamental data manipulation task.

### `keep()`

The `keep()` function subsets a given dataframe, keeping only those rows that meet
the conditions provided. Each condition is contained in a string and may use
column names, logical operators, and math functions.

```python
df = df >> keep('origin == JFK', 'dest == SFO')
```

### `create()`

The `create()` function is used for creating new dataframe columns. The
name of the column is defined by the keyword argument. Each new column is
defined in a string and may use dataframe column names, logical operators,
math functions, and any column defined in the arguments given.

```python
df = df >> create(t_delay='arr_delay + dep_delay',
                  t_delay_hrs='t_delay / 60')
```

### `select()`

The `select()` function is used to subset a given dataframe, returning the dataframe with only those columns included
in the arguments.

```python
df = df >> select('origin', 'dest', 'arr_delay')
```

### `rename()`

The `rename()` function is used to rename dataframe columns.

```python
df = df >> rename(origin='origin_new')
```

### `group_by()`

The `group_by()` function is used for creating new dataframe columns. The
name of the column is defined by the keyword argument. Each new column is
defined in a string and may use dataframe column names, logical operators,
math functions, and any column defined in the arguments given.

```python
df = df >> select('origin', 'dest', 'arr_delay')
```


### `summarise()`

The `select()` function is used for creating new dataframe columns. The
name of the column is defined by the keyword argument. Each new column is
defined in a string and may use dataframe column names, logical operators,
math functions, and any column defined in the arguments given.

```python
df = df >> select('origin', 'dest', 'arr_delay')
```


### `order_by()`

The `select()` function is used for creating new dataframe columns. The
name of the column is defined by the keyword argument. Each new column is
defined in a string and may use dataframe column names, logical operators,
math functions, and any column defined in the arguments given.

```python
df = df >> select('origin', 'dest', 'arr_delay')
```

### `merge_with()`

The `merge_with()` function is used for creating new dataframe columns. The
name of the column is defined by the keyword argument. Each new column is
defined in a string and may use dataframe column names, logical operators,
math functions, and any column defined in the arguments given.

```python
df = df >> select('origin', 'dest', 'arr_delay')
```

### `apply_function()`

`apply_function()` function is used for creating new dataframe columns. The
name of the column is defined by the keyword argument. Each new column is
defined in a string and may use dataframe column names, logical operators,
math functions, and any column defined in the arguments given.

```python
df = df >> select('origin', 'dest', 'arr_delay')
```

## How it Works

String arguments that require parsing - those used in the `keep()` function, for example - are handled by the 
`simpleeval` package. The `simpleeval` package allows for the evaluation of expressions, contained in strings,
using defined functions and variables ("names). For example, 

```python
simple_eval('one = 1', names={'one': df['one'})
```

has the same effect as

```python
df['one'] = 1
```



