"""typy string types"""
import ast 

import typy
import typy.util
import typy.util.astx as astx
import typy.std.boolean
import typy.fp

class str_(typy.Type):
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

    def ana_Str(self, ctx, e):
        return # all string literals are ok

    @classmethod
    def syn_idx_Str(cls, ctx, e, inc_idx):
        return ()

    def translate_Str(self, ctx, e):
        return astx.copy_node(e)

    def syn_BinOp(self, ctx, e):
        op = e.op
        if isinstance(op, ast.Add):
            e.ana(e.right, self)
            return self
        else:
            raise typy.TypeError("Invalid binary operator on strings.", e)

    def translate_BinOp(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.right = ctx.translate(e.right)
        return translation

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if not isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot, ast.In, ast.NotIn)):
                raise typy.TypeError("Invalid comparison operator on strings.", e)
        for e_ in typy.util.tpl_cons(left, comparators):
            if hasattr(e_, 'match'): continue # already synthesized
            ctx.ana(e_, self)
        return typy.std.boolean.bool

    def translate_Compare(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.comparators = tuple(
            ctx.translate(comparators)
            for comparator in comparators)
        return translation

    def syn_Subscript(self, ctx, e):
        slice_ = e.slice 
        if isinstance(slice_, ast.Ellipsis):
            raise typy.TypeError("String slice cannot be an Ellipsis.", e)
        elif isinstance(slice_, ast.ExtSlice):
            raise typy.TypeError("String slice can only have one dimension.", e)
        elif isinstance(slice_, ast.Index):
            ctx.ana(slice_.value, int)
        else: #if isinstance(slice_, ast.Slice):
            lower, upper, step = slice_.lower, slice_.upper, slice_.step
            if lower is not None:
                ctx.ana(lower, int)
            if upper is not None:
                ctx.ana(upper, int)
            if step is not None:
                ctx.ana(step, int)
        return self

    def translate_Subscript(self, ctx, e):
        translation = astx.copy_node(e)
        translation.value = ctx.translate(e.value)
        slice_ = e.slice
        slice_translation = astx.copy_node(slice_)
        if isinstance(slice_, ast.Index):
            slice_translation.value = ctx.translate(slice_.value)
        else:
            lower, upper, step = slice_.lower, slice_.upper, slice_.step
            slice_translation.lower = ctx.translate(lower) if lower is not None else None
            slice_translation.upper = ctx.translate(upper) if upper is not None else None
            slice_translation.step = ctx.translate(step) if step is not None else None
        translation.slice = slice_translation
        return translation 

str = str_[()]
