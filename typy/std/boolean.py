"""Python booleans"""
import ast

import typy
import typy.util.astx as astx

class bool_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of boolean type must be ().")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
    	if inc_idx != () and inc_idx != Ellipsis:
    		raise typy.TypeFormationError("Incomplete index of boolean type must be () or Ellipsis.")
    	return inc_idx

    def ana_Name_constructor(self, ctx, e):
        id = e.id
        if id != "True" and id != "False":
            raise typy.TypeError(
                "Must introduce a value of boolean type with either True or False.",
                e)

    @classmethod
    def syn_idx_Name_constructor(cls, ctx, e, inc_idx):
        id = e.id
        if id != "True" and id != "False":
            raise typy.TypeError(
                "Must introduce a value of boolean type with either True or False.",
                e)
        return ()

    def translate_Name_constructor(self, ctx, e):
        return astx.copy_node(e)

    def syn_UnaryOp(self, ctx, e):
        if isinstance(e.op, ast.Not):
            return self
        else:
            raise typy.TypeError(
                """Type bool does not support this unary operator.""",
                e)

    def translate_UnaryOp(self, ctx, e):
        return astx.copy_node(e)

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if not isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
                raise typy.TypeError("Type bool does not support this operator.", op)
        for e_ in typy.util.tpl_cons(left, comparators):
            if hasattr(e_, 'match'): continue # already synthesized
            ctx.ana(e_, self)
        return self

    def translate_Compare(self, ctx, e):
        return astx.copy_node(e)

    def syn_BoolOp(self, ctx, e):
        values = e.values
        for value in values:
            ctx.ana(value, self)
        return self

    def translate_BoolOp(self, ctx, e):
        return astx.copy_node(e)

    # TODO: case/if operators
bool = bool_[()]

