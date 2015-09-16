"""typy: A programmable static type system as a Python library."""
import ast # Python standard library's abstract syntax module
import inspect # for accessing source code for functions
import textwrap # for stripping leading spaces

import cypy # helper functions
import six # Python 2-3 compatibility, e.g. metaclasses
# TODO: semver

class UsageError(Exception):
  pass 

class TypeError(Exception):
  def __init__(self, message, tree):
    Exception.__init__(message)
    self.tree = tree
  # TODO: error pretty-printing

class NotSupportedError(TypeError):
  def __init__(self, delegate, meth_category, meth_name, tree):
    self.delegate = delegate
    self.meth_category = meth_category
    self.meth_name = meth_name
    self.tree = tree
    # TODO: base constructor call

class TypeFormationError(Exception):
  pass

class _TypeMetaclass(type): # here, type is Python's "type" builtin
  def __getitem__(self, idx):
    if _contains_ellipsis(idx): return _construct_incty(self, idx)
    else: return _construct_ty(self, idx)

def _contains_ellipsis(idx):
  if idx is Ellipsis: return True
  elif isinstance(idx, tuple):
    for item in idx:
      if item is Ellipsis: return True
  return False 

def _construct_incty(tycon, inc_idx):
  tycon.validate_inc_idx(inc_idx)
  return IncompleteType(tycon, inc_idx)

def _construct_ty(tycon, idx):
  tycon.validate_idx(idx)
  return tycon(idx, True)

@six.add_metaclass(_TypeMetaclass)
class Type(object):
  """Base class for typy types.

  An typy type is an instance of typy.Type.
  An typy tycon is a subclass of typy.Type.
  """
  def __init__(self, idx, ok=False):
    if not ok:
      raise TypeFormationError(
        "Types should not be constructed directly. Use tycon[idx].")
    self.idx = idx

  @classmethod
  def validate_idx(cls, idx): pass

  @classmethod
  def validate_inc_idx(cls, inc_idx): pass

  def __eq__(self, other):
    return isinstance(other, Type) \
       and tycon(self) is tycon(other) \
       and self.idx == other.idx

  def __ne__(self, other):
    return not self.__eq__(other)

  def __call__(self, f):
    raise TypeError("Non-FnType used as a top-level function decorator.")

class IncompleteType(object):
  """Represents an incomplete type, used for literal forms.

  An incomplete type is constructed by providing an index 
  containing one or more ellipses (so the constructor need 
  not typically be called directly):
    tycon[a, ..., b]
  """
  def __init__(self, tycon, inc_idx):
    self.tycon = tycon
    self.inc_idx = inc_idx

  def __call__(self, f):
    if issubclass(self.tycon, FnType):
      (ast, static_env) = _reflect_func(f)
      return Fn(ast, static_env, self)
    else: raise TypeError("Incomplete non-FnType used as a top-level function decorator.")

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
  def __call__(self, f):
    (tree, static_env) = _reflect_func(f)
    return Fn(tree, static_env, self)

  # TODO: can you have a method and a class method w/ same name?
  @classmethod
  def init_ctx(cls, ctx): pass
  def init_ctx(self, ctx): pass 

  def ana_FunctionDef_TopLevel(self, ctx, tree, static_env):
    raise NotSupportedError(self, "method", "ana_FunctionDef_TopLevel", tree)

  @classmethod
  def syn_idx_FunctionDef_TopLevel(self, ctx, tree, static_env):
    raise NotSupportedError(self, "class method", "ana_FunctionDef_TopLevel", tree)

  # TODO: translation phase
  #########
  # The following stubs are pasted from the result of running _generate_FnType.py.
  ########

  @classmethod
  def check_FunctionDef(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_FunctionDef", tree)

  def check_FunctionDef(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_FunctionDef", tree)

  @classmethod
  def check_ClassDef(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_ClassDef", tree)

  def check_ClassDef(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_ClassDef", tree)

  @classmethod
  def check_Return(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Return", tree)

  def check_Return(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Return", tree)

  @classmethod
  def check_Delete(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Delete", tree)

  def check_Delete(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Delete", tree)

  @classmethod
  def check_Assign(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Assign", tree)

  def check_Assign(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Assign", tree)

  @classmethod
  def check_AugAssign(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_AugAssign", tree)

  def check_AugAssign(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_AugAssign", tree)

  @classmethod
  def check_Print(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Print", tree)

  def check_Print(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Print", tree)

  @classmethod
  def check_For(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_For", tree)

  def check_For(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_For", tree)

  @classmethod
  def check_While(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_While", tree)

  def check_While(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_While", tree)

  @classmethod
  def check_If(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_If", tree)

  def check_If(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_If", tree)

  @classmethod
  def check_With(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_With", tree)

  def check_With(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_With", tree)

  @classmethod
  def check_Raise(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Raise", tree)

  def check_Raise(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Raise", tree)

  @classmethod
  def check_TryExcept(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_TryExcept", tree)

  def check_TryExcept(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_TryExcept", tree)

  @classmethod
  def check_TryFinally(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_TryFinally", tree)

  def check_TryFinally(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_TryFinally", tree)

  @classmethod
  def check_Assert(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Assert", tree)

  def check_Assert(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Assert", tree)

  @classmethod
  def check_Import(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Import", tree)

  def check_Import(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Import", tree)

  @classmethod
  def check_ImportFrom(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_ImportFrom", tree)

  def check_ImportFrom(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_ImportFrom", tree)

  @classmethod
  def check_Exec(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Exec", tree)

  def check_Exec(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Exec", tree)

  @classmethod
  def check_Global(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Global", tree)

  def check_Global(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Global", tree)

  @classmethod
  def check_Expr(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Expr", tree)

  def check_Expr(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Expr", tree)

  @classmethod
  def check_Pass(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Pass", tree)

  def check_Pass(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Pass", tree)

  @classmethod
  def check_Break(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Break", tree)

  def check_Break(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Break", tree)

  @classmethod
  def check_Continue(cls, ctx, tree):
    raise NotSupportedError(cls, "class method", "check_Continue", tree)

  def check_Continue(self, ctx, tree):
    raise NotSupportedError(self, "method", "check_Continue", tree)

  ####### end autogenerated section ########

def _reflect_func(f):
  source = textwrap.dedent(inspect.getsource(f))
  tree = ast.parse(source).body[0] # ast.parse produces a Module initially
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
    self.tree = tree
    self.static_env = static_env
    self.ascription = ascription
    self.compiled = False 

  def compile(self):
    if self.compiled: return
    ctx = Context(self)
    tree, static_env, ascription = self.tree, self.static_env, self.ascription
    if isinstance(ascription, Type):
      delegate = ascription
      delegate.init_ctx(ctx)
      delegate.ana_FunctionDef_TopLevel(ctx, tree, static_env)
      ty = ascription
    else: # IncompleteType
      delegate = ascription.tycon
      delegate.init_ctx(ctx)
      idx = delegate.syn_idx_FunctionDef_TopLevel(ctx, tree, static_env)
      ty = _construct_ty(ascription, idx)
    tree.ty, tree.delegate = ty, delegate
    # TODO: translation
    self.compiled = True

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
    delegate = self.fn.delegate
    method = getattr(delegate, check_method)
    method(self, stmt)

  def ana(self, e, ty):
    pass # TODO

  def syn(self, e):
    pass # TODO

  def translate(self, tree):
    pass # TODO

