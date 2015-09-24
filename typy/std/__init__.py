"""typy standard library"""
import typy

class unit_(typy.Type):
    @classmethod
    def validate_idx(cls, idx):
        if idx != ():
            raise TypeFormationError("Index of unit type must be ().")

    # TODO: intro operator
unit = unit_[()]

class fn(typy.Type):
    @classmethod
    def validate_idx(cls, idx):
        # TODO: validate idx
        pass

    @classmethod
    def validate_inc_idx(cls, inc_idx):
        # TODO: validate inc indx
        pass

    # TODO: rest of the methods

# TODO: tuples and ltuples
# TODO: casetypes
# TODO: string
# TODO: number
