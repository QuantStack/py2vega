"""Python to VegaExpression transpiler."""

import ast
import inspect
import types

from .constants import constants
from .functions import vega_functions


operator_mapping = {
    ast.Eq: '==', ast.NotEq: '!=',
    ast.Lt: '<', ast.LtE: '<=',
    ast.Gt: '>', ast.GtE: '>=',
    ast.Is: '===', ast.IsNot: '!==',
    ast.Add: '+', ast.Sub: '-',
    ast.Mult: '*', ast.Div: '/',
    ast.Mod: '%'
}


def check_validity(nodes, origin_node):
    """Check whether or not a list of nodes is valid.

    A list of nodes is considered valid when:
    - it is not empty
    - the last node is an `if` statement or a `return` statement
    - everything but the last element is not an `if` statement or a `return` statement
    """
    if len(nodes) == 0:
        raise RuntimeError(
            'A `{}` node body must contain at least one `if` statement or one `return` statement'.format(
                origin_node.__class__.__name__))
    for node in nodes[:-1]:
        if isinstance(node, ast.If) or isinstance(node, ast.Return):
            raise RuntimeError(
                'A `{}` node body cannot contain an `if` or `return` statement if it is not the last element of the body'.format(
                    origin_node.__class__.__name__))
    if not isinstance(nodes[-1], ast.If) and not isinstance(nodes[-1], ast.Return):
        raise RuntimeError(
            'The last element of a `{}` node body must be an `if` or `return` statement'.format(origin_node.__class__.__name__))


class VegaExpressionVisitor(ast.NodeVisitor):
    """Visitor that turns a Node into a Vega expression."""

    def __init__(self, whitelist, scope={}):
        self.whitelist = whitelist
        self.scope = scope

    def generic_visit(self, node):
        """Throwing an error by default."""
        raise RuntimeError('Unsupported {} node, only a subset of Python is supported'.format(node.__class__.__name__))

    def visit_Return(self, node):
        """Turn a Python return statement into a Vega-expression."""
        return self.visit(node.value)

    def visit_If(self, node):
        """Turn a Python if statement into a Vega-expression."""
        # Visiting body
        body_scope = self.scope.copy()
        check_validity(node.body, node)
        for stmt in node.body[:-1]:
            VegaExpressionVisitor(self.whitelist, body_scope).visit(stmt)

        # Visiting orelse
        orelse_scope = self.scope.copy()
        check_validity(node.orelse, node)
        for stmt in node.orelse[:-1]:
            VegaExpressionVisitor(self.whitelist, orelse_scope).visit(stmt)

        return 'if({}, {}, {})'.format(
            self.visit(node.test),
            VegaExpressionVisitor(self.whitelist, body_scope).visit(node.body[-1]),
            VegaExpressionVisitor(self.whitelist, orelse_scope).visit(node.orelse[-1])
        )

    def visit_NameConstant(self, node):
        """Turn a Python nameconstant expression into a Vega-expression."""
        if node.value is False:
            return 'false'
        if node.value is True:
            return 'true'
        if node.value is None:
            return 'null'
        raise NameError('name \'{}\' is not defined, only a subset of Python is supported'.format(str(node.value)))

    def visit_Num(self, node):
        """Turn a Python num expression into a Vega-expression."""
        return repr(node.n)

    def visit_Str(self, node):
        """Turn a Python str expression into a Vega-expression."""
        return repr(node.s)

    def _visit_list_impl(self, node):
        """Turn a Python list expression into a Vega-expression."""
        return '[{}]'.format(', '.join(self.visit(elt) for elt in node.elts))

    def visit_Tuple(self, node):
        """Turn a Python tuple expression into a Vega-expression."""
        return self._visit_list_impl(node)

    def visit_List(self, node):
        """Turn a Python list expression into a Vega-expression."""
        return self._visit_list_impl(node)

    def visit_Dict(self, node):
        """Turn a Python dict expression into a Vega-expression."""
        return '{{{}}}'.format(
            ', '.join([
                '{}: {}'.format(self.visit(node.keys[idx]), self.visit(node.values[idx]))
                for idx in range(len(node.keys))
            ])
        )

    def visit_Assign(self, node):
        """Turn a Python assignment expression into a Vega-expression. And save the assigned variable in the current scope."""
        value = self.visit(node.value)

        for target in node.targets:
            if not isinstance(target, ast.Name):
                raise RuntimeError('Unsupported target {} for the assignment'.format(target.__class__.__name__))

            self.scope[target.id] = value

        # Assignment in Python returns None
        return 'null'

    def visit_UnaryOp(self, node):
        """Turn a Python unaryop expression into a Vega-expression."""
        if isinstance(node.op, ast.Not):
            return '!({})'.format(self.visit(node.operand))
        if isinstance(node.op, ast.USub):
            return '-{}'.format(self.visit(node.operand))
        if isinstance(node.op, ast.UAdd):
            return '+{}'.format(self.visit(node.operand))

        raise RuntimeError('Unsupported {} operator, only a subset of Python is supported'.format(node.op.__class__.__name__))

    def visit_BoolOp(self, node):
        """Turn a Python boolop expression into a Vega-expression."""
        return '{} {} {}'.format(
            self.visit(node.values[0]),
            '||' if isinstance(node.op, ast.Or) else '&&',
            self.visit(node.values[1])
        )

    def _visit_binop_impl(self, left_node, op, right_node):
        left = left_node if isinstance(left_node, str) else self.visit(left_node)
        right = self.visit(right_node)

        if isinstance(op, ast.In):
            return 'indexof({}, {}) != -1'.format(right, left)
        if isinstance(op, ast.NotIn):
            return 'indexof({}, {}) == -1'.format(right, left)
        if isinstance(op, ast.Pow):
            return 'pow({}, {})'.format(left, right)

        operator = operator_mapping.get(op.__class__)

        if operator is None:
            raise RuntimeError('Unsupported {} operator, only a subset of Python is supported'.format(op.__class__.__name__))

        return '{} {} {}'.format(left, operator, right)

    def visit_BinOp(self, node):
        """Turn a Python binop expression into a Vega-expression."""
        return self._visit_binop_impl(node.left, node.op, node.right)

    def visit_IfExp(self, node):
        """Turn a Python if expression into a Vega-expression."""
        return '{} ? {} : {}'.format(
            self.visit(node.test),
            self.visit(node.body),
            self.visit(node.orelse)
        )

    def visit_Compare(self, node):
        """Turn a Python compare expression into a Vega-expression."""
        left_operand = node.left

        for idx in range(len(node.comparators)):
            left_operand = self._visit_binop_impl(left_operand, node.ops[idx], node.comparators[idx])

        return left_operand

    def visit_Name(self, node):
        """Turn a Python name expression into a Vega-expression."""
        # If it's in the scope, return it's evaluated expression
        if node.id in self.scope:
            return self.scope[node.id]

        if node.id in constants or node.id in self.whitelist:
            return node.id

        raise NameError('name \'{}\' is not defined, only a subset of Python is supported'.format(node.id))

    def visit_Call(self, node):
        """Turn a Python call expression into a Vega-expression."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in vega_functions:
            return '{}({})'.format(
                func_name,
                ', '.join([self.visit(arg) for arg in node.args])
            )

        raise NameError('name \'{}\' is not defined, only a subset of Python is supported'.format(func_name))

    def visit_Attribute(self, node):
        """Turn a Python attribute expression into a Vega-expression."""
        return node.attr


def visit_nodes(nodes, whitelist):
    """Visit a list of nodes, and return the equivalent Vega expression."""
    scope = {}
    check_validity(nodes, )
    for node in nodes[:-1]:
        VegaExpressionVisitor(whitelist, scope).visit(node)
    return VegaExpressionVisitor(whitelist, scope).visit(nodes[-1])


def py2vega(value, whitelist=[]):
    """Convert Python code or Python function to a valid Vega expression."""
    if isinstance(value, str):
        parsed = ast.parse(value, '<string>', 'eval')

        return VegaExpressionVisitor(whitelist).visit(parsed.body)

    if isinstance(value, (types.FunctionType, types.MethodType)):
        if getattr(value, '__name__', '') in ('', '<lambda>'):
            raise RuntimeError('Anonymous functions not supported')

        value = inspect.getsource(value)

        func = ast.parse(value, '<string>', 'exec').body[0]

        scope = {}
        check_validity(func.body, func)
        for node in func.body[:-1]:
            VegaExpressionVisitor(whitelist, scope).visit(node)
        return VegaExpressionVisitor(whitelist, scope).visit(func.body[-1])

    raise RuntimeError('py2vega only supports a code string or function as input')
