"""Python booleans"""
import typy

class pybool_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of boolean type must be ().")
        return idx

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

    def translate_Name_constructor(self, ctx, e):
        return astx.copy_node(e)

    # TODO: case/if operators
pybool = pybool_[()]

