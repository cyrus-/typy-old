"""typy standard library"""
import ast
from collections import OrderedDict

from .. import util as _util 
from ..util import astx
from .._components import component
from .._fragments import Fragment
from .._ty_exprs import CanonicalTy
from .._errors import TypeValidationError, TyError

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

    @classmethod
    def ana_pat_Tuple(cls, ctx, pat, idx):
        if len(pat.elts) != 0:
            raise TyError(
                "Tuple pattern must be empty to match unit values.", pat)
        return { }

    @classmethod
    def trans_pat_Tuple(cls, ctx, pat, idx, scrutinee_trans):
        return (ast.copy_location(
            ast.NameConstant(value=True), pat), { })

    @classmethod
    def syn_Compare(cls, ctx, e):
        unit_ty = CanonicalTy(unit, ())
        ctx.ana(e.left, unit_ty)
        for op, comparator in zip(e.ops, e.comparators):
            if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn)):
                raise TyError("Invalid comparison operator on unit.", comparator)
            ctx.ana(comparator, unit_ty)
        return CanonicalTy(boolean, ())
    
    @classmethod
    def trans_Compare(cls, ctx, e):
        left_tr = ctx.trans(e.left)
        comp_trs = [ ]
        for comparator in e.comparators:
            comp_trs.append(ctx.trans(comparator))
        return ast.copy_location(
            ast.Compare(
                left = left_tr,
                ops = e.ops,
                comparators = comp_trs), e)

class boolean(Fragment):
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        return _check_trivial_idx_ast(idx_ast)

    @classmethod
    def ana_NameConstant(cls, ctx, e, idx):
        value = e.value
        if value is True or value is False:
            return
        else:
            raise TyError("Invalid name constant: " + str(value), e)

    @classmethod
    def trans_NameConstant(cls, ctx, e, idx):
        return ast.copy_location(
            ast.NameConstant(value=e.value), e)

    @classmethod
    def ana_pat_NameConstant(cls, ctx, pat, idx):
        value = pat.value
        if value is True or value is False:
            return {}
        else:
            raise TyError("Invalid name constant: " + str(value), pat)

    @classmethod
    def trans_pat_NameConstant(cls, ctx, pat, idx, scrutinee_trans):
        if pat.value:
            condition = scrutinee_trans
        else:
            condition = ast.fix_missing_locations(ast.copy_location(
                ast.UnaryOp(
                    op = ast.Not(),
                    operand=scrutinee_trans), pat))
        return condition, {}

    @classmethod
    def syn_BoolOp(cls, ctx, e):
        bool_ty = CanonicalTy(boolean, ())
        for value in e.values:
            ctx.ana(value, bool_ty)
        return bool_ty

    @classmethod
    def ana_BoolOp(cls, ctx, e, idx):
        bool_ty = CanonicalTy(boolean, ())
        for value in e.values:
            ctx.ana(value, bool_ty)

    @classmethod
    def trans_BoolOp(cls, ctx, e):
        values_tr = [ ]
        for value in e.values:
            values_tr.append(ctx.trans(value))
        return ast.copy_location(
            ast.BoolOp(
                op = e.op,
                values = values_tr), e)

    @classmethod
    def syn_Compare(cls, ctx, e):
        bool_ty = CanonicalTy(boolean, ())
        ctx.ana(e.left, bool_ty)
        for op, comparator in zip(e.ops, e.comparators):
            if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn)):
                raise TyError("Invalid comparison operator on unit.", comparator)
            ctx.ana(comparator, bool_ty)
        return bool_ty

    @classmethod
    def trans_Compare(cls, ctx, e):
        left_tr = ctx.trans(e.left)
        comp_trs = [ ]
        for comparator in e.comparators:
            comp_trs.append(ctx.trans(comparator))
        return ast.copy_location(
            ast.Compare(
                left = left_tr,
                ops = e.ops,
                comparators = comp_trs), e)

    @classmethod
    def syn_If(cls, ctx, e, idx):
        body_ty = ctx.syn_block(e.body)
        orelse_ty = ctx.ana_block(e.orelse, body_ty)
        return body_ty
    
    @classmethod
    def ana_If(cls, ctx, e, idx, ty):
        ctx.ana_block(e.body, ty)
        ctx.ana_block(e.orelse, ty)

    @classmethod
    def trans_If(cls, ctx, e, idx):
        return [ast.copy_location(
            ast.If(
                test=ctx.trans(e.test),
                body=ctx.trans_block(e.body),
                orelse=ctx.trans_block(e.orelse)), e)]

    @classmethod
    def syn_IfExp(cls, ctx, e, idx):
        body_ty = ctx.syn(e.body)
        orelse_ty = ctx.ana(e.orelse, body_ty)
        return body_ty

    @classmethod
    def ana_IfExp(cls, ctx, e, idx, ty):
        ctx.ana(e.body, ty)
        ctx.ana(e.orelse, ty)

    @classmethod
    def trans_IfExp(cls, ctx, e, idx):
        return ast.copy_location(
            ast.IfExp(
                test=ctx.trans(e.test),
                body=ctx.trans(e.body),
                orelse=ctx.trans(e.orelse)), e)

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
    
    # TODO idx_eq

    @classmethod
    def ana_Dict(cls, ctx, e, idx):
        for lbl, value in zip(e.keys, e.values):
            if isinstance(lbl, ast.Name):
                id = lbl.id
                if id in idx: ctx.ana(value, idx[id])
                else:
                    raise TyError("Invalid label: " + id, lbl)
            else:
                raise TyError("Label is not an identifier.", lbl)
        
        if len(idx) != len(e.keys):
            raise TyError("Labels do not match those in type.", e)

    @classmethod
    def trans_Dict(cls, ctx, e, idx):
        ast_dict = dict((k.id, v)
                        for k, v in zip(e.keys, e.values))
        return ast.copy_location(ast.Tuple(
            elts=list(
                ctx.trans(ast_dict[lbl])
                for lbl in sorted(idx.keys())
            ), ctx=ast.Load()), 
            e)

    @classmethod
    def syn_Attribute(cls, ctx, e, idx):
        try:
            return idx[e.attr]
        except KeyError:
            raise TyError("Invalid field label: " + e.attr, e)

    @classmethod
    def trans_Attribute(cls, ctx, e, idx):
        pos = _util._seq_pos_of(e.attr, sorted(idx.keys()))
        return ast.fix_missing_locations(ast.copy_location(
            ast.Subscript(
                value=ctx.trans(e.value),
                slice=ast.Index(ast.Num(n=pos)),
                ctx=e.ctx),
            e))

    # TODO pattern matching

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

    @classmethod
    def syn_BinOp(cls, ctx, e):
        left, op, right = e.left, e.op, e.right
        string_ty = CanonicalTy(cls, ())
        if isinstance(op, ast.Add):
            ctx.ana(left, string_ty)
            ctx.ana(right, string_ty)
            return string_ty
        else:
            raise TyError("Invalid string operator.", e)
        # TODO decide which other operations are exposed

    @classmethod
    def trans_BinOp(cls, ctx, e):
        return ast.copy_location(
            ast.BinOp(
                left=ctx.trans(e.left),
                op=e.op,
                right=ctx.trans(e.right)),
        e)

    # TODO pattern matching

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
    @classmethod
    def init_idx(cls, ctx, idx_ast):
        # TODO init_idx
        raise NotImplementedError()

    @classmethod
    def syn_FunctionDef(cls, ctx, stmt):
        # process decorators
        decorator_list = stmt.decorator_list
        if len(decorator_list) > 1:
            raise TyError(
                "fn does not support additional decorators.",
                decorator_list[1])

        # process args
        arguments = stmt.args
        if arguments.vararg is not None:
            raise TyError(
                "fn does not support varargs", arguments)
        if len(arguments.kwonlyargs) > 0:
            raise TyError(
                "fn does not support kw only args", arguments)
        if arguments.kwarg is not None:
            raise TyError(
                "fn does not support kw arg", arguments)
        if len(arguments.defaults) > 0:
            raise TyError(
                "fn does not support defaults", arguments)
        args = arguments.args
        def _process_args():
            for arg in args:
                arg_id = arg.arg
                arg_ann = arg.annotation
                if arg_ann is None:
                    raise TyError(
                        "Missing argument type on " + arg_id,
                        arg)
                arg_ty = ctx.as_type(arg_ann)
                # simulate a name for the error reporting system
                name = ast.Name(id=arg_id, 
                                lineno=arg.lineno, 
                                col_offset=arg.col_offset)
                yield (name, arg_ty)
        arg_sig = stmt.arg_sig = OrderedDict(_process_args())

        # TODO process return type annotation
        
        # push bindings
        stmt.uniq_arg_sig = ctx.push_var_bindings(dict(arg_sig))

        # TODO recursive functions

        # process docstring
        body = stmt.body
        if (len(body) > 0 
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Str)):
            proper_body = stmt.proper_body = body[1:]
            docstring = stmt.docstring = body[0].value.s
        else:
            proper_body = stmt.proper_body = body
            docstring = stmt.docstring = None

        # make sure there is at least one remaining statement
        if len(proper_body) == 0:
            raise TyError(
                "Must be at least one statement, "
                "other than the docstring, in the body.",
                stmt)

        # check statements in proper_body
        for stmt in proper_body:
            ctx.check(stmt)

        # synthesize return type from last statement
        last_stmt = proper_body[-1]
        if isinstance(last_stmt, ast.Expr):
            rty = last_stmt.value.ty
        else:
            raise TyError(
                "Last statement must be an expression.", 
                last_stmt)
        
        # bindings
        ctx.pop_var_bindings()

        # return canonical type
        return CanonicalTy(fn, (arg_sig, rty))

    # TODO ana_FunctionDef

    @classmethod
    def trans_FunctionDef(cls, ctx, stmt, id):
        # translate arguments
        arguments_tr = ast.arguments(
            args= [
                ast.arg(
                    arg=stmt.uniq_arg_sig[arg.arg][0],
                    annotation=None,
                    lineno=arg.lineno,
                    col_offset=arg.col_offset)
                for arg in stmt.args.args
            ],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[])

        # translate body
        body_tr = [
            ctx.trans(stmt)
            for stmt in stmt.proper_body
        ]

        # translate return
        last_stmt = body_tr[-1]
        body_tr[-1] = ast.copy_location(
            ast.Return(value=last_stmt.value), 
            last_stmt)

        return [ast.copy_location(
            ast.FunctionDef(
                name=id,
                args=arguments_tr,
                body=body_tr,
                decorator_list=[],
                returns=None), 
            stmt)]

    # TODO lambdas

    @classmethod
    def syn_Call(cls, ctx, e, idx):
        if len(e.keywords) != 0:
            raise TyError("fn does not support keyword arguments.", e)

        # check args
        args = e.args
        arg_sig, rty = idx
        n_args = len(args)
        n_args_reqd = len(arg_sig)
        if n_args < n_args_reqd:
            raise TyError("Too few arguments provided.", e)
        elif n_args > n_args_reqd:
            raise TyError("Too many arguments provided.", e)
        for arg, arg_ty in zip(args, arg_sig.values()):
            ctx.ana(arg, arg_ty)
        
        # return type
        return rty

    @classmethod
    def trans_Call(cls, ctx, e, idx):
        return ast.copy_location(
            ast.Call(
                func=ctx.trans(e.func),
                args=[
                    ctx.trans(arg)
                    for arg in e.args],
                keywords=[]),
            e)

    @classmethod
    def check_Assign(cls, ctx, stmt):
        targets = stmt.targets
        if len(targets) != 1:
            # TODO support for multiple targets
            raise TyError(
                "Too many assignment targets.", targets[1])
        target = targets[0]
        pat, ann = cls._get_pat_and_ann(target)
        if ann is not None:
            ty = ctx.as_type(ann)
            ctx.ana(stmt.value, ty)
        else:
            ty = ctx.syn(stmt.value)
        bindings = stmt.bindings = ctx.ana_pat(pat, ty)
        stmt.uniq_bindings = ctx.add_bindings(bindings)
    
    @staticmethod
    def _get_pat_and_ann(target):
        if isinstance(target, ast.Subscript):
            subscript_target = target.target
            slice = target.slice
            if isinstance(slice, ast.Slice):
                start, stop, step = slice.start, slice.stop, slice.step
                if start is None and stop is not None and step is None:
                    return (subscript_target, slice)
        return target, None

    @classmethod
    def trans_Assign(cls, ctx, stmt):
        assert len(stmt.bindings) == 1
        target_name = tuple(stmt.bindings.keys())[0]
        target_tr = ast.copy_location(
            ast.Name(id=stmt.uniq_bindings[target_name.id][0],
                     ctx=target_name.ctx),
            target_name)
        value = stmt.value
        value_tr = ast.copy_location(
            ctx.trans(value),
            value)
        return ast.copy_location(
            ast.Assign(
                targets=[target_tr],
                value=value_tr),
            stmt)

    @classmethod
    def check_Expr(self, ctx, stmt):
        ctx.syn(stmt.value)

    @classmethod
    def trans_Expr(self, ctx, stmt):
        return ast.copy_location(
            ast.Expr(
                value=ctx.trans(stmt.value)),
            stmt)

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

def _check_trivial_idx_ast(idx_ast):
    if isinstance(idx_ast, ast.Tuple) and len(idx_ast.elts) == 0:
        return ()
    else:
        raise TypeValidationError(
            "unit type can only have trivial index.", idx_ast)

# Maybe not in the standard library?
# TODO proto
# TODO string_in
# TODO array
# TODO numpy stuff
# TODO cl stuff

