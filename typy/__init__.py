"""typy: A programmable static type system as a Python library."""
import ast # Python standard library's abstract syntax module
import inspect # for accessing source code for functions
import textwrap # for stripping leading spaces

import six # Python 2-3 compatibility, e.g. metaclasses
# TODO: semver
# TODO: fix indentation

class UsageError(Exception):
    pass 

class TypeError(Exception):
    def __init__(self, message, tree):
        Exception.__init__(self, message)
        self.tree = tree
    # TODO: error pretty-printing

class TypeMismatchError(TypeError):
    def __init__(self, expected, got, tree):
        TypeError.__init__(self, 
            "Type mismatch. Expected: {0}. Got: {1}.".format(expected, got), 
            tree)
        self.expected = expected
        self.got = got

class NotSupportedError(TypeError):
    def __init__(self, delegate, meth_category, meth_name, tree):
        self.delegate = delegate
        self.meth_category = meth_category
        self.meth_name = meth_name
        self.tree = tree
        # TODO: base constructor call

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
        if _contains_ellipsis(idx): return _construct_incty(self, idx)
        else: return _construct_ty(self, idx)

def _contains_ellipsis(idx):
    if idx is Ellipsis: return True
    elif isinstance(idx, tuple):
        for item in idx:
            if item is Ellipsis: return True
    else: return False 

def _construct_incty(tycon, inc_idx):
    inc_idx = tycon.init_inc_idx(inc_idx)
    return IncompleteType(tycon, inc_idx, from_construct_incty=True)

def _construct_ty(tycon, idx):
    idx = tycon.init_idx(idx)
    return tycon(idx, from_construct_ty=True)

@six.add_metaclass(_TypeMetaclass)
class Type(object):
    """Base class for typy types.

    An typy type is an instance of typy.Type.
    An typy tycon is a subclass of typy.Type.
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

    @classmethod
    def init_idx(cls, idx): 
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        return inc_idx

    def ana_Tuple(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Tuple", e)

    @classmethod
    def syn_idx_Tuple(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_Tuple", e)

    def translate_Tuple(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Tuple", e)

    def ana_Name_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", "ana_Name_constructor", e)

    @classmethod
    def syn_idx_Name_constructor(self, ctx, e, inc_idx):
        raise NotSupportedError(self, "class method", "syn_idx_Name_constructor", e)

    def translate_Name_constructor(self, ctx, e):
        raise NotSupportedError(self, "method", "translate_Name_constructor", e)

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
        else: raise TypeError("Incomplete non-FnType used as a top-level function decorator.")

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
    def init_ctx(cls, ctx): pass

    @classmethod
    def preprocess_FunctionDef_toplevel(cls, fn, tree):
        pass 

    def ana_FunctionDef_toplevel(self, ctx, tree, ty):
        raise NotSupportedError(self, "method", "ana_FunctionDef_toplevel", tree)

    @classmethod
    def syn_idx_FunctionDef_toplevel(self, ctx, tree, inc_ty):
        raise NotSupportedError(self, "class method", "ana_FunctionDef_toplevel", tree)

    def translate_FunctionDef_toplevel(self, ctx, tree):
        raise NotSupportedError(self, "method", "translate_FunctionDef_toplevel", tree)

    @classmethod 
    def syn_Name(self, ctx, e):
        raise NotSupportedError(self, "class method", "syn_Name", e)

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
        try: return self.closure[item]
        except KeyError: return self.globals[item]

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
    if closure is None: return {}
    else: return dict(zip(f.func_code.co_freevars, (c.cell_contents for c in closure)))

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
        if self.typechecked: return
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
        if self.compiled: return
        tree, ascription, ctx = self.tree, self.ascription, self.ctx
        ty = tree.ty
        translation = ty.translate_FunctionDef_toplevel(ctx, tree)
        self.translation = translation
        self.compiled = True
        return translation

    def __call__(self, *args):
        # TODO: implement thisv
        raise NotImplemented()

class Context(object):
    def __init__(self, fn):
        self.fn = fn
        self.data = { }

    def check(self, stmt):
        # TODO: compare against py3 grammar
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
            if classname == "Name" and e.id[0].isupper():
                classname = "Name_constructor"
            ana_method = 'ana_%s' % classname
            method = getattr(ty, ana_method)
            method(self, e)
            e.ty = ty
            e.delegate = ty
            print "SETTING TMN TO ", classname
            e.translation_method_name = 'translate_%s' % classname
        else:
            syn_ty = self.syn(e)
            if ty != syn_ty:
                raise TypeMismatchError(ty, syn_ty, e)

    def syn(self, e):
        if isinstance(e, ast.Subscript):
            value, slice_ = e.value, e.slice 
            ty = _process_ascription_slice(slice_, self.fn.static_env)
            if isinstance(ty, Type):
                self.ana(value, ty)
                e.ty = ty
                e.delegate = value.delegate
                e.is_ascription = True 
                return ty
            elif isinstance(ty, IncompleteType):
                if _is_intro_form(value):
                    classname = value.__class__.__name__
                    if classname == "Name":
                        classname = "Name_constructor"
                    syn_idx_methodname = 'syn_idx_%s' % classname
                    delegate = ty.tycon
                    method = getattr(delegate, syn_idx_methodname)
                    syn_idx = method(self, value, ty.inc_idx)
                    ty = _construct_ty(delegate, syn_idx)
                    e.delegate, e.ty = delegate, ty
                    e.is_ascription = True 
                    value.translation_method_name = "translate_%s" % classname
                    value.delegate, value.ty = delegate, ty
                    return ty
                else:
                    raise TypeError(
                        "Incomplete type ascriptions can only appear on introductory forms.", 
                        value)
            else:
                # not an ascription
                value_ty = self.syn(value)
                ty = value_ty.syn_Subscript(self, e)
                e.delegate, e.ty = value_ty, ty
                e.translation_method_name = 'translate_Subscript'
                return ty
        elif isinstance(e, ast.Name):
            id = e.id
            delegate = tycon(self.fn.ascription)
            ty = delegate.syn_Name(self, e)
            if isinstance(ty, Type):
                e.delegate, e.ty = delegate, ty
                e.translation_method_name = 'translate_Name'
                return ty
            else:
                raise typy.TypeInvariantError(
                    "syn_Name did not return a type.", e)
        else:
            raise TypeError("Unsupported form", e)

    def translate(self, tree):
        if isinstance(tree, ast.stmt):
            classname = tree.__class__.__name__
            method_name = 'translate_' + classname
            delegate = self.fn.tree.ty
            method = getattr(delegate, method_name)
            return method(self, tree)
        elif isinstance(tree, ast.expr):
            if hasattr(tree, "is_ascription"):
                return self.translate(tree.value)
            elif isinstance(tree, ast.Name):
                delegate = self.fn.tree.ty
                return delegate.translate_Name(self, tree)
            else:
                method_name = tree.translation_method_name
                delegate = tree.ty
                method = getattr(delegate, method_name)
                return method(self, tree)
        else:
            raise NotImplementedError("cannot translate this...")

_intro_forms = (ast.Lambda, ast.Dict, ast.Set, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.Num, ast.Str, ast.List, ast.Tuple)
def _is_intro_form(e):
    return isinstance(e, _intro_forms) \
                 or (isinstance(e, ast.Name) and e.id[0].isupper())

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
