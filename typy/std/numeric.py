"""typy numeric types that behave like the corresponding Python types"""
import ast 

import typy
import typy.util.astx as astx

_pyint = int
_pylong = long
_pyfloat = float
_pycomplex = complex

class int_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of I type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx != () and inc_idx != Ellipsis:
            raise typy.TypeFormationError("Incomplete index of I type must be () or Ellipsis.")
        return inc_idx

    def ana_Num(self, ctx, e):
        n = e.n
        if isinstance(n, (_pyint, _pylong)):
            return
        else:
            raise typy.TypeError("Expression is not an int or long literal.", e)

    @classmethod
    def syn_idx_Num(cls, ctx, e, inc_idx):
        n = e.n
        if isinstance(n, (_pyint, _pylong)):
            return ()
        else:
            raise typy.TypeError("Expression is not an int or long literal.", e)

    def translate_Num(self, ctx, e):
        return astx.copy_node(e)

    def syn_UnaryOp(self, ctx, e):
        if not isinstance(e.op, ast.Not):
          return self
        else:
            raise typy.TypeError("Invalid unary operator 'not' for operand of type int.", e)

    def translate_UnaryOp(self, ctx, e):
        return astx.copy_node(e)

    def syn_BinOp(self, ctx, e):
        op = e.op
        if isinstance(op, ast.Div):
            raise typy.TypeError("Cannot divide integers. Use // or convert to float.", e)
        ctx.ana(e.right, self)
        return self

    def translate_BinOp(self, ctx, e):
        return astx.copy_node(e)


    # TODO: binary operators
    # TODO: comparators

int = int_[()]

# TODO: long?
# TODO: float?
# TODO: complex?
