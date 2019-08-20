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

`py2vega` provides a `py2vega` function that turns a Python string code or a Python function into a valid [Vega-expression](https://vega.github.io/vega/docs/expressions/). Because it is turning the Python code into a Vega-expression, only a subset of Python is supported: the `if` and `return` statements, the ternary operator, the `in` operator and types like `str`, `bool`, `dict`, `tuple`...

```Python
from py2vega import py2vega

def foo(value):
    if value < 3:
        return 'red'
    elif value < 5:
        return 'green'
    else:
        return 'yellow'

foo_expr = py2vega(foo, whitelist=['value'])  # "if(value < 3, 'red', if(value < 5, 'green', 'yellow'))"
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

foo_expr = py2vega(foo, whitelist=['value'])  # "if(isNaN(value), lower('It is NaN...'), value)"
```

Even if assignments are prohibited in Vega-expressions, you can assign variables in your Python function, it will be turned into a valid Vega-expression anyway:

```Python
from py2vega import py2vega

def foo(value):
    a = 'green'
    b = 'red'

    return a if value < 3 else b

foo_expr = py2vega(foo, whitelist=['value'])  # "value < 3 ? 'green' : 'red'"
```
