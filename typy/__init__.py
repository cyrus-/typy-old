"""typy: A programmable static type system as a Python library."""
import ast  # Python standard library's abstract syntax module
import inspect  # for accessing source code for functions
import textwrap  # for stripping leading spaces from source code

import six  # Python 2-3 compatibility, e.g. metaclasses
import ordereddict
_OD = ordereddict.OrderedDict

import util  # various utilities used throughout typy
import util.astx  # utility functions for working with asts

class UsageError(Exception):
    pass

class TypeError(Exception):
    def __init__(self, message, tree):
        Exception.__init__(self, message)
        self.tree = tree

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
        if _contains_ellipsis(idx): 
            return _construct_incty(self, idx)
        else: 
            return _construct_ty(self, idx)

def _contains_ellipsis(idx):
    if idx is Ellipsis: 
        return True
    elif isinstance(idx, tuple):
        for item in idx:
            if item is Ellipsis: 
                return True
    return False 

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
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        return inc_idx

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

    def ana_pat_Lambda(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_Lambda", pat)

    def translate_pat_Lambda(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_Lambda", pat)

    # Name_constructor

    def ana_Name_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Name_constructor", e)

    @classmethod
    def syn_idx_Name_constructor(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_Name_constructor", e)

    def translate_Name_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Name_constructor", e)

    def ana_pat_Name_constructor(self, ctx, pat):
        raise NotSupportedError(self, "method", "ana_pat_Name_constructor", pat)

    def translate_pat_Name_constructor(self, ctx, pat, scrutinee_trans):
        raise NotSupportedError(self, "method", "translate_pat_Name_constructor", pat)

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
            raise TypeError("Incomplete non-FnType used as a top-level function decorator.")

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
    def push_bindings(cls, ctx, bindings):
        raise NotSupportedError(cls, "class method", "push_bindings", None)

    @classmethod
    def pop_bindings(cls, ctx):
        raise NotSupportedError(cls, "class method", "pop bindings", None)

    @classmethod
    def preprocess_FunctionDef_toplevel(cls, fn, tree):
        pass 

    def ana_FunctionDef_toplevel(self, ctx, tree, ty):
        raise NotSupportedError(self, "method", "ana_FunctionDef_toplevel", tree)

    @classmethod
    def syn_idx_FunctionDef_toplevel(cls, ctx, tree, inc_ty):
        raise NotSupportedError(cls, "class method", "ana_FunctionDef_toplevel", tree)

    def translate_FunctionDef_toplevel(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_FunctionDef_toplevel", tree)

    @classmethod 
    def syn_Name(cls, ctx, e):
        raise NotSupportedError(cls, "class method", "syn_Name", e)

    def translate_Name(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Name", tree)

    ################################################################################
    # The following stubs are pasted from the result of running _generate_FnType.py.
    ################################################################################

    @classmethod
    def check_FunctionDef(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_FunctionDef", tree)

    def translate_FunctionDef(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_FunctionDef", tree)

    @classmethod
    def check_ClassDef(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_ClassDef", tree)

    def translate_ClassDef(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_ClassDef", tree)

    @classmethod
    def check_Return(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Return", tree)

    def translate_Return(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Return", tree)

    @classmethod
    def check_Delete(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Delete", tree)

    def translate_Delete(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Delete", tree)

    @classmethod
    def check_Assign(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Assign", tree)

    def translate_Assign(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Assign", tree)

    @classmethod
    def check_AugAssign(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_AugAssign", tree)

    def translate_AugAssign(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_AugAssign", tree)

    @classmethod
    def check_Print(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Print", tree)

    def translate_Print(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Print", tree)

    @classmethod
    def check_For(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_For", tree)

    def translate_For(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_For", tree)

    @classmethod
    def check_While(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_While", tree)

    def translate_While(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_While", tree)

    @classmethod
    def check_If(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_If", tree)

    def translate_If(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_If", tree)

    @classmethod
    def check_With(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_With", tree)

    def translate_With(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_With", tree)

    @classmethod
    def check_Raise(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Raise", tree)

    def translate_Raise(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Raise", tree)

    @classmethod
    def check_TryExcept(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_TryExcept", tree)

    def translate_TryExcept(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_TryExcept", tree)

    @classmethod
    def check_TryFinally(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_TryFinally", tree)

    def translate_TryFinally(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_TryFinally", tree)

    @classmethod
    def check_Assert(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Assert", tree)

    def translate_Assert(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Assert", tree)

    @classmethod
    def check_Import(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Import", tree)

    def translate_Import(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Import", tree)

    @classmethod
    def check_ImportFrom(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_ImportFrom", tree)

    def translate_ImportFrom(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_ImportFrom", tree)

    @classmethod
    def check_Exec(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Exec", tree)

    def translate_Exec(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Exec", tree)

    @classmethod
    def check_Global(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Global", tree)

    def translate_Global(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Global", tree)

    @classmethod
    def check_Expr(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Expr", tree)

    def translate_Expr(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Expr", tree)

    @classmethod
    def check_Pass(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Pass", tree)

    def translate_Pass(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Pass", tree)

    @classmethod
    def check_Break(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Break", tree)

    def translate_Break(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Break", tree)

    @classmethod
    def check_Continue(cls, ctx, tree):
        raise NotSupportedError(cls, "class method", "check_Continue", tree)

    def translate_Continue(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_Continue", tree)

    ################################################################################
    # End autogenerated section
    ################################################################################

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
            delegate = ty = ascription
            delegate.ana_FunctionDef_toplevel(ctx, tree)
        else: # IncompleteType
            delegate = ascription.tycon
            idx = delegate.syn_idx_FunctionDef_toplevel(ctx, tree, ascription)
            ty = _construct_ty(delegate, idx)
        tree.ty, tree.delegate = ty, delegate
        self.typechecked = True
        return ty

    def compile(self):
        self.typecheck()
        if self.compiled: 
            return
        tree, ctx = self.tree, self.ctx
        ty = tree.ty
        translation = ty.translate_FunctionDef_toplevel(ctx, tree)
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
        print "TMP" + tmp
        print _tmp_count
        try:
            tmp_count = _tmp_count[tmp]
        except KeyError:
            print " ERROR "
            tmp_count = _tmp_count[tmp] = 1
        else:
            tmp_count = _tmp_count[tmp] = tmp_count + 1
        return '__typy_tmp_' + tmp + '_' + str(tmp_count) + '__'

    def check(self, stmt):
        if not isinstance(stmt, ast.stmt):
            raise UsageError("Cannot check a non-statement.")
        classname = stmt.__class__.__name__
        check_method = 'check_%s' % classname
        delegate = tycon(self.fn.ascription)
        method = getattr(delegate, check_method)
        method(self, stmt)

    def ana(self, e, ty):
        if not isinstance(e, ast.expr):
            raise UsageError("Cannot analyze a non-expression.")
        if not isinstance(ty, Type):
            raise UsageError("Cannot analyze an expression against a non-type.")
        if _is_intro_form(e):
            classname = e.__class__.__name__
            if classname == "Name":
                classname = "Name_constructor"
            elif classname == "Call":
                classname = "Call_constructor"
            ana_method = 'ana_%s' % classname
            method = getattr(ty, ana_method)
            method(self, e)
            e.ty = ty
            e.delegate = ty
            e.translation_method_name = 'translate_%s' % classname
        elif _is_match_expr(e):
            elts = e.left.elts
            n_elts = len(elts)
            if n_elts == 0:
                raise TypeError("Scrutinee missing.", e)
            elif n_elts > 1:
                # TODO: turn it into a tuple
                raise TypeError("Too many scrutinees.", e)
            scrutinee = elts[0]
            scrutinee_ty = self.syn(scrutinee)
            rule_dict = e.comparators[0]
            rules = zip(rule_dict.keys, rule_dict.values)
            for (pat, branch) in rules:
                bindings = self.ana_pat(pat, scrutinee_ty)
                self._push_bindings(bindings)
                self.ana(branch, ty)
                self._pop_bindings()
            e.delegate = scrutinee_ty
            e.ty = ty
        else:
            syn_ty = self.syn(e)
            if ty != syn_ty:
                raise TypeMismatchError(ty, syn_ty, e)

    def ana_intro_inc(self, value, inc_ty):
        if not _is_intro_form(value):
            raise UsageError("Expression is not an intro form.")
        if not isinstance(inc_ty, IncompleteType):
            raise UsageError("No incomplete type provided.")
        classname = value.__class__.__name__
        if classname == "Name":
            classname = "Name_constructor"
        elif classname == "Call":
            classname = "Call_constructor"
        syn_idx_methodname = 'syn_idx_%s' % classname
        delegate = inc_ty.tycon
        method = getattr(delegate, syn_idx_methodname)
        syn_idx = method(self, value, inc_ty.inc_idx)
        ty = _construct_ty(delegate, syn_idx)
        value.translation_method_name = "translate_%s" % classname
        value.delegate, value.ty = delegate, ty
        return ty 

    def syn(self, e):
        if _is_match_expr(e):
            elts = e.left.elts
            n_elts = len(elts)
            if n_elts == 0:
                raise TypeError("Scrutinee missing.", e)
            elif n_elts > 1:
                raise TypeError("Too many scrutinees.", e)
            scrutinee = elts[0]
            scrutinee_ty = self.syn(scrutinee)
            rule_dict = e.comparators[0]
            rules = zip(rule_dict.keys, rule_dict.values)
            syn_ty = None
            for (pat, branch) in rules:
                bindings = self.ana_pat(pat, scrutinee_ty)
                self._push_bindings(bindings)
                branch_ty = self.syn(branch)
                if syn_ty is None:
                    syn_ty = branch_ty
                else:
                    if syn_ty != branch_ty:
                        raise TypeError("Inconsistent branch types.", branch)
                self._pop_bindings()
            delegate = scrutinee_ty
            ty = syn_ty
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
                        "Incomplete type ascriptions can only appear on introductory forms.", 
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
        else:
            raise TypeError("Unsupported form for type synthesis: " + e.__class__.__name__, e)

        assert delegate is not None
        assert ty is not None 
        e.delegate, e.ty = delegate, ty
        return ty 

    def translate(self, tree):
        if isinstance(tree, ast.stmt):
            classname = tree.__class__.__name__
            method_name = 'translate_' + classname
            delegate = self.fn.tree.ty
            method = getattr(delegate, method_name)
            translation = method(self, tree)
            if isinstance(translation, ast.stmt):
                translation = [translation]
        elif isinstance(tree, ast.expr):
            if hasattr(tree, "is_ascription"):
                translation = self.translate(tree.value)
            elif _is_match_expr(tree):
                scrutinee = tree.left.elts[0]
                scrutinee_trans = self.translate(scrutinee)
                scrutinee_var = ast.Name(id="__typy_scrutinee__", ctx=ast.Load())
                rules = tree.comparators[0]
                rules = zip(rules.keys, rules.values)
                rule_translations = tuple(_translate_rules(self, rules, scrutinee_var))
                if len(rule_translations) == 0:
                    compiled_rules = util.astx.expr_Raise_Exception_string("Match failure.")
                else:
                    rt_0 = rule_translations[0]
                    rt_rest = rule_translations[1:]
                    compiled_rules = _compile_rule(rt_0, rt_rest)
                translation = util.astx.make_simple_Call(
                    util.astx.make_Lambda(('__typy_scrutinee__',), compiled_rules),
                    [scrutinee_trans])
            elif _is_intro_form(tree):
                delegate = tree.ty
                method = getattr(delegate, tree.translation_method_name)
                translation = method(self, tree)
            else:
                if isinstance(tree, ast.Name):
                    delegate = self.fn.tree.ty
                    translation = delegate.translate_Name(self, tree)
                elif isinstance(tree, (
                        ast.Call, 
                        ast.Subscript, 
                        ast.Attribute, 
                        ast.BoolOp, 
                        ast.Compare, 
                        ast.BinOp, 
                        ast.UnaryOp)):
                    delegate = tree.delegate
                    method = getattr(delegate, tree.translation_method_name)
                    translation = method(self, tree)
                else:
                    method_name = tree.translation_method_name
                    delegate = tree.ty
                    method = getattr(delegate, method_name)
                    translation = method(self, tree)
        else:
            raise NotImplementedError("cannot translate this...")
        return translation

    def ana_pat(self, pat, ty):
        if _is_intro_form(pat):
            classname = pat.__class__.__name__
            if classname == "Name":
                classname = "Name_constructor"
            elif classname == "Call":
                classname = "Call_constructor"
            ana_pat_methodname = 'ana_pat_' + classname
            delegate = ty
            method = getattr(delegate, ana_pat_methodname)
            bindings = method(self, pat)
            if not isinstance(bindings, _OD):
                raise UsageError("Expected ordered dict.")
            for name, binding_ty in bindings.iteritems():
                if not util.astx.is_identifier(name):
                    raise UsageError("Binding " + str(name) + " is not an identifier.")
                if not isinstance(binding_ty, Type):
                    raise UsageError("Binding for " + name + " has invalid type.")
        elif isinstance(pat, ast.Name):
            id = pat.id
            if id == "_":
                bindings = {}
            else:
                bindings = {id : ty}
        else:
            raise TypeError("Invalid pattern form", pat)
        pat.bindings = bindings
        pat.ty = ty
        return bindings

    def translate_pat(self, pat, scrutinee_trans):
        if _is_intro_form(pat):
            classname = pat.__class__.__name__
            if classname == "Name":
                classname = "Name_constructor"
            elif classname == "Call":
                classname = "Call_constructor"
            translate_pat_methodname = "translate_pat_" + classname
            delegate = pat.ty
            method = getattr(delegate, translate_pat_methodname)
            condition, binding_translations = method(self, pat, scrutinee_trans)
        elif isinstance(pat, ast.Name):
            condition = ast.Name(id='True', ctx=ast.Load())
            id = pat.id
            if id == "_":
                binding_translations = _OD()
            else:
                binding_translations = _OD(((id, scrutinee_trans),))
        else:
            raise UsageError("Cannot translate this pattern...")
        bindings = pat.bindings
        if bindings.keys() != binding_translations.keys():
            raise UsageError("Not all bindings have translations.")
        return condition, binding_translations

    def _push_bindings(self, bindings):
        tc = tycon(self.fn.ascription)
        tc.push_bindings(self, bindings)

    def _pop_bindings(self):
        tc = tycon(self.fn.ascription)
        tc.pop_bindings(self)
 
_intro_forms = (
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
            _is_Call_constructor(e))

def _is_Name_constructor(e):
    return isinstance(e, ast.Name) and e.id[0].isupper()

def _is_Call_constructor(e):
    return isinstance(e, ast.Call) and _is_Name_constructor(e.func)

def _process_ascription_slice(slice_, static_env):
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

def _is_match_expr(e):
    # {scrutinee} is {rules}
    return (isinstance(e, ast.Compare) and
            len(e.ops) == 1 and 
            isinstance(e.ops[0], ast.Is) and
            isinstance(e.left, ast.Set) and 
            isinstance(e.comparators[0], ast.Dict))

def _translate_rules(ctx, rules, scrutinee_trans):
    for (pat, branch) in rules:
        (condition, binding_translations) = ctx.translate_pat(pat, scrutinee_trans)
        if not isinstance(condition, ast.expr):
            raise UsageError("Condition must be an expression.")
        if not pat.bindings.keys() == binding_translations.keys():
            raise UsageError("All bindings must have translations.")
        for binding_translation in binding_translations.itervalues():
            if not isinstance(binding_translation, ast.expr):
                raise UsageError("Binding translation must be an expression.")
        branch_translation = ctx.translate(branch)
        yield condition, binding_translations, branch_translation

def _compile_rule(rule_translation, rest):
    test, binding_translations, branch_translation = rule_translation

    if len(binding_translations) == 0:
        body = branch_translation
    else:
        body_lambda = util.astx.make_Lambda(
            binding_translations.iterkeys(),
            branch_translation)
        body = util.astx.make_simple_Call(
            body_lambda, 
            binding_translations.values())

    if len(rest) == 0:
        orelse = util.astx.expr_Raise_Exception_string("Match failure.")
    else:
        orelse = _compile_rule(rest[0], rest[1:])

    return ast.IfExp(
        test=test,
        body=body,
        orelse=orelse)
