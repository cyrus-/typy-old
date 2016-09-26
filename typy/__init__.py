"typy"

#
# Errors
#

class TypyError(Exception):
    """Base class for typy errors."""
    pass

class UsageError(TypyError):
    """Raised by typy to indicate incorrect usage of the typy API."""
    def __init__(self, message):
        TypyError.__init__(self, message)

class TyError(TypyError):
    """Raised by fragments to indicate a type error."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

class TypeValidationError(TypyError):
    """Raised by fragments to indicate that a type index value
    cannot be computed."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

class ComponentFormationError(TypyError):
    """Raised to indicate that a component is malformed."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

#
# Program Components
#

import ast
import inspect
import textwrap

def component(f):
    """Decorator that transforms Python function definitions into Components."""
    (tree, static_env) = _reflect_func(f)
    c = Component(tree, static_env)
    c._evaluate()
    return c

def _reflect_func(f):
    """Returns the ast and StaticEnv of Python function f."""
    source = textwrap.dedent(inspect.getsource(f))
    tree = ast.parse(source).body[0]
    static_env = StaticEnv.from_func(f)
    return (tree, static_env)

class Component(object):
    """Top-level components."""
    def __init__(self, tree, static_env):
        """Called by component."""
        self.tree = tree
        self.static_env = static_env
        self._parsed = False
        self._checked = False
        self._evaluated = False

    def _parse(self):
        if self._parsed: return

        tree = self.tree

        # make sure there are no arguments
        args = tree.args
        if (len(args.args) != 0 or 
              args.vararg is not None or 
              len(args.kwonlyargs) != 0 or 
              args.kwarg is not None):
            raise ComponentFormationError(
                "Components cannot take arguments.", tree)

        # parse the members
        def _parse_members(body):
            for stmt in body:
                if isinstance(stmt, ast.Assign):
                    targets = stmt.targets
                    value = stmt.value
                    if len(targets) != 1:
                        raise ComponentFormationError(
                            "Too many assignment targets.", stmt)
                    target = targets[0]
                    name, ann = self._process_target(target)
                    k_ann = Kind.parse_kind(ann)
                    if k_ann is not None:
                        yield TypeMember(name, k_ann, value)
                    else:
                        ty_ann = TyExpr.parse_ty_expr(ann)
                        yield ValueMember(name, ty_ann, value)
                else:
                    yield StmtMember(stmt)
        self._members = tuple(_parse_members(tree.body))
        # TODO exports

        self._parsed = True

    @classmethod
    def _process_target(cls, target):
        if isinstance(target, ast.Name):
            return target.id, None
        elif isinstance(target, ast.Subscript):
            result = _parse_ascription(target)
            if result is None:
                raise ComponentFormationError("Invalid member signature", target)
            else:
                value, asc = result
                if isinstance(value, ast.Name):
                    return value.id, asc
                else:
                    raise ComponentFormationError("Invalid member name", target)
        else:
            raise ComponentFormationError("Invalid member", target)

    def _typecheck_and_translate(self):
        """Called by component."""
        self._parse()

    def _evaluate(self):
        """Called by component."""
        self._typecheck_and_translate()

def _parse_ascription(expr):
    if isinstance(expr, ast.Subscript):
        value, slice = expr.value, expr.slice
        if isinstance(slice, ast.Slice):
            lower, upper, step = slice.lower, slice.upper, slice.step
            if lower is None and upper is not None and step is None:
                return value, upper
    return None

class ComponentMember(object):
    """Base class for top-level component members."""

class ValueMember(object):
    """Value members."""
    def __init__(self, name, ty_ann, expr):
        self.name = name
        self.ty_ann = ty_ann
        self.expr = expr

class TypeMember(object):
    """Type members."""
    def __init__(self, name, k_ann, ty_expr):
        self.name = name
        self.k_ann = k_ann
        self.ty_expr = ty_expr

class StmtMember(object):
    """Expression members (not exported)."""
    def __init__(self, stmt):
        self.expr = expr

#
# Static Environments
#

import ast

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
        closure = cls._func_closure(f)
        try:
            globals = f.func_globals
        except AttributeError:
            globals = f.__globals__
        return cls(closure, globals)

    @classmethod
    def _func_closure(cls, f):
        try:
            closure = f.func_closure
        except AttributeError:
            closure = f.__closure__
        if closure is None:
            return {}
        else:
            return dict(cls._get_cell_contents(f.func_code.co_freevars, closure))

    @classmethod
    def _get_cell_contents(cls, co_freevars, closure):
        for x, c in zip(co_freevars, closure):
            try:
                yield x, c.cell_contents
            except ValueError:
                continue

    def eval_expr_ast(self, tree):
        tree = ast.Expression(tree)
        code = compile(tree, "<eval_expr_ast>", "eval")
        return eval(code, self.globals, self.closure)

#
# Semantic Fragments
#

class Fragment(object):
    def __init__(self):
        raise NotImplementedError()

#
# Type Expressions
#

class TyExpr(object):
    @classmethod
    def parse_ty_expr(cls, expr):
        if isinstance(expr, ast.Name):
            return NameTyExpr(expr)
        elif isinstance(expr, ast.Subscript):
            return CanonicalType(expr.target, expr.slice)
        else:
            return None

class CanonicalTyExpr(TyExpr):
    def __init__(self, fragment_ast, idx_ast):
        self.fragment_ast = fragment_ast
        self.idx_ast = idx_ast

class NameTyExpr(TyExpr):
    def __init__(self, name_ast):
        self.name_ast = name_ast
        self.id = name_ast.id

class Kind(object):
    @classmethod
    def parse_kind(cls, expr):
        if isinstance(expr, ast.Name) and expr.id == "type":
            return TypeKind
        else:
            return None

class TypeKind(Kind):
    def __init__(self):
        Kind.__init__(self)
TypeKind = TypeKind()

#
# Contexts
#

class Context(object):
    def ana(self, e, ty):
        raise NotImplementedError()

    def syn(self, e):
        raise NotImplementedError()

    def check(self, stmt):
        raise NotImplementedError()

    def ana_pat(self, pat, ty):
        raise NotImplementedError()

    def trans(self, e):
        raise NotImplementedError()


