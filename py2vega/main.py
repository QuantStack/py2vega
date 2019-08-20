"""Python to VegaExpression transpiler."""

import ast
import inspect
import types

from .constants import constants
from .functions import vega_functions


def return_stmt(stmt, whitelist, scope):
    """Turn a Python return statement into a vega-expression."""
    return pystmt2vega(stmt.value, whitelist, scope)


def if_stmt(stmt, whitelist, scope):
    """Turn a Python if statement into a vega-expression."""
    def check_sanity(stmt_body):
        if len(stmt_body) > 1 and not isinstance(stmt_body[0], ast.Return) and not isinstance(stmt_body[0], ast.If):
            raise RuntimeError('Only a `return` or an `if` statement is allowed inside an `if` statement')

    check_sanity(stmt.body)
    check_sanity(stmt.orelse)

    return 'if({}, {}, {})'.format(
        pystmt2vega(stmt.test, whitelist, scope),
        pystmt2vega(stmt.body[0], whitelist, scope),
        pystmt2vega(stmt.orelse[0], whitelist, scope)
    )


def nameconstant_expr(expr, whitelist, scope):
    """Turn a Python nameconstant expression into a vega-expression."""
    if expr.value is False:
        return 'false'
    if expr.value is True:
        return 'true'
    if expr.value is None:
        return 'null'
    raise NameError('name \'{}\' is not defined, only a subset of Python is supported'.format(str(expr.value)))


def num_expr(expr, whitelist, scope):
    """Turn a Python num expression into a vega-expression."""
    return repr(expr.n)


def str_expr(expr, whitelist, scope):
    """Turn a Python str expression into a vega-expression."""
    return repr(expr.s)


def list_expr(expr, whitelist, scope):
    """Turn a Python list expression into a vega-expression."""
    return '[{}]'.format(', '.join(pystmt2vega(elt, whitelist, scope) for elt in expr.elts))


def dict_expr(expr, whitelist, scope):
    """Turn a Python dict expression into a vega-expression."""
    return '{{{}}}'.format(
        ', '.join([
            '{}: {}'.format(pystmt2vega(expr.keys[idx], whitelist, scope), pystmt2vega(expr.values[idx], whitelist, scope))
            for idx in range(len(expr.keys))
        ])
    )


def assign_expr(expr, whitelist, scope):
    """Turn a Python assignment expression into a vega-expression. And save the assigned variable in the current scope."""
    value = pystmt2vega(expr.value, whitelist, scope)

    for target in expr.targets:
        if not isinstance(target, ast.Name):
            raise RuntimeError('Unsupported target {} for the assignment'.format(str(target)))

        scope[target.id] = value

    # Assignment in Python returns None
    return 'null'


def unaryop_expr(expr, whitelist, scope):
    """Turn a Python unaryop expression into a vega-expression."""
    if isinstance(expr.op, ast.Not):
        return '!({})'.format(pystmt2vega(expr.operand, whitelist, scope))
    if isinstance(expr.op, ast.USub):
        return '-{}'.format(pystmt2vega(expr.operand, whitelist, scope))
    if isinstance(expr.op, ast.UAdd):
        return '+{}'.format(pystmt2vega(expr.operand, whitelist, scope))

    raise RuntimeError('Unsupported {} operator, only a subset of Python is supported'.format(str(expr.op)))


def boolop_expr(expr, whitelist, scope):
    """Turn a Python boolop expression into a vega-expression."""
    return '{} {} {}'.format(
        pystmt2vega(expr.values[0], whitelist, scope),
        '||' if isinstance(expr.op, ast.Or) else '&&',
        pystmt2vega(expr.values[1], whitelist, scope)
    )


def _binop_expr_impl(left_expr, op, right_expr, whitelist, scope):
    operator_mapping = {
        ast.Eq: '==', ast.NotEq: '!=',
        ast.Lt: '<', ast.LtE: '<=',
        ast.Gt: '>', ast.GtE: '>=',
        ast.Is: '===', ast.IsNot: '!==',
        ast.Add: '+', ast.Sub: '-',
        ast.Mult: '*', ast.Div: '/',
        ast.Mod: '%'
    }

    left = left_expr if isinstance(left_expr, str) else pystmt2vega(left_expr, whitelist, scope)
    right = pystmt2vega(right_expr, whitelist, scope)

    if isinstance(op, ast.In):
        return 'indexof({}, {}) != -1'.format(right, left)
    if isinstance(op, ast.NotIn):
        return 'indexof({}, {}) == -1'.format(right, left)
    if isinstance(op, ast.Pow):
        return 'pow({}, {})'.format(left, right)

    operator = operator_mapping.get(op.__class__)

    if operator is None:
        raise RuntimeError('Unsupported {} operator, only a subset of Python is supported'.format(repr(op)))

    return '{} {} {}'.format(left, operator, right)


def binop_expr(expr, whitelist, scope):
    """Turn a Python binop expression into a vega-expression."""
    return _binop_expr_impl(expr.left, expr.op, expr.right, whitelist, scope)


def if_expr(expr, whitelist, scope):
    """Turn a Python if expression into a vega-expression."""
    return '{} ? {} : {}'.format(
        pystmt2vega(expr.test, whitelist, scope),
        pystmt2vega(expr.body, whitelist, scope),
        pystmt2vega(expr.orelse, whitelist, scope)
    )


def compare_expr(expr, whitelist, scope):
    """Turn a Python compare expression into a vega-expression."""
    left_operand = expr.left

    for idx in range(len(expr.comparators)):
        left_operand = _binop_expr_impl(left_operand, expr.ops[idx], expr.comparators[idx], whitelist, scope)

    return left_operand


def name_expr(expr, whitelist, scope):
    """Turn a Python name expression into a vega-expression."""
    # If it's in the scope, return it's evaluated expression
    if expr.id in scope:
        return scope[expr.id]

    if expr.id in constants or expr.id in whitelist:
        return expr.id

    raise NameError('name \'{}\' is not defined, only a subset of Python is supported'.format(expr.id))


def call_expr(expr, whitelist, scope):
    """Turn a Python call expression into a vega-expression."""
    if isinstance(expr.func, ast.Name):
        func_name = expr.func.id

    if isinstance(expr.func, ast.Attribute):
        func_name = expr.func.attr

    if func_name in vega_functions:
        return '{}({})'.format(
            func_name,
            ', '.join([pystmt2vega(arg, whitelist, scope) for arg in expr.args])
        )

    raise NameError('name \'{}\' is not defined, only a subset of Python is supported'.format(func_name))


def attribute_expr(expr, whitelist, scope):
    """Turn a Python attribute expression into a vega-expression."""
    return expr.attr


stmt_mapping = {
    ast.Return: return_stmt,
    ast.If: if_stmt,
    ast.NameConstant: nameconstant_expr,
    ast.Num: num_expr,
    ast.Str: str_expr,
    ast.Tuple: list_expr,
    ast.List: list_expr,
    ast.Dict: dict_expr,
    ast.Assign: assign_expr,
    ast.UnaryOp: unaryop_expr,
    ast.BoolOp: boolop_expr,
    ast.BinOp: binop_expr,
    ast.IfExp: if_expr,
    ast.Compare: compare_expr,
    ast.Name: name_expr,
    ast.Call: call_expr,
    ast.Attribute: attribute_expr,
}


def pystmt2vega(stmt, whitelist=[], scope={}):
    """Turn a Python statement object into a Vega expression."""
    func = stmt_mapping.get(stmt.__class__)

    if func is None:
        raise RuntimeError('Unsupported {} statement'.format(repr(stmt)))

    return func(stmt, whitelist, scope)


def py2vega(value, whitelist=[]):
    """Convert Python code or Python function to a valid Vega expression."""
    if isinstance(value, str):
        parsed = ast.parse(value, '<string>', 'eval')

        return pystmt2vega(parsed.body, whitelist)

    if isinstance(value, (types.FunctionType, types.MethodType)):
        if getattr(value, '__name__', '') in ('', '<lambda>'):
            raise RuntimeError('Anonymous functions not supported')

        value = inspect.getsource(value)

        func = ast.parse(value, '<string>', 'exec').body[0]

        scope = {}
        for stmt in func.body[:-1]:
            pystmt2vega(stmt, whitelist, scope)
        return pystmt2vega(func.body[-1], whitelist, scope)

    raise RuntimeError('py2vega only supports code string or functions as input')
