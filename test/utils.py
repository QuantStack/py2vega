"""Utils module for testing."""

import subprocess


def evaluate_js(expr, scope={}):
    """Evaluate a JavaScript expression and return the result.

    This is used for evaluating the py2vega output. It does not ensure that the vega expression
    is correct, but it allows to test if the expression is at least a valid JavaScript expression.
    """
    scoped_expr = expr
    for key, value in scope.items():
        scoped_expr = scoped_expr.replace(key, str(value))

    result = subprocess.run(['node', '--eval', 'console.log({})'.format(scoped_expr)], stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")[:-1]
