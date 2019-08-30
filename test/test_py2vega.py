import pytest

from py2vega import py2vega, Variable
from py2vega.main import Py2VegaSyntaxError, Py2VegaNameError
from py2vega.functions.math import isNaN

whitelist = ['value', 'x', Variable('cell', ['value', 'x'])]


def test_nameconstant():
    code = 'False'
    assert py2vega(code, whitelist) == 'false'

    code = 'True'
    assert py2vega(code, whitelist) == 'true'

    code = 'None'
    assert py2vega(code, whitelist) == 'null'


def test_num():
    code = '36'
    assert py2vega(code, whitelist) == '36'


def test_str():
    code = '\'white\''
    assert py2vega(code, whitelist) == '\'white\''


def test_tuple():
    code = '(True, 3, \'hello\')'
    assert py2vega(code, whitelist) == '[true, 3, \'hello\']'

    code = '((True, 3, \'hello\'), 3)'
    assert py2vega(code, whitelist) == '[[true, 3, \'hello\'], 3]'


def test_list():
    code = '[True, 3, \'hello\']'
    assert py2vega(code, whitelist) == '[true, 3, \'hello\']'


def test_dict():
    code = '{\'hello\': 3, \'there\': 4}'
    assert py2vega(code, whitelist) == '{\'hello\': 3, \'there\': 4}'

    code = '{\'hello\': 3, \'there\': 4}'
    assert py2vega(code, whitelist) == '{\'hello\': 3, \'there\': 4}'


def test_unary():
    code = 'not value'
    assert py2vega(code, whitelist) == '!(value)'

    code = '-value'
    assert py2vega(code, whitelist) == '-value'

    code = '+value'
    assert py2vega(code, whitelist) == '+value'


def test_binary():
    code = 'value or 3'
    assert py2vega(code, whitelist) == '(value || 3)'

    code = 'value and 3'
    assert py2vega(code, whitelist) == '(value && 3)'

    code = 'value + 3'
    assert py2vega(code, whitelist) == '(value + 3)'

    code = 'value**3'
    assert py2vega(code, whitelist) == '(pow(value, 3))'

    # Unsupported operator
    code = 'value & x'
    with pytest.raises(Py2VegaSyntaxError):
        py2vega(code, whitelist)


def test_ternary():
    code = '3 if value else 4'
    assert py2vega(code, whitelist) == '(value ? 3 : 4)'


def test_compare():
    code = '3 < value <= 4'
    assert py2vega(code, whitelist) == '(3 < value <= 4)'

    code = 'value in (\'ford\', \'chevrolet\')'
    assert py2vega(code, whitelist) == '(indexof([\'ford\', \'chevrolet\'], value) != -1)'

    code = '\'chevrolet\' in value'
    assert py2vega(code, whitelist) == '(indexof(value, \'chevrolet\') != -1)'

    code = '\'chevrolet\' not in value'
    assert py2vega(code, whitelist) == '(indexof(value, \'chevrolet\') == -1)'


def test_call():
    code = 'toBoolean(3)'
    assert py2vega(code, whitelist) == 'toBoolean(3)'

    code = 'bool(3)'
    assert py2vega(code, whitelist) == '(isValid(3) ? toBoolean(3) : false)'

    code = 'py2vega.string.toString(3)'
    assert py2vega(code, whitelist) == 'toString(3)'

    code = 'str(3)'
    assert py2vega(code, whitelist) == 'toString(3)'

    code = 'toNumber("3")'
    assert py2vega(code, whitelist) == 'toNumber(\'3\')'

    code = 'float("3")'
    assert py2vega(code, whitelist) == 'toNumber(\'3\')'

    code = 'int("3")'
    assert py2vega(code, whitelist) == 'floor(toNumber(\'3\'))'

    code = 'length(value)'
    assert py2vega(code, whitelist) == 'length(value)'

    code = 'len(value)'
    assert py2vega(code, whitelist) == 'length(value)'

    # Unsupported function
    code = 'foo(value)'
    with pytest.raises(Py2VegaNameError):
        py2vega(code, whitelist)


def test_subscript():
    code = 'value[0]'
    assert py2vega(code, whitelist) == 'value[0]'

    code = '[34, 32][0 if value < 2 else 1]'
    assert py2vega(code, whitelist) == '[34, 32][((value < 2) ? 0 : 1)]'

    code = 'value[:2]'
    assert py2vega(code, whitelist) == 'slice(value, 0, 2)'

    code = 'value[1:]'
    assert py2vega(code, whitelist) == 'slice(value, 1)'

    code = 'value[:]'
    assert py2vega(code, whitelist) == 'slice(value, 0)'

    code = 'value[1:2]'
    assert py2vega(code, whitelist) == 'slice(value, 1, 2)'

    # Unsupported step parameter
    code = 'value[::2]'
    with pytest.raises(Py2VegaSyntaxError):
        py2vega(code, whitelist)

    # Unsupported ExtSlice node
    code = 'value[::2, 1:]'
    with pytest.raises(Py2VegaSyntaxError):
        py2vega(code, whitelist)


def test_attribute():
    code = 'cell.value'
    assert py2vega(code, whitelist) == 'cell.value'

    with pytest.raises(NameError):
        py2vega('cell.value')

    with pytest.raises(Py2VegaSyntaxError):
        py2vega('cell.undef', whitelist)

    assert py2vega('3 if value.member1 > value.member2 else 4', whitelist=[Variable('value', ['member1', 'member2'])]) == "((value.member1 > value.member2) ? 3 : 4)"

    # Nested member access
    whitelisted_vars = [Variable('nested_var', [Variable('var', ['test']), 'x'])]

    assert py2vega('nested_var.x', whitelisted_vars) == 'nested_var.x'

    with pytest.raises(NameError):
        py2vega('var.test', whitelisted_vars)

    assert py2vega('nested_var.var.test', whitelisted_vars) == 'nested_var.var.test'

    # Cannot validate a member access on an unknown variable
    with pytest.raises(Py2VegaSyntaxError):
        py2vega('nested_var[0].test', whitelisted_vars)


def func(value):
    return 'red' if value < 150 else 'green'


def test_function():
    assert py2vega(func, whitelist) == '((value < 150) ? \'red\' : \'green\')'


def test_whitelist():
    with pytest.raises(NameError):
        py2vega('my_variable')
    assert py2vega('my_variable', ['my_variable']) == 'my_variable'

    # Vega constants are accessible by default
    assert py2vega('PI') == 'PI'


def math_func():
    return isNaN(3)


def test_math():
    assert py2vega(math_func) == 'isNaN(3)'


def invalid_func1():
    print(3)


def test_invalid1():
    with pytest.raises(Py2VegaSyntaxError):
        py2vega(invalid_func1)


def invalid_func2():
    return 2
    return 3


def test_invalid2():
    with pytest.raises(Py2VegaSyntaxError, match='A `FunctionDef` node body cannot contain an `if` or `return` statement if it is not the last element of the body'):
        py2vega(invalid_func2)


def invalid_func3(value):
    if value < 3:
        return 3

    return 2


def test_invalid3():
    with pytest.raises(Py2VegaSyntaxError, match='A `FunctionDef` node body cannot contain an `if` or `return` statement if it is not the last element of the body'):
        py2vega(invalid_func3)


def invalid_func4(value):
    if value < 3:
        return 2
        return 1
    else:
        return 2


def test_invalid4():
    with pytest.raises(Py2VegaSyntaxError, match='A `If` node body cannot contain an `if` or `return` statement if it is not the last element of the body'):
        py2vega(invalid_func4)


def invalid_func5(value):
    if value < 3:
        return 3


def test_invalid5():
    with pytest.raises(Py2VegaSyntaxError, match='A `If` node body must contain at least one `if` statement or one `return` statement'):
        py2vega(invalid_func5)


def invalid_func6(value):
    del value
    return 3


def test_invalid6():
    with pytest.raises(Py2VegaSyntaxError):
        py2vega(invalid_func6)


def test_lambda():
    with pytest.raises(RuntimeError):
        py2vega(lambda value: value)


def conditional_func(value):
    if value < 3:
        return 'red'
    elif value < 5:
        return 'green'
    else:
        return 'yellow'


def test_if_stmt():
    assert py2vega(conditional_func, whitelist) == "if((value < 3), 'red', if((value < 5), 'green', 'yellow'))"


def assign_func1(value):
    val = ('USA', 'Japan')

    return 'red' if value in val else 'green'


def test_assign1():
    assert py2vega(assign_func1, whitelist) == "((indexof(['USA', 'Japan'], value) != -1) ? 'red' : 'green')"


def assign_func2(value):
    a = 'green'
    b = 'red'

    return a if value < 3 else b


def test_assign2():
    assert py2vega(assign_func2, whitelist) == "((value < 3) ? 'green' : 'red')"


def assign_func3(value):
    a = 'green'
    a = 'red'

    return a


def test_assign3():
    assert py2vega(assign_func3, whitelist) == "'red'"


def assign_func4(value):
    a = 'green'
    b = a

    return b


def test_assign4():
    assert py2vega(assign_func4, whitelist) == "'green'"


def assign_func5(value):
    a = b = 'Hello'

    return (a, b)


def test_assign5():
    assert py2vega(assign_func5, whitelist) == "['Hello', 'Hello']"


def assign_func6(value):
    a = 'Hello'
    b = a
    a = 'World'

    return b


def test_assign6():
    assert py2vega(assign_func6, whitelist) == "'Hello'"


def assign_func7(value):
    if value < 3:
        a = 3
        return a
    else:
        return a


def test_assign7():
    with pytest.raises(NameError):
        py2vega(assign_func7, whitelist)


def assign_func8(value):
    if value < 3:
        a = 3
        return a
    else:
        a = 8
        return a


def test_assign8():
    assert py2vega(assign_func8, whitelist) == "if((value < 3), 3, 8)"


def assign_func9(value):
    a = 38 if isNaN(value) else 32
    if value < 3:
        return a
    else:
        a = 8
        return a


def test_assign9():
    assert py2vega(assign_func9, whitelist) == "if((value < 3), (isNaN(value) ? 38 : 32), 8)"


def assign_func10(value):
    value[0] = 36
    return 3


def test_assign10():
    with pytest.raises(Py2VegaSyntaxError, match='Unsupported target'):
        assert py2vega(assign_func10, whitelist)
