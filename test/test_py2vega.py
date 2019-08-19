import pytest

from py2vega import py2vega, math

whitelist = ['value', 'x', 'y', 'height', 'width', 'row', 'column']


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
    assert py2vega(code, whitelist) == 'value || 3'

    code = 'value and 3'
    assert py2vega(code, whitelist) == 'value && 3'

    code = 'value + 3'
    assert py2vega(code, whitelist) == 'value + 3'

    code = 'value**3'
    assert py2vega(code, whitelist) == 'pow(value, 3)'


def test_ternary():
    code = '3 if value else 4'
    assert py2vega(code, whitelist) == 'value ? 3 : 4'


def test_compare():
    code = '3 < value <= 4'
    assert py2vega(code, whitelist) == '3 < value <= 4'

    code = 'value in (\'ford\', \'chevrolet\')'
    assert py2vega(code, whitelist) == 'indexof([\'ford\', \'chevrolet\'], value) != -1'

    code = '\'chevrolet\' in value'
    assert py2vega(code, whitelist) == 'indexof(value, \'chevrolet\') != -1'

    code = '\'chevrolet\' not in value'
    assert py2vega(code, whitelist) == 'indexof(value, \'chevrolet\') == -1'


def foo(value):
    return 'red' if value < 150 else 'green'


def test_function():
    assert py2vega(foo, whitelist) == 'value < 150 ? \'red\' : \'green\''


def test_whitelist():
    with pytest.raises(NameError):
        py2vega('my_variable')
    assert py2vega('my_variable', ['my_variable']) == 'my_variable'

    # Vega constants are accessible by default
    assert py2vega('PI') == 'PI'


def bar():
    return math.isNaN(3)


def test_math():
    assert py2vega(bar) == 'isNaN(3)'


def invalid_func1():
    print(3)


def invalid_func2():
    f = 3


def invalid_func3(value):
    value < 3
    return 3 < value <= 4


def test_invalid1():
    with pytest.raises(RuntimeError):
        py2vega(invalid_func1)


def test_invalid2():
    with pytest.raises(RuntimeError):
        assert py2vega(invalid_func2)


def test_invalid3():
    with pytest.raises(RuntimeError):
        py2vega(invalid_func3)


def test_invalid4():
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
    assert py2vega(conditional_func, whitelist) == "if(value < 3, 'red', if(value < 5, 'green', 'yellow'))"
