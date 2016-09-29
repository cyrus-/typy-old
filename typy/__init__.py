"typy"

#
# Errors
#

class TypyError(Exception):
    """Base class for typy errors."""
    pass

class InternalError(TypyError):
    """Raised when an internal invariant has been violated."""
    def __init__(self, message):
        TypyError.__init__(self, message)

class UsageError(TypyError):
    """Raised by typy to indicate incorrect usage of the typy API."""
    def __init__(self, message):
        TypyError.__init__(self, message)

class TyError(TypyError):
    """Raised by fragments to indicate a type error."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

class KindError(TypyError):
    """Raised by typy or fragments to indicate a kind error."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

class TypeValidationError(KindError):
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

class FragmentError(TypyError):
    """Raised to indicate a problem with a fragment definition."""
    def __init__(self, message, fragment):
        TypyError.__init__(self, message)
        self.fragment = fragment

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
        self._translated = False
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
        def _parse_members():
            body = tree.body
            for stmt in body:
                if isinstance(stmt, ast.Assign):
                    targets, value = stmt.targets, stmt.value
                    if len(targets) != 1:
                        raise ComponentFormationError(
                            "Too many assignment targets.", stmt)
                    name, asc = _process_target(targets[0])
                    k_asc = Kind.parse(asc)
                    if k_asc is not None:
                        # TODO test this branch
                        ucon = UCon.parse(value)
                        yield TypeMember(name, k_asc, ucon)
                    else:
                        uty = UCon.parse(asc)
                        yield ValueMember(name, uty, value)
                else:
                    yield StmtMember(stmt)

        def _process_target(target):
            if isinstance(target, ast.Name):
                return target, None
            elif isinstance(target, ast.Subscript):
                result = _parse_ascription(target)
                if result is None:
                    raise ComponentFormationError(
                        "Invalid member signature", target)
                else:
                    value, asc = result
                    if isinstance(value, ast.Name):
                        return value, asc
                    else:
                        raise ComponentFormationError(
                            "Invalid member name", target)
            else:
                raise ComponentFormationError("Invalid member", target)

        self._members = _members = tuple(_parse_members())
        
        # determine the exports
        def _determine_exports():
            for member in _members:
                if not isinstance(member, StmtMember):
                    yield (member.name.id, member)
        self._exports = dict(_determine_exports())

        self._parsed = True

    def _check(self):
        if self._checked: return
        self._parse()
        ctx = self.ctx = Context(self.static_env)
        for member in self._members:
            member.check(ctx)
        self._checked = True

    def _translate(self):
        if self._translated: return
        self._check()
        for member in self._members:
            member.translate(self.ctx)
        self._translated = True

    def _evaluate(self):
        if self._evaluated: return
        self._translate()
        # TODO generate a single object?
        for member in self._members:
            member.evaluate(self.ctx)
        self._evaluated = True

def _parse_ascription(expr):
    if isinstance(expr, ast.Subscript):
        value, slice = expr.value, expr.slice
        if isinstance(slice, ast.Slice):
            lower, upper, step = slice.lower, slice.upper, slice.step
            if lower is None and upper is not None and step is None:
                return value, upper
    return None

class ComponentMember(object):
    """Base class for component members."""

class ValueMember(ComponentMember):
    """Value members."""
    def __init__(self, name, uty, expr):
        self.name = name
        self.uty = uty
        self.expr = expr

    def check(self, ctx):
        uty = self.uty
        if uty is None:
            # TODO test this branch
            self.ty = ty = ctx.syn(self.expr)
        else:
            self.ty = ty = ctx.ana_ucon(uty, TypeKind)
            ctx.ana(self.expr, ty)
            self.ty = ty

    def translate(self, ctx):
        ctx.trans(self.expr)

    def evaluate(self, ctx):
        self.value = ctx.static_env.eval_expr_ast(self.expr.translation)

class TypeMember(ComponentMember):
    """Type members."""
    def __init__(self, name, k_asc, ucon):
        self.name = name
        self.k_asc = k_asc
        self.ucon = ucon

    def check(self, ctx):
        ty = self.ty = ctx.ana_ucon(self.ucon, self.k_asc)
        ctx.push_ucon_binding(self.name, SingletonKind(ty))

    def translate(self, ctx): 
        pass

    def evaluate(self, ctx):
        pass

class StmtMember(ComponentMember):
    """Statement members (not exported)."""
    def __init__(self, stmt):
        self.expr = expr

    def check(self, ctx):
        raise NotImplementedError()

    def translate(self, ctx):
        raise NotImplementedError()

    def evaluate(self, ctx):
        raise NotImplementedError()

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

    def __contains__(self, item):
        return item in self.closure or item in self.globals

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
# Type Constructions
#

import ast

class UCon(object):
    @classmethod
    def parse(cls, expr):
        if isinstance(expr, ast.Name):
            return UName(expr)
        elif isinstance(expr, ast.Subscript):
            return UCanonicalTy(expr.value, expr.slice)
        else:
            return None

class UCanonicalTy(UCon):
    def __init__(self, fragment_ast, idx_ast):
        self.fragment_ast = fragment_ast
        self.idx_ast = idx_ast

class UName(UCon):
    def __init__(self, name_ast):
        self.name_ast = name_ast
        self.id = name_ast.id

class Con(object):
    pass

class CanonicalTy(Con):
    def __init__(self, fragment, idx):
        self.fragment = fragment
        self.idx = idx

    @classmethod
    def new(cls, ctx, fragment, idx_ast):
        return cls(fragment, fragment.init_idx(ctx, idx_ast))

class ConVar(Con):
    def __init__(self, ctx, name_ast, uniq_id):
        self.name_ast = name_ast
        self.uniq_id = uniq_id

class Kind(object):
    @classmethod
    def parse(cls, expr):
        if isinstance(expr, ast.Name) and expr.id == "type":
            return TypeKind
        else:
            return None

class TypeKind(Kind):
    def __init__(self):
        Kind.__init__(self)

    def __repr__(self):
        return "type"

    def __str__(self):
        return "type"
TypeKind = TypeKind()

class SingletonKind(Kind):
    def __init__(self, ty):
        self.ty = ty

#
# Contexts
#

import ast
import typy.util.astx as _astx

class Context(object):
    def __init__(self, static_env):
        self.static_env = static_env
        self.ty_ids = { } # map from id to ConVar
        self.ty_vars = { } # map from uniq_id to kind 
        self.exp_ids = { } # map from id to uniq_id
        self.exp_vars = { } # map from uniq_id to ty
        self.last_ty_var = 0
        self.last_exp_var = 0

    def push_ucon_binding(self, name_ast, k):
        uniq_id = self.last_ty_var
        self.ty_ids[name_ast.id] = ConVar(self, name_ast, uniq_id)
        self.ty_vars[uniq_id] = k
        uniq_id += 1

    def is_kind(self, k):
        if k == TypeKind: return True
        elif isinstance(k, SingletonKind):
            self.ana(k.ty, TypeKind)
            return True
        else:
            raise UsageError("Invalid kind")
    
    def kind_eq(self, k1, k2):
        if k1 is k2:
            return True
        elif isinstance(k1, SingletonKind) and isinstance(k2, SingletonKind):
            return self.con_eq(k1.ty, k2.ty, TypeKind)
        else:
            return False

    def subkind(self, k1, k2):
        if self.kind_eq(k1, k2): 
            return True
        elif isinstance(k1, SingletonKind) and k2 == TypeKind:
            return True
        else:
            return False

    def syn_con(self, c):
        if isinstance(c, ConVar):
            uniq_id = c.uniq_id
            try:
                return self.ty_vars[uniq_id]
            except KeyError:
                raise KindError("Unbound type variable: " + c.name_ast.id,
                                c)
        elif isinstance(c, CanonicalTy):
            return SingletonKind(c)
        else:
            raise UsageError("Invalid kind.")

    def ana_con(self, c, k):
        syn_k = self.syn_con(c)
        if self.subkind(syn_k, k): return
        else:
            raise KindError(
                "Kind mismatch. Expected: '" + str(k) + "'. Got: '" + str(syn_k) + "'.",
                c)

    def con_eq(self, c1, c2, k):
        if c1 == c2:
            return self.ana_con(c1, k)
        elif k == TypeKind:
            k1 = self.syn_con(c1)
            if isinstance(k1, SingletonKind):
                k2 = self.syn_con(c2)
                if isinstance(k2, SingletonKind):
                    return self.con_eq(k1.ty, k2.ty, k)
                else:
                    return self.con_eq(c2, k1.ty, k)
            elif isinstance(k2, SingletonKind):
                return self.con_eq(c1, k2.ty, k)
            if isinstance(c1, CanonicalTy):
                if isinstance(c2, CanonicalTy):
                    return (c1.fragment == c2.fragment 
                            and c1.fragment.idx_eq(self, c1.idx, c2.idx))
                else:
                    return False
            else:
                return False
        elif isinstance(k, SingletonKind):
            try:
                return self.ana_con(c1, k) and self.ana_con(c2, k)
            except KindError:
                return False

    def canonicalize(self, ty):
        if isinstance(ty, CanonicalTy): return ty
        elif isinstance(ty, ConVar):
            k = self.syn_con(ty)
            if k == TypeKind:
                return ty
            elif isinstance(k, SingletonKind):
                return self.canonicalize(k.ty)
            else:
                raise UsageError("Invalid kind.")
        else:
            raise UsageError("Invalid construction.")

    def syn_ucon(self, ucon):
        raise NotImplementedError()

    def ana_ucon(self, ucon, k):
        if isinstance(ucon, UName):
            id = ucon.id
            print(id)
            static_env = self.static_env
            ty_ids = self.ty_ids
            if id in ty_ids:
                convar = ty_ids[id]
                self.ana_con(convar, k)
                return convar
            elif id in static_env:
                static_val = self.static_env[id]
                if issubclass(static_val, Fragment):
                    ty = CanonicalTy.new(self, static_val, 
                                         _astx.empty_tuple_ast)
                    self.ana_con(ty, k)
                    return ty
                else:
                    raise KindError(
                        "Type expression '" + 
                        id + 
                        "' is bound to static value '" + 
                        repr(static_val) + 
                        "', which is neither a fragment nor a " +
                        "type expression.", ucon)
            else:
                raise KindError(
                    "Type expression '" + 
                    id + 
                    "' is unbound.", ucon)
        elif isinstance(ucon, UCanonicalTy):
            fragment_ast = ucon.fragment_ast
            idx_ast = ucon.idx_ast
            static_env = self.static_env
            fragment = static_env.eval_expr_ast(fragment_ast)
            if issubclass(fragment, Fragment):
                ty = CanonicalTy.new(self, fragment, idx_ast)
                self.ana_con(ty, k)
                return ty
            else:
                raise KindError(
                    "Term did not evaluate to a fragment in static environment.",
                    fragment_ast)
        else:
            raise KindError(
                "Invalid type expression: " + repr(ucon), ucon)

    def as_type(self, expr):
        ucon = UCon.parse(expr)
        return self.ana_ucon(ucon, TypeKind)

    def ana(self, e, ty):
        if _is_intro_form(e):
            canonical_ty = self.canonicalize(ty)
            if canonical_ty is None:
                raise TyError(
                    "Cannot analyze an intro form against a non-canonical type.",
                    e)
            e.is_intro_form = True
            classname = e.__class__.__name__
            ana_method_name = "ana_" + classname
            fragment = canonical_ty.fragment
            idx = canonical_ty.idx
            ana_method = getattr(fragment, ana_method_name)
            ana_method(self, e, idx)
            e.ty = canonical_ty
            e.delegate = fragment
            e.delegate_idx = idx
            e.translation_method_name = "trans_" + classname
        else:
            raise NotImplementedError()

    def syn(self, e):
        raise NotImplementedError()

    def check(self, stmt):
        raise NotImplementedError()

    def ana_pat(self, pat, ty):
        raise NotImplementedError()

    def trans(self, e):
        fragment = e.delegate
        idx = e.delegate_idx
        translation_method_name = e.translation_method_name
        translation_method = getattr(fragment, translation_method_name)
        translation = e.translation = translation_method(self, e, idx)
        return translation

_intro_forms = (
    ast.FunctionDef, # the only stmt intro form
    ast.Lambda, 
    ast.Dict, 
    ast.Set, 
    ast.Num, 
    ast.Str, 
    ast.Bytes,
    ast.NameConstant,
    ast.List, 
    ast.Tuple)
def _is_intro_form(e):
    return isinstance(e, _intro_forms) 

#
# Semantic Fragments
#

class Fragment(object):
    def __init__(self):
        raise NotImplementedError()

    @classmethod
    def init_idx(cls, ctx, idx_ast):
        raise FragmentError("Does not implement init_idx.", cls)

    @classmethod
    def idx_eq(cls, ctx, idx1, idx2):
        return idx1 == idx2

    # intro forms
    @classmethod
    def ana_FunctionDef(cls, ctx, stmt, idx):
        raise TyError("Does not support def literals.", cls)

    @classmethod
    def trans_FunctionDef(cls, ctx, stmt, idx):
        raise FragmentError("Missing translation method: trans_FunctionDef.", cls)

    @classmethod
    def ana_Lambda(cls, ctx, e, idx):
        raise TyError("Does not support lambda literals.", cls)

    @classmethod
    def trans_Lambda(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Lambda.", cls)

    @classmethod
    def ana_Dict(cls, ctx, e, idx):
        raise TyError("Does not support dictionary literals.", cls)

    @classmethod
    def trans_Dict(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Dict.", cls)

    @classmethod
    def ana_Set(cls, ctx, e, idx):
        raise TyError("Does not support set literals.", cls)

    @classmethod
    def trans_Set(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Set.", cls)

    @classmethod
    def ana_Num(cls, ctx, e, idx):
        raise TyError("Does not support number literals.", cls)

    @classmethod
    def trans_Num(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Num.", cls)

    @classmethod
    def ana_Str(cls, ctx, e, idx):
        raise TyError("Does not support string literals.", cls)

    @classmethod
    def trans_Str(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Str.", cls)

    @classmethod # TODO what are these
    def ana_Bytes(cls, ctx, e, idx):
        raise TyError("Does not support byte literals.", cls)

    @classmethod
    def trans_Bytes(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Bytes.", cls)

    @classmethod # TODO what are these
    def ana_NameConstant(cls, ctx, e, idx):
        raise TyError("Does not support name constant literals.", cls)

    @classmethod
    def trans_NameConstant(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_NameConstant.", cls)

    @classmethod
    def ana_List(cls, ctx, e, idx):
        raise TyError("Does not support list literals.", cls)
    
    @classmethod
    def trans_List(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_List.", cls)

    @classmethod
    def ana_Tuple(cls, ctx, e, idx):
        raise TyError("Does not support tuple literals.", cls)
    
    @classmethod
    def trans_Tuple(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Tuple.", cls)

