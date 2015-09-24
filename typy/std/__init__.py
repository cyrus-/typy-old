"""typy standard library"""
import typy

class unit_(typy.Type):
    @classmethod
    def validate_idx(cls, idx):
        if idx != ():
            raise TypeFormationError("Index of unit type must be ().")

    # TODO: intro operator
unit = unit_[()]


