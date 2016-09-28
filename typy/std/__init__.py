"""typy standard library"""
import ast

from ..util import astx
from .. import component, Fragment, TypeValidationError

def _check_trivial_idx_ast(idx_ast):
    if isinstance(idx_ast, ast.Tuple) and len(idx_ast.elts) == 0:
        return ()
    else:
        raise TypeValidationError(
            "unit type can only have trivial index.", idx_ast)

class unit(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)

    @classmethod
    def ana_Tuple(cls, ctx, e, idx):
        if len(e.elts) != 0:
            raise TyError(
                "Tuple must be empty to be a unit value.", e)

    @classmethod
    def trans_Tuple(cls, ctx, e, idx):
        return astx.copy_node(e)

    # TODO pattern matching
    # TODO get rid of this and combine with tpl

class record(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        if isinstance(idx_ast, ast.Slice):
            # Python special cases single slices
            # we don't want that
            idx_ast = ast.ExtSlice(dims=[idx_ast])
        
        if isinstance(idx_ast, ast.ExtSlice):
            idx_value = dict() # returned below
            for dim in idx_ast.dims:
                if (isinstance(dim, ast.Slice) and 
                        dim.step is None and
                        dim.upper is not None and 
                        isinstance(dim.lower, ast.Name)):
                    lbl = dim.lower.id
                    if lbl in idx_value:
                        raise typy.TypeValidationError(
                            "Duplicate label.", dim)
                    ty = ctx.as_type(dim.upper)
                    idx_value[lbl] = ty
                else:
                    raise typy.TypeValidationError(
                        "Invalid field specification.", dim)
            return idx_value
        else:
            raise typy.TypeValidationError(
                "Invalid record specification.", idx_ast)

    @classmethod
    def ana_Dict(cls, ctx, e, idx):
        for lbl, value in zip(e.keys, e.values):
            if isinstance(lbl, ast.Name):
                id = lbl.id
                if id in idx: ctx.ana(value, idx[id])
                else:
                    raise TyError("Invalid label: " + id, lbl)
            else:
                raise TyError("Label is not a name.", lbl)
        
        if len(idx) != len(e.keys):
            raise TyError("Labels do not match those in type.", e)

    @classmethod
    def trans_Dict(cls, ctx, e, idx):
        ast_dict = dict((k.id, v)
                        for k, v in zip(e.keys, e.values))
        return ast.Tuple(
            elts=list(
                ctx.trans(ast_dict[lbl]) # TODO fix typo in paper
                for lbl in sorted(idx.keys())
            ),
            lineno=e.lineno, col_offset=e.col_offset, ctx=astx.load_ctx)

    # TODO syn_Attribute
    # TODO trans_Attribute
    # TODO pattern matching
    pass

class tpl(Fragment):
    # TODO init_idx
    # TODO ana_Tuple
    # TODO ana_Dict
    # TODO syn_Attribute
    # TODO trans_Attribute
    # TODO syn_Subscript
    # TODO trans_Subscript
    # TODO pattern matching
    pass

class string(Fragment):
    @classmethod
    def init_idx(self, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)

    @classmethod
    def ana_Str(cls, ctx, e, idx):
        return

    @classmethod
    def trans_Str(cls, ctx, e, idx):
        return astx.copy_node(e)

    # TODO decide which other operations are exposed
    # TODO pattern matching
    pass

class num(Fragment):
    # TODO init_idx
    # TODO intro forms
    # TODO other operations
    # TODO pattern matching
    pass

class ieee(Fragment):
    # TODO init_idx
    # TODO intro forms
    # TODO other operations
    # TODO pattern matching
    pass

class cplx(Fragment):
    # TODO init_idx
    # TODO intro_forms
    # TODO other operations
    # TODO pattern matching
    pass

class finsum(Fragment):
    # TODO init_idx
    # TODO intro forms
    # TODO other operations
    # TODO pattern matching
    pass

class fn(Fragment):
    # TODO init_idx
    # TODO intro forms
    # TODO call
    pass

class py(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)
    
    @classmethod
    def ana_Dict(cls, ctx, e, idx):
        return

    @classmethod
    def trans_Dict(cls, ctx, e, idx):
        # TODO: deep copy
        return astx.copy_node(e)

    # TODO intro forms
    # TODO other operations
    # TODO pattern matching
    pass

# Maybe not in the standard library?
# TODO proto
# TODO string_in
# TODO array
# TODO numpy stuff
# TODO cl stuff

