"""typy numeric types that behave like the corresponding Python types"""
import ast 

import typy
import typy.util
import typy.util.astx as astx
import typy.std.boolean

_pyint = int
_pylong = long
_pyfloat = float
_pycomplex = complex

class int_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of int_ type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx != () and inc_idx != Ellipsis:
            raise typy.TypeFormationError("Incomplete index of int_ type must be () or Ellipsis.")
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
        translation = astx.copy_node(e)
        translation.operand = ctx.translate(e.operand)
        return translation

    def syn_BinOp(self, ctx, e):
        op = e.op
        if isinstance(op, ast.Div):
            ctx.ana(e.right, float)
            return float
        else:
            ctx.ana(e.right, self)
            return self

    def translate_BinOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.right = ctx.translate(e.right)
        return translation

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if isinstance(op, (ast.In, ast.NotIn)):
                raise typy.TypeError("Type int does not support this operator.", op)
        for e_ in typy.util.tpl_cons(left, comparators):
            if hasattr(e_, 'match'): continue # already synthesized
            ctx.ana(e_, self)
        return typy.std.boolean.bool

    def translate_Compare(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.comparators = (
            ctx.translate(comparator)
            for comparator in e.comparators)
        return translation

int = int_[()]

class float_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of float_ type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx != () and inc_idx != Ellipsis:
            raise typy.TypeFormationError("Incomplete index of float_ type must be () or Ellipsis.")
        return inc_idx

    def ana_Num(self, ctx, e):
        if not isinstance(e.n, (_pyint, _pylong, _pyfloat)):
            raise typy.TypeError(
                "Complex literal cannot be used to introduce value of type 'float'.", e)

    @classmethod
    def syn_idx_Num(cls, ctx, e, inc_idx):
        if not isinstance(e.n, (_pyint, _pylong, _pyfloat)):
            raise typy.TypeError(
                "Complex literal cannot be used to introduce value of type 'float'.", e)
        return ()

    def translate_Num(self, ctx, e):
        translation = astx.copy_node(e)
        translation.n = _pyfloat(e.n)
        return translation

    def syn_UnaryOp(self, ctx, e):
        if not isinstance(e.op, ast.Not):
          return self
        else:
            raise typy.TypeError("Invalid unary operator 'not' for operand of type float.", e)

    def translate_UnaryOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.operand = ctx.translate(e.operand)
        return translation

    def syn_BinOp(self, ctx, e):
        ctx.ana(e.right, self)
        return self

    def translate_BinOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.right = ctx.translate(e.right)
        return translation

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if isinstance(op, (ast.In, ast.NotIn)):
                raise typy.TypeError("Type float does not support this operator.", op)
        for e_ in typy.util.tpl_cons(left, comparators):
            if hasattr(e_, 'match'): continue # already synthesized
            ctx.ana(e_, self)
        return typy.std.boolean.bool

    def translate_Compare(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.comparators = (
            ctx.translate(comparator)
            for comparator in e.comparators)
        return translation

float = float_[()]

# TODO: complex?
