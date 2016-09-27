"""typy standard library"""
import ast

from ..util import astx
from .. import component, Fragment, TypeValidationError

class unit(Fragment):
    @classmethod
    def init_idx(cls, idx_ast):
        if isinstance(idx_ast, ast.Tuple) and len(idx_ast.elts) == 0:
            return ()
        else:
            raise TypeValidationError(
                "unit type can only have trivial index.", idx_ast)

    @classmethod
    def ana_Tuple(cls, ctx, e, idx):
        if len(e.elts) != 0:
            raise TyError(
                "Tuple must be empty to be a unit value.", e)

    @classmethod
    def trans_Tuple(cls, ctx, e):
        return astx.copy_node(e)

    # TODO pattern matching
    # TODO get rid of this and combine with tpl

