# py2vega


[![Travis](https://travis-ci.org/QuantStack/py2vega.svg?branch=master)](https://travis-ci.org/QuantStack/py2vega)
[![Chat](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/QuantStack/Lobby)

A Python to [Vega-expression](https://vega.github.io/vega/docs/expressions/) transpiler.

## Installation

### From PyPi

```bash
pip install py2vega
```

### From conda-forge

```bash
conda install -c conda-forge py2vega
```

### From sources

You can install from sources using `pip`:

```bash
git clone https://github.com/QuantStack/py2vega
cd py2vega
pip install .
```


## Usage

`py2vega` provides a `py2vega` function that turns a Python string code or a Python function into a valid [Vega-expression](https://vega.github.io/vega/docs/expressions/). Because it is turning the Python code into a [Vega-expression](https://vega.github.io/vega/docs/expressions/), only a subset of Python is supported: the `if` and `return` statements, the ternary operator, the `in` operator and types like `str`, `bool`, `dict`, `tuple`...

```Python
from py2vega import py2vega

def foo(value):
    if value < 3:
        return 'red'
    elif value < 5:
        return 'green'
    else:
        return 'yellow'

py2vega(foo, whitelist=['value'])  # "if(value < 3, 'red', if(value < 5, 'green', 'yellow'))"
```

`py2vega` also provides functions and constants the same way they are available for vega-expressions:

```Python
from py2vega import py2vega
from py2vega.functions.math import isNaN
from py2vega.functions.string import lower

def foo(value):
    if isNaN(value):
        return lower('It is NaN...')
    else:
        return value

py2vega(foo, whitelist=['value'])  # "if(isNaN(value), lower('It is NaN...'), value)"
```

Even if assignments are prohibited in [Vega-expressions](https://vega.github.io/vega/docs/expressions/), you can assign variables in your Python function, it will be turned into a valid [Vega-expression](https://vega.github.io/vega/docs/expressions/) anyway:

```Python
from py2vega import py2vega

def foo(value):
    a = 'green'
    b = 'red'

    return a if value < 3 else b

py2vega(foo, whitelist=['value'])  # "value < 3 ? 'green' : 'red'"
```

You can provide a variable whitelist as a list of strings, each string being an available variable. You can also allow member access using the `Variable` class from py2vega:

```Python
from py2vega import py2vega, Variable

py2vega('3 if value > 0 else 4', whitelist=['value'])  # Returns "value > 0 ? 3 : 4"
py2vega('3 if my_variable > 0 else 4', whitelist=['value'])  # Raises a SyntaxError, `my_variable` is not whitelisted
py2vega('3 if value.member1 > value.member2 else 4', whitelist=[Variable('value', ['member1', 'member2'])])  # Returns "value.member1 > value.member2 ? 3 : 4"
py2vega('3 if value.member3 > 0 else 4', whitelist=[Variable('value', ['member1', 'member2'])])  # Raises a SyntaxError, `value.member3` is not whitelisted`
```


Because of the way [Vega-expressions](https://vega.github.io/vega/docs/expressions/) are defined, there are some rules that must follow your Python function:
- the function body __must__ end with an `if` __or__ `return` statement and __cannot__ contain more than one `if` __or__ `return` statement
- `if` statements __can__ be followed by `elif` statements but __must__ be followed by an `else` statement
- the `if`/`elif`/`else` body __must__ end with an `if` __or__ `return` statement and __cannot__ contain more than one `if` __or__ `return` statement

If one of those rules is not respected, a Python `RuntimeError` will be raised.
