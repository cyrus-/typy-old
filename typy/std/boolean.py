"""Python booleans"""
import ast

import typy

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

    # TODO: case/if operators
bool = bool_[()]

