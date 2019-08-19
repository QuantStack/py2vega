# py2vega

A Python to Vega-expression transpiler.

## Installation

You can install from sources using `pip`:

```bash
git clone https://github.com/QuantStack/py2vega
cd py2vega
pip install .
```


## Usage

`py2vega` provides a `py2vega` function that turns a Python string code or a Python function into a valid [vega-expression](https://vega.github.io/vega/docs/expressions/). Because it is turning the Python code into a Vega-expression, only a subset of Python is supported: the `if` and `return` statements, the ternary operator, the `in` operator and types like `str`, `bool`, `dict`, `tuple`...

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

`py2vega` also provides mathematical functions and constants as it is available for vega-expressions:

```Python
from py2vega import py2vega, isNaN

def foo(value):
    if isNaN(value):
        return 'It is NaN...'
    else:
        return value

foo_expr = py2vega(foo, whitelist=['value'])  # "if(isNaN(value), 'It is NaN...', value)"
```
