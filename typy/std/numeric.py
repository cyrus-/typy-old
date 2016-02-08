"""typy numeric types that behave like the corresponding Python types"""
import ast 

import typy
import typy.util
import typy.util.astx as astx
import typy.std.boolean
import typy.fp

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

    def syn_Attribute(self, ctx, e):
        attr = e.attr
        if attr == 'f':
            return float
        elif attr == 'c':
            return complex
        else:
            raise typy.TypeError("Invalid attribute.", e)

    def translate_Attribute(self, ctx, e):
        value, attr = e.value, e.attr
        if attr == 'f':
            name = 'float'
        elif attr == 'c':
            name = 'complex'

        return ast.copy_location(
            astx.builtin_call(name, [ctx.translate(value)]),
            value)

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

    def syn_Attribute(self, ctx, e):
        if e.attr == 'c':
            return complex
        else:
            raise typy.TypeError("Invalid attribute.", e)

    def translate_Attribute(self, ctx, e):
        value = e.value
        return ast.copy_location(
            astx.builtin_call('complex', [ctx.translate(value)]),
            value)
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

    @classmethod
    def _process_Tuple(cls, ctx, e):
        elts = e.elts
        if len(elts) != 2:
            raise typy.TypeError(
                "Using a tuple to introduce a value of type complex requires two elements.",
                e)
        rl, im = elts[0], elts[1]

        if isinstance(rl, ast.Num):
            ctx.ana(rl, float)
        else:
            rl_ty = ctx.syn(rl)
            if rl_ty != int and rl_ty != float:
                raise typy.TypeError(
                    "Real component must be be integer or float.", rl)

        if not isinstance(im, ast.Num):
            im_ty = ctx.syn(im)
            if im_ty != int and im_ty != float:
                raise typy.TypeError(
                    "Imaginary component must be a complex literal, or an expressin of type 'int' or 'float'.",
                    im)

    def ana_Tuple(self, ctx, e):
        complex_._process_Tuple(ctx, e)

    @classmethod
    def syn_idx_Tuple(self, ctx, e, inc_idx):
        complex_._process_Tuple(ctx, e)
        return ()

    def translate_Tuple(self, ctx, e):
        elts = e.elts
        rl, im = elts[0], elts[1]

        rl_trans = ctx.translate(rl)

        if isinstance(im, ast.Num):
            n = im.n
            if isinstance(n, _pycomplex):
                n = n.imag
            im_trans = ast.copy_location(
                ast.Num(n), 
                im)
        else:
            im_trans = ctx.translate(im)

        # __builtin__.complex([[rl_trans]], [[im_trans]])
        return ast.copy_location(
            astx.builtin_call('complex', [rl_trans, im_trans]), 
        e)

    def syn_UnaryOp(self, ctx, e):
        if not isinstance(e.op, (ast.Not, ast.Invert)):
          return self
        else:
            raise typy.TypeError("Invalid unary operator for operand of type float.", e)

    def translate_UnaryOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.operand = ctx.translate(e.operand)
        return translation

    def syn_BinOp(self, ctx, e):
        if isinstance(e.op, (ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd)):
            raise typy.TypeError("Cannot use bitwise operators on floats.", e)
        if isinstance(e.op, ast.Mod):
            raise typy.TypeError("Cannot take the modulus of a complex number.", e)

        right = e.right
        ctx.ana(right, self)

        return self

    def translate_BinOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.right = ctx.translate(e.right)
        return translation

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                raise typy.TypeError("No ordering relation on complex numbers.", e)
            elif isinstance(op, (ast.In, ast.NotIn)):
                raise typy.TypeError("Type complex does not support this operator.", op)
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

    def syn_Attribute(self, ctx, e):
        attr = e.attr
        if attr == "real" or attr == "imag":
            return float
        elif attr == "conjugate":
            return typy.fp.fn[(), self]
        else:
            raise typy.TypeError("Invalid attribute: " + attr, e)

    def translate_Attribute(self, ctx, e):
        translation = astx.copy_node(e)
        translation.value = ctx.translate(e.value)
        return translation

complex = complex_[()]
