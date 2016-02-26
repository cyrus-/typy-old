"""typy: A programmable static type system as a Python library."""
import ast  # Python standard library's abstract syntax module
import inspect  # for accessing source code for functions
import textwrap  # for stripping leading spaces from source code

import six  # Python 2-3 compatibility, e.g. metaclasses
import ordereddict # Built in to 2.7+ but needed for 2.6.
odict = ordereddict.OrderedDict

import util  # various utilities used throughout typy
import util.astx  # utility functions for working with asts

class UsageError(Exception):
    """For internal errors."""
    pass # TODO rename to InternalError

class TypeError(Exception):
    def __init__(self, message, tree):
        Exception.__init__(self, message)
        self.tree = tree

    # TODO pretty-printing
    # TODO error message codes
    # TODO review error message usability

class TypeMismatchError(TypeError):
    def __init__(self, expected, got, tree):
        TypeError.__init__(self, 
            "Type mismatch. Expected: {0}. Got: {1}.".format(expected, got), 
            tree)
        self.expected = expected
        self.got = got

class NotSupportedError(TypeError):
    def __init__(self, delegate, meth_category, meth_name, tree):
        TypeError.__init__(self, meth_name + " not supported.", tree)
        self.delegate = delegate
        self.meth_category = meth_category
        self.meth_name = meth_name
        self.tree = tree

class TypeFormationError(Exception):
    pass

class TypeInvariantError(Exception):
    def __init__(self, message, tree):
        Exception.__init__(self, message)
        self.tree = tree

def warn(message, tree=None):
    # TODO: better warning handling
    print "WARNING: "
    print message

class _TypeMetaclass(type): # here, type is Python's "type" builtin
    def __getitem__(self, idx):
        if util.contains_ellipsis(idx): 
            return _construct_incty(self, idx)
        else: 
            return _construct_ty(self, idx)

def _construct_incty(tycon, inc_idx):
    inc_idx = tycon.init_inc_idx(inc_idx)
    return IncompleteType(tycon, inc_idx, from_construct_incty=True)

def _construct_ty(tycon, idx):
    idx = tycon.init_idx(idx)
    return tycon(idx, from_construct_ty=True)

@six.add_metaclass(_TypeMetaclass)
class Type(object):
    """Base class for typy types.

    An typy type is an instance of Type.
    An typy tycon is a subclass of Type.
    """
    def __init__(self, idx, from_construct_ty=False):
        if not from_construct_ty:
            raise TypeFormationError(
                "Types should not be constructed directly. Use tycon[idx].")
        self.idx = idx

    def __call__(self, f):
        raise TypeError("Non-FnType used as a top-level function decorator.")

    def __eq__(self, other):
        return isinstance(other, Type) \
            and tycon(self) is tycon(other) \
            and self.idx == other.idx

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.__class__.__name__) + "[" + str(self.idx) + "]"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def init_idx(cls, idx): 
        raise TypeFormationError("init_idx not implemented.")

    @classmethod
    def init_inc_idx(cls, inc_idx):
        raise TypeFormationError("init_inc_idx not implemented.")

    # Num

    def ana_Num(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Num", e)

    def translate_Num(self, ctx, e):    
        raise NotSupportedError(self, "method", "translate_Num", e)

    @classmethod
    def syn_idx_Num(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_Num", e)

    def ana_pat_Num(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_Num", pat)

    def translate_pat_Num(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_Num", pat)

    # Str 

    def ana_Str(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Str", e)

    @classmethod
    def syn_idx_Str(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_Str", e)

    def translate_Str(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Str", e)

    def ana_pat_Str(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_Str", pat)

    def translate_pat_Str(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_Str", pat)

    # Tuple

    def ana_Tuple(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Tuple", e)

    @classmethod
    def syn_idx_Tuple(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_Tuple", e)

    def translate_Tuple(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Tuple", e)

    def ana_pat_Tuple(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_Tuple", pat)

    def translate_pat_Tuple(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_Tuple", pat)

    # List

    def ana_List(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_List", e)

    @classmethod
    def syn_idx_List(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_List", e)

    def translate_List(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_List", e)

    def ana_pat_List(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_List", pat)

    def translate_pat_List(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_List", pat)

    # Dict

    def ana_Dict(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Dict", e)

    @classmethod
    def syn_idx_Dict(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_Dict", e)

    def translate_Dict(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Dict", e)

    def ana_pat_Dict(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_Dict", pat)

    def translate_pat_Dict(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_Dict", pat)

    # Set

    def ana_Set(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Set", e)

    @classmethod
    def syn_idx_Set(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_Set", e)

    def translate_Set(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Set", e)

    def ana_pat_Set(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_Set", pat)

    def translate_pat_Set(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_Set", pat)

    # Lambda

    def ana_Lambda(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Lambda", e)

    @classmethod
    def syn_idx_Lambda(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_Lambda", e)

    def translate_Lambda(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Lambda", e)

    # Name_constructor

    def ana_Name_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Name_constructor", e)

    @classmethod
    def syn_idx_Name_constructor(cls, ctx, e, inc_idx):
        raise NotSupportedError(cls, "class method", "syn_idx_Name_constructor", e)

    def translate_Name_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Name_constructor", e)

    def ana_pat_Name_constructor(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_Name_constructor", pat)

    def translate_pat_Name_constructor(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_Name_constructor", pat)

    # Unary_Name_constructor

    def ana_Unary_Name_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Unary_Name_constructor", e)

    @classmethod
    def syn_idx_Unary_Name_constructor(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", 
                                "syn_idx_Unary_Name_constructor", e)

    def translate_Unary_Name_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", 
                                "translate_Unary_Name_constructor", e)

    def ana_pat_Unary_Name_constructor(self, ctx, pat):
        raise NotSupportedError(self, "method", 
                                "ana_pat_Unary_Name_constructor", pat)

    def translate_pat_Unary_Name_constructor(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method",
                                "translate_pat_Unary_Name_constructor", pat)

    # Call_constructor

    def ana_Call_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Call_constructor", e)

    @classmethod
    def syn_idx_Call_constructor(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "method", "syn_idx_Call_constructor", e)

    def translate_Call_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Call_constructor", e)

    def ana_pat_Call_constructor(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_Call_constructor", pat)

    def translate_pat_Call_constructor(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_Call_constructor", pat)

    # UnaryOp

    def syn_UnaryOp(self, ctx, e):
        raise NotSupportedError(self, "method", "syn_UnaryOp", e)

    def translate_UnaryOp(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_UnaryOp", e)

    # BinOp

    def syn_BinOp(self, ctx, e):
        raise NotSupportedError(self, "method", "syn_BinOp", e)

    def translate_BinOp(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_BinOp", e)

    # Compare

    def syn_Compare(self, ctx, e):
        raise NotSupportedError(self, "method", "syn_Compare", e)

    def translate_Compare(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Compare", e)

    # BoolOp

    def syn_BoolOp(self, ctx, e):
        raise NotSupportedError(self, "method", "syn_BoolOp", e)

    def translate_BoolOp(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_BoolOp", e)

    # Attribute

    def syn_Attribute(self, ctx, e):
        raise NotSupportedError(self, "method", "syn_Attribute", e)

    def translate_Attribute(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Attribute", e)

    # Subscript

    def syn_Subscript(self, ctx, e):
        raise NotSupportedError(self, "method", "syn_Subscript", e)

    def translate_Subscript(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Subscript", e)

    # Call

    def syn_Call(self, ctx, e):
        raise NotSupportedError(self, "method", "syn_Call", e)

    def translate_Call(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Call", e)

class IncompleteType(object):
    """Represents an incomplete type, used for literal forms.

    An incomplete type is constructed by providing an index 
    containing one or more ellipses (so the constructor need 
    not typically be called directly):
        tycon[a, ..., b]
    """
    def __init__(self, tycon, inc_idx, from_construct_incty=False):
        if not from_construct_incty:
            raise TypeFormationError(
                "Incomplete types should not be constructed directly. Use tycon[idx].")
        self.tycon = tycon
        self.inc_idx = inc_idx

    def __call__(self, f):
        if issubclass(self.tycon, FnType):
            (ast, static_env) = _reflect_func(f)
            return Fn(ast, static_env, self)
        else: 
            raise TypeError(
                "Incomplete non-FnType used as a top-level function decorator.",
                None)

    def __eq__(self, other):
        return isinstance(other, IncompleteType) \
            and tycon(self) is tycon(other) \
            and self.inc_idx == other.inc_idx

    def __ne__(self, other):
        return not self.__eq__(other)

def tycon(ty):
    """Returns the tycon of the provided type or incomplete type ."""
    if isinstance(ty, Type):
        return ty.__class__
    elif isinstance(ty, IncompleteType):
        return ty.tycon
    else:
        raise UsageError("Argument to tycon is not a type or incomplete type.")

def is_tycon(x):
    """Indicates whether the provided value is a tycon."""
    return issubclass(x, Type)

class FnType(Type):
    """Base class for typy function types."""
    def __new__(cls, idx_or_f, from_construct_ty=False):
        # override __new__ to allow the class to be used as fn decorator
        if not from_construct_ty and inspect.isfunction(idx_or_f):
            (tree, static_env) = _reflect_func(idx_or_f)
            return Fn(tree, static_env, cls[...])
        else: 
            return super(FnType, cls).__new__(cls, idx_or_f, from_construct_ty)

    def __call__(self, f):
        (tree, static_env) = _reflect_func(f)
        return Fn(tree, static_env, self)

    @classmethod
    def init_ctx(cls, ctx): 
        pass

    @classmethod
    def preprocess_FunctionDef_toplevel(cls, fn, tree):
        pass 

    # FunctionDef

    def ana_FunctionDef(self, ctx, tree, ty):
        raise NotSupportedError(self, "method", "ana_FunctionDef", tree)

    @classmethod
    def syn_idx_FunctionDef(cls, ctx, tree, inc_idx):
        raise NotSupportedError(cls, "class method", "ana_FunctionDef", tree)

    def translate_FunctionDef(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_FunctionDef", tree)

    # Name

    @classmethod 
    def syn_Name(cls, ctx, e):
        raise NotSupportedError(cls, "class method", "syn_Name", e)

    def translate_Name(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Name", tree)

    # match expressions

    @classmethod
    def ana_match_expr(cls, ctx, e, ty):
        raise NotSupportedError(cls, "class method", "ana_match_expr", e)

    @classmethod
    def syn_match_expr(cls, ctx, e):
        raise NotSupportedError(cls, "class method", "syn_match_expr", e)

    # if expressions

    @classmethod
    def translate_match_expr(cls, ctx, e):
        raise NotSupportedError(cls, "method", "translate_match_expr", e)

    @classmethod
    def ana_IfExp(cls, ctx, e, ty):
        raise NotSupportedError(cls, "class method", "ana_IfExp", e)

    @classmethod
    def syn_IfExp(cls, ctx, e):
        raise NotSupportedError(cls, "class method", "syn_IfExp", e)

    @classmethod
    def translate_IfExp(cls, ctx, e):
        raise NotSupportedError(cls, "class method", "translate_IfExp", e)

def _reflect_func(f): 
    source = textwrap.dedent(inspect.getsource(f))
    tree = ast.parse(source).body[0] # ast.parse produces a Module, so grab its only item
    return (tree, StaticEnv.from_func(f))

class StaticEnv(object):
    def __init__(self, closure, globals):
        self.closure = closure
        self.globals = globals

    def __getitem__(self, item):
        try: 
            return self.closure[item]
        except KeyError:
            return self.globals[item]

    @classmethod
    def from_func(cls, f):
        closure = _func_closure(f)
        globals = f.func_globals
        return cls(closure, globals)

    def eval_expr_ast(self, tree):
        tree = ast.Expression(tree)
        code = compile(tree, "<eval_expr_ast>", "eval")
        return eval(code, self.globals, self.closure)

def _func_closure(f):
    closure = f.func_closure
    if closure is None: 
        return {}
    else:
        return dict(_get_cell_contents(f.func_code.co_freevars, closure))

def _get_cell_contents(co_freevars, closure):
    for x, c in zip(co_freevars, closure):
        try:
            yield x, c.cell_contents
        except ValueError:
            continue

class Fn(object):
    """All top-level typy functions are instances of Fn."""
    def __init__(self, tree, static_env, ascription):
        assert isinstance(tree, ast.AST)
        assert isinstance(static_env, StaticEnv)
        assert isinstance(ascription, Type) \
            or isinstance(ascription, IncompleteType)
        assert issubclass(tycon(ascription), FnType)
        self.tree = tree
        self.static_env = static_env
        self.ascription = ascription
        self.typechecked = False
        self.compiled = False

        tc = tycon(ascription)
        tc.preprocess_FunctionDef_toplevel(self, tree)

    def typecheck(self):
        if self.typechecked: 
            return
        tree, ascription = self.tree, self.ascription
        ctx = self.ctx = Context(self)
        tycon(ascription).init_ctx(ctx)
        if isinstance(ascription, Type):
            ctx.ana(tree, ascription)
        else: # IncompleteType
            ctx.ana_intro_inc(tree, ascription)
        ty = tree.ty
        self.typechecked = True
        return ty

    def compile(self):
        self.typecheck()
        if self.compiled: 
            return
        tree, ctx = self.tree, self.ctx
        ty = tree.ty
        translation = ty.translate_FunctionDef(ctx, tree)
        self.translation = translation
        self.compiled = True
        return translation

    def __call__(self, *args):
        # TODO: implement this
        raise NotImplementedError()

class Context(object):
    def __init__(self, fn):
        self.fn = fn
        self.data = {}
        self._id_count = {}
        self._tmp_count = {}

    def generate_fresh_id(self, id):
        _id_count = self._id_count
        try:
            id_count = _id_count[id]
        except KeyError:
            _id_count[id] = 1
            return id
        else:
            _id_count[id] = id_count + 1
            return '__typy_id_' + id + '_' + str(id_count) + '__'
    
    def generate_fresh_tmp(self, tmp):
        _tmp_count = self._tmp_count
        print _tmp_count
        try:
            tmp_count = _tmp_count[tmp]
        except KeyError:
            tmp_count = _tmp_count[tmp] = 1
        else:
            tmp_count = _tmp_count[tmp] = tmp_count + 1
        return '__typy_tmp_' + tmp + '_' + str(tmp_count) + '__'

    def ana(self, e, ty):
        if not isinstance(ty, Type):
            raise UsageError("Cannot analyze an expression against a non-type.")
        if _is_intro_form(e):
            e.is_intro_form = True
            classname = e.__class__.__name__
            if classname == "Name":
                classname = "Name_constructor"
            elif classname == "Call":
                classname = "Call_constructor"
            elif classname == "UnaryOp":
                classname = "Unary_Name_constructor"
            ana_method = 'ana_%s' % classname
            method = getattr(ty, ana_method)
            method(self, e)
            e.ty = ty
            e.delegate = ty
            e.translation_method_name = 'translate_%s' % classname
        elif _is_match_expr(e):
            e.is_match_expr = True
            delegate = tycon(self.fn.ascription)
            delegate.ana_match_expr(self, e, ty)
            e.ty = ty
            e.delegate = delegate
            e.translation_method_name = 'translate_match_expr'
        elif isinstance(e, ast.IfExp):
            delegate = tycon(self.fn.ascription)
            delegate.ana_IfExp(self, e, ty)
            e.ty = ty
            e.delegate = delegate
            e.translation_method_name = 'translate_IfExp'
        else:
            syn_ty = self.syn(e)
            if ty != syn_ty:
                raise TypeMismatchError(ty, syn_ty, e)

    def ana_intro_inc(self, value, inc_ty):
        if not _is_intro_form(value):
            raise UsageError("Term is not an intro form.")
        if not isinstance(inc_ty, IncompleteType):
            raise UsageError("No incomplete type provided.")
        classname = value.__class__.__name__
        if classname == "Name":
            classname = "Name_constructor"
        elif classname == "Call":
            classname = "Call_constructor"
        elif classname == "UnaryOp":
            classname = "Unary_Name_constructor"
        syn_idx_methodname = 'syn_idx_%s' % classname
        delegate = inc_ty.tycon
        method = getattr(delegate, syn_idx_methodname)
        syn_idx = method(self, value, inc_ty.inc_idx)
        ty = _construct_ty(delegate, syn_idx)
        value.is_intro_form = True
        value.translation_method_name = "translate_%s" % classname
        value.delegate, value.ty = delegate, ty
        return ty 

    def syn(self, e):
        if _is_match_expr(e):
            e.is_match_expr = True
            delegate = tycon(self.fn.ascription)
            ty = delegate.syn_match_expr(self, e)
            e.ty = ty
            e.delegate = delegate
            e.translation_method_name = "translate_match_expr"
        elif isinstance(e, ast.Subscript):
            value, slice_ = e.value, e.slice 
            ty = _process_ascription_slice(slice_, self.fn.static_env)
            if isinstance(ty, Type):
                self.ana(value, ty)
                delegate = value.delegate
                e.is_ascription = True 
            elif isinstance(ty, IncompleteType):
                if _is_intro_form(value):
                    self.ana_intro_inc(value, ty)
                    delegate, ty = value.delegate, value.ty
                    e.is_ascription = True 
                else:
                    raise TypeError(
                        "Incomplete type ascriptions can only appear"
                        "on introductory forms.", 
                        value)
            else:
                # not an ascription
                delegate = self.syn(value)
                ty = delegate.syn_Subscript(self, e)
                e.translation_method_name = 'translate_Subscript'
        elif isinstance(e, ast.Name):
            delegate = tycon(self.fn.ascription)
            ty = delegate.syn_Name(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_Name'
            else:
                raise TypeInvariantError(
                    "syn_Name did not return a type.", e)
        elif isinstance(e, ast.Call):
            func = e.func
            delegate = self.syn(func)
            ty = delegate.syn_Call(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_Call'
            else:
                raise TypeInvariantError(
                    "syn_Call did not return a type.", e)
        elif isinstance(e, ast.UnaryOp):
            operand = e.operand
            delegate = self.syn(operand)
            ty = delegate.syn_UnaryOp(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_UnaryOp'
            else:
                raise TypeInvariantError(
                    "syn_UnaryOp did not return a type.", e)
        elif isinstance(e, ast.BinOp):
            left = e.left
            delegate = self.syn(left)
            ty = delegate.syn_BinOp(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_BinOp'
            else:
                raise TypeInvariantError(
                    "syn_BinOp did not return a type.", e)
        elif isinstance(e, ast.Compare):
            left, comparators = e.left, e.comparators
            delegate, match = None, None
            for e_ in util.tpl_cons(left, comparators):
                try:
                    delegate = self.syn(e_)
                    match = e_
                    break
                except TypeError: 
                    continue
            if delegate is None:
                raise TypeError("No comparators synthesize a type.", e)
            match.match = True
            ty = delegate.syn_Compare(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_Compare'
            else:
                raise TypeInvariantError(
                    "syn_Compare did not return a type.", e)
        elif isinstance(e, ast.BoolOp):
            values = e.values
            delegate, match = None, None
            for value in values:
                try:
                    delegate = self.syn(value)
                    match = value
                    break
                except TypeError:
                    continue
            if delegate is None:
                raise TypeError("No clauses of boolean operation synthesize a type.", e)
            match.match = True
            ty = delegate.syn_BoolOp(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_BoolOp'
            else:
                raise TypeInvariantError(
                    "syn_BoolOp did not return a type.", e)
        elif isinstance(e, ast.Attribute):
            value = e.value
            delegate = self.syn(value)
            ty = delegate.syn_Attribute(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_Attribute'
            else:
                raise TypeInvariantError(
                    "syn_Attribute did not return a type.", e)
        elif isinstance(e, ast.IfExp):
            delegate = tycon(self.fn.ascription)
            ty = delegate.syn_IfExp(self, e)
            if isinstance(ty, Type):
                e.translation_method_name = 'translate_IfExp'
            else:
                raise TypeInvariantError(
                    "syn_IfExp did not return a type.", e)
        else:
            raise TypeError("Unsupported form for type synthesis: " + 
                            e.__class__.__name__, e)

        assert delegate is not None
        assert ty is not None 
        e.delegate, e.ty = delegate, ty
        return ty 

    def translate(self, tree):
        if hasattr(tree, "is_ascription"):
            translation = self.translate(tree.value)
        elif hasattr(tree, "is_match_expr"):
            delegate = tree.delegate
            translation = delegate.translate_match_expr(self, tree)
        elif hasattr(tree, "is_intro_form"):
            delegate = tree.ty
            method = getattr(delegate, tree.translation_method_name)
            translation = method(self, tree)
        elif isinstance(tree, ast.Name):
            delegate = self.fn.tree.ty
            translation = delegate.translate_Name(self, tree)
        elif isinstance(tree, (
                ast.Call, 
                ast.Subscript, 
                ast.Attribute, 
                ast.BoolOp, 
                ast.Compare, 
                ast.BinOp, 
                ast.UnaryOp,
                ast.IfExp)):
            delegate = tree.delegate
            method = getattr(delegate, tree.translation_method_name)
            translation = method(self, tree)
        else:
            method_name = tree.translation_method_name
            delegate = tree.ty
            method = getattr(delegate, method_name)
            translation = method(self, tree)
        return translation

    def ana_pat(self, pat, ty):
        if _is_pat_intro_form(pat):
            classname = pat.__class__.__name__
            if classname == "Name":
                classname = "Name_constructor"
            elif classname == "Call":
                classname = "Call_constructor"
            elif classname == "UnaryOp":
                classname = "Unary_Name_constructor"
            ana_pat_methodname = 'ana_pat_' + classname
            delegate = ty
            method = getattr(delegate, ana_pat_methodname)
            bindings = method(self, pat)
            if not isinstance(bindings, odict):
                raise UsageError("Expected ordered dict.")
            for name, binding_ty in bindings.iteritems():
                if not util.astx.is_identifier(name):
                    raise UsageError("Binding " + str(name) + " is not an identifier.")
                if not isinstance(binding_ty, Type):
                    raise UsageError("Binding for " + name + " has invalid type.")
        elif isinstance(pat, ast.Name):
            id = pat.id
            if id == "_":
                bindings = odict()
            else:
                bindings = odict((
                    (id, ty),
                ))
        else:
            raise TypeError("Invalid pattern form", pat)
        pat.bindings = bindings
        pat.ty = ty
        return bindings

    def translate_pat(self, pat, scrutinee_trans):
        if _is_pat_intro_form(pat):
            classname = pat.__class__.__name__
            if classname == "Name":
                classname = "Name_constructor"
            elif classname == "Call":
                classname = "Call_constructor"
            elif classname == "UnaryOp":
                classname = "Unary_Name_constructor"
            translate_pat_methodname = "translate_pat_" + classname
            delegate = pat.ty
            method = getattr(delegate, translate_pat_methodname)
            condition, binding_translations = method(self, pat, scrutinee_trans)
        elif isinstance(pat, ast.Name):
            condition = ast.Name(id='True', ctx=ast.Load())
            id = pat.id
            if id == "_":
                binding_translations = odict()
            else:
                binding_translations = odict(((id, scrutinee_trans),))
        else:
            raise UsageError("Cannot translate this pattern...")
        bindings = pat.bindings
        if bindings.keys() != binding_translations.keys():
            raise UsageError("Not all bindings have translations.")
        return condition, binding_translations

_intro_forms = (
    ast.FunctionDef, # only stmt intro form
    ast.Lambda, 
    ast.Dict, 
    ast.Set, 
    # ast.ListComp, 
    # ast.SetComp, 
    # ast.DictComp, 
    # ast.GeneratorExp, 
    ast.Num, 
    ast.Str, 
    ast.List, 
    ast.Tuple)
def _is_intro_form(e):
    return (isinstance(e, _intro_forms) or 
            _is_Name_constructor(e) or
            _is_Unary_Name_constructor(e) or 
            _is_Call_constructor(e))

_pat_intro_forms = (
    ast.Dict,
    ast.Set,
    ast.Num,
    ast.Str,
    ast.List,
    ast.Tuple)
def _is_pat_intro_form(pat):
    return (isinstance(pat, _pat_intro_forms) or
            _is_Name_constructor(pat) or 
            _is_Unary_Name_constructor(pat) or
            _is_Call_constructor(pat))

def _is_Name_constructor(e):
    return isinstance(e, ast.Name) and _is_Name_constructor_id(e.id)

def _is_Name_constructor_id(id):
    return id != "" and id[0].isupper()

def _is_Unary_Name_constructor(e):
    return (isinstance(e, ast.UnaryOp) and 
            isinstance(e.op, (ast.USub, ast.UAdd, ast.Invert)) and 
            _is_Name_constructor(e.operand))

def _is_Call_constructor(e):
    return isinstance(e, ast.Call) and _is_Name_constructor(e.func)

def _is_match_expr(e):
    # {scrutinee} is {rules}
    return (isinstance(e, ast.Compare) and
            len(e.ops) == 1 and 
            isinstance(e.ops[0], ast.Is) and
            isinstance(e.left, ast.Set) and 
            isinstance(e.comparators[0], ast.Dict))

def _check_ascription_ast(e):
    if isinstance(e, ast.Subscript):
        value, slice = e.value, e.slice
        if isinstance(slice, ast.Slice):
            lower, upper, step = slice.lower, slice.upper, slice.step
            if lower is None and upper is not None and step is None:
                return value, upper

def _check_ascription(e, static_env):
    if isinstance(e, ast.Subscript):
        value, slice = e.value, e.slice
        asc = _process_ascription_slice(slice, static_env)
        return value, asc
    return None

def _process_ascription_slice(slice_, static_env):
    # TODO make this call _process_asc_ast
    if isinstance(slice_, ast.Slice):
        lower, upper, step = slice_.lower, slice_.upper, slice_.step
        if lower is None and upper is not None and step is None:
            ty = static_env.eval_expr_ast(upper)
            if isinstance(ty, Type) or isinstance(ty, IncompleteType):
                return ty
            elif issubclass(ty, Type):
                return ty[...]
            else:
                raise TypeError("Type ascription is not a type or incomplete type.",
                    upper)
    return None 

def _process_asc_ast(ctx, asc_ast):
    asc = ctx.fn.static_env.eval_expr_ast(asc_ast)
    if (isinstance(asc, Type) or 
            isinstance(asc, IncompleteType)):
        return asc
    elif issubclass(asc, Type):
        return asc[...]
    else:
        raise TypeError("Invalid ascription.", asc_ast)

