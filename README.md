# dgrmr (Data Grammar)


A small library for data manipulation in Python inspired by (and 
a cheap immitation of) Hadley Wickham's R package `dplyr`. The goal is to
make for more structured, readable, and intuitive data manipulation. It 
is essentially a modified subset of `pandas`.


The core feature is the "pipe" operator, `>>`, which turns `x >> f(y)`
into `f(x,y)`. It allows for the chaining together of any number
of data manipulation functions. The idea is to pass a dataframe 
through a clear, concise, ordered set of instructions.

The code below is an example of one such instruction set.

```python
df = df >> filter('origin == JFK', 'dest == SFO') \
        >> create(speed='distance / air_time * 60',
                  log_speed = 'log(speed)') \
        >> group_by('carrier') \
        >> summarise(mean_arr_delay=mean(arr_delay),
                     mean_dep_delay=mean(dep_delay),
                     mean_speed=mean(speed))
```




## Examples

To get very simple evaluating:

```python
df = df >> filter('month == 1', 'day == 1', '(dep_delay == 2) | (dep_delay == 3)') \
        >> rename(month='idiotMonth')\
        >> mutate(futureYear='year + 1000', doubleFutureYear='futureYear + 1000') \
        >> preview() \
        >> select('futureYear', 'doubleFutureYear') \
        >> mutate(tripleFutureYear='doubleFutureYear + 1000')
```

returns `42`.

Expressions can be as complex and convoluted as you want:

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

returns `535.714285714`.

You can add your own functions in as well.

```python
# Filter dataframe for origin and destination.
df = df[(df.origin == 'JFK') & (df.dest == 'SFO')]
# Define the 'gain', 'speed', and 'gain_per_hour' columns.
df['gain'] = df['arr_delay'] - df['dep_delay']
df['speed'] = df['distance'] / df['air_time'] * 60
df['gain_per_hour'] = df['gain'] / (df['air_time'] * 60)
# Group by carrier.
gf = df.groupby('carrier')
# Get aggregate statistics.
gf = gf.agg({'arr_delay': {'mean_arr': mean}, 'speed': {'mean_speed': mean}})


df = df >> filter('origin == JFK', 'dest == SFO') \
        >> mutate(gain='arr_delay - dep_delay',
                  speed='distance / air_time * 60',
                  gain_per_hour='gain / (air_time / 60)') \
        >> group_by('carrier') \
        >> summarise(mean_arr='mean(arr_delay)', mean_speed='mean(speed)')
```

returns `121`.

For more details of working with functions, read [The docs on pypi](https://pypi.python.org/pypi/simpleeval)

### Note:
all further examples use `>>>` to designate python code, as if you are using the python interactive
prompt.

## Limited Power

Also note, the `**` operator has been locked down by default to have a maximum input value
of `4000000`, which makes it somewhat harder to make expressions which go on for ever.  You
can change this limit by changing the `simpleeval.POWER_MAX` module level value to whatever
is an appropriate value for you (and the hardware that you're running on) or if you want to
completely remove all limitations, you can set the `s.operators[ast.Pow] = operator.pow` or make
your own function.

On my computer, `9**9**5` evaluates almost instantly, but `9**9**6` takes over 30 seconds.
Since `9**7` is `4782969`, and so over the `POWER_MAX` limit, it throws a
``NumberTooHigh` exception for you. (Otherwise it would go on for hours, or until the computer
runs out of memory)

## String Safety

There are also limits on string length (100000 characters, `MAX_STRING_LENGTH`).
This can be changed if you wish.

## If Expressions

You can use python style `if x then y else z` type expressions:

```python
    >>> simple_eval("'equal' if x == y else 'not equal'",
                    names={"x": 1, "y": 2})
    'not equal'
```
which, of course, can be nested:

```python
    >>> simple_eval("'a' if 1 == 2 else 'b' if 2 == 3 else 'c'")
    'c'
```

## Functions

You can define functions which you'd like the expressions to have access to:

```python
    >>> simple_eval("double(21)", functions={"double": lambda x:x*2})
    42
```

You can define "real" functions to pass in rather than lambdas, of course too, and even re-name them so that expressions can be shorter

```python
    >>> def double(x):
            return x * 2
    >>> simple_eval("d(100) + double(1)", functions={"d": double, "double":double})
    202
```

## Names

Sometimes it's useful to have variables available, which in python terminology are called 'names'.

```python
    >>> simple_eval("a + b", names={"a": 11, "b": 100})
    111
```

You can also hand the handling of names over to a function, if you prefer:

```python
    >>> def name_handler(node):
            return ord(node.id[0].lower(a))-96

    >>> simple_eval('a + b', names=name_handler)
    3
```

That was a bit of a silly example, but you could use this for pulling values from a database or file, say, or doing some kind of caching system.

## Creating an Evaluator Class

Rather than creating a new evaluator each time, if you are doing a lot of evaluations,
you can create a SimpleEval object, and pass it expressions each time (which should be a bit quicker, and certainly more convenient for some use cases):

```python
    s = SimpleEval()
    s.eval("1 + 1")
    # and so on...
```
You can assign / edit the various options of the `SimpleEval` object if you want to.
Either assign them during creation (like the `simple_eval` function)

```python
    s = SimpleEval(functions={"boo": boo})
```

or edit them after creation:

```python
    s.names['fortytwo'] = 42
```

this actually means you can modify names (or functions) with functions, if you really feel so inclined:

```python
    s = SimpleEval()
    def set_val(name, value):
        s.names[name.value] = value.value
        return value.value

    s.functions = {'set': set_val}

    s.eval("set('age', 111)")
```
Say.  This would allow a certain level of 'scriptyness' if you had these evaluations happening as callbacks in a program.  Although you really are reaching the end of what this library is intended for at this stage.

## Other...

The library supports both python 2 and 3 using the 2to3 converter.

Please read the `test_simpleeval.py` file for other potential gotchas or details.  I'm very happy to accept pull requests, suggestions, or other issues.  Enjoy!