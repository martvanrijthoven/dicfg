import ast
import operator as op

from dicfg.addons.addon import ModifierAddon

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
}


def safe_eval(expr):
    """
    Safely evaluate a math expression from a string.
    Only allows basic arithmetic operations.
    """

    def eval_node(node):
        if isinstance(node, ast.Constant):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            return operators[type(node.op)](eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
            return operators[type(node.op)](eval_node(node.operand))
        else:
            raise TypeError("Unsupported expression: {}".format(node))

    parsed = ast.parse(expr, mode="eval").body
    return eval_node(parsed)


class MathModifierError(Exception):
    pass


class MathModifier(ModifierAddon):
    NAME = "math"

    @classmethod
    def modify(cls, expression):
        try:
            result = safe_eval(expression)
            return result
        except Exception as e:
            raise MathModifierError(f"Error evaluating expression '{expression}': {e}")
