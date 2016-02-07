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
        if isinstance(e.op, (ast.Not, ast.Invert)):
            raise typy.TypeError("Invalid unary operator for operand of type float.", e)
        else:
            return self
            
    def translate_UnaryOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.operand = ctx.translate(e.operand)
        return translation

    def syn_BinOp(self, ctx, e):
        if isinstance(e.op, (ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd)):
            raise typy.TypeError("Cannot use bitwise operators on floats.", e)
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

class complex_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of complex_ type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx != () and inc_idx != Ellipsis:
            raise typy.TypeFormationError("Incomplete index of complex_ type must be () or Ellipsis.")
        return inc_idx

    def ana_Num(self, ctx, e):
        # all number literals are valid
        return

    @classmethod
    def syn_idx_Num(cls, ctx, e, inc_idx):
        return ()

    def translate_Num(self, ctx, e):
        translation = astx.copy_node(e)
        n = e.n
        if isinstance(n, _pycomplex):
            translation.n = n
        else:
            translation.n = _pycomplex(e.n)
        return translation

    def ana_Tuple(self, ctx, e):
        elts = e.elts
        if len(elts) != 2:
            raise typy.TypeError(
                "Using a tuple to introduce a value of type complex requires providing two elements.",
                e)
        rl, im = elts[0], elts[1]

        if isinstance(rl, ast.Num):
            ctx.ana(rl, float)
        else:
            rl_ty = ctx.syn(rl)
            if rl_ty != int and rl_ty != float:
                raise typy.TypeError(
                    "Real component must be an integer or float.", rl)

        if not isinstance(im, ast.Num):
            im_ty = ctx.syn(im)
            if im_ty != int and im_ty != float:
                raise typy.TypeError(
                    "Imaginary component must be a complex literal, or an expressin of type 'int' or 'float'.",
                    im)

        return self

    def translate_Tuple(self, ctx, e):
        elts = e.elts
        rl, im = elts[0], elts[1]
        rl_trans = ctx.translate(rl)
        if isinstance(im, ast.Num):
            im_trans = ast.copy_location(
                ast.Num(_pycomplex(im.n)), 
                im)
        else:
            im_trans = ctx.translate(im)

        # __builtin__.complex([[rl_trans]], [[im_trans]])
        return ast.copy_location(ast.Call(
            func=ast.Attribute(
                value=ast.Name(
                    id='__builtin__', ctx=Load()), 
                attr='complex', ctx=Load()),
            args=[rl_trans, im_trans], 
            keywords=[], 
            starargs=None, 
            kwargs=None), 
        e)

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