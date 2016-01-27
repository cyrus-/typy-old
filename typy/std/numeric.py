"""typy numeric types that behave like the corresponding Python types"""
import typy
import typy.util.astx as astx

class I_(typy.Type):
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
        if isinstance(n, (int, long)):
            return
        else:
            raise typy.TypeError("Expression is not an int or long literal.", e)

    @classmethod
    def syn_idx_Num(cls, ctx, e, inc_idx):
        n = e.n
        if isinstance(n, (int, long)):
            return ()
        else:
            raise typy.TypeError("Expression is not an int or long literal.", e)

    def translate_Num(self, ctx, e):
        return astx.copy_node(e)

    # TODO: unary operators
    # TODO: binary operators

I = I_[()]

# TODO: long?
# TODO: float?
# TODO: complex?
