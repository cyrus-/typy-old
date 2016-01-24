"""typy numeric types that behave like the corresponding Python types"""
import typy

class pyint_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of int type must be ().")

    # TODO: number literals
    # TODO: unary operators
    # TODO: binary operators

pyint = pyint_[()]

# TODO: long
# TODO: float
# TODO: complex

