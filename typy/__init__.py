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

class TypeFormationError(TypyError):
    """Raised by typy to indicate that a type construction is malformed."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

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

from .util import astx as _astx

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
        if not _astx.is_empty_args(tree.args):
            raise ComponentFormationError(
                "Components cannot take arguments.", tree)

        # parse the members
        def _parse_members():
            body = tree.body
            for stmt in body:
                if isinstance(stmt, ast.Assign):
                    type_member = TypeMember.parse_Assign(stmt)
                    if type_member is not None: yield type_member
                    else:
                        value_member = ValueMember.parse_Assign(stmt)
                        if value_member is not None: yield value_member
                        else: 
                            raise ComponentFormationError(
                                "Invalid member definition.", stmt)
                elif isinstance(stmt, ast.FunctionDef):
                    value_member = ValueMember.parse_FunctionDef(stmt)
                    if value_member is not None: yield value_member
                    else:
                        raise ComponentFormationError(
                            "Invalid member definition.", stmt)
                # TODO AsyncFunctionDef?
                # TODO ClassDef?
                else:
                    yield StmtMember(stmt)
        self._members = members = tuple(_parse_members())

        # determine exports
        # TODO separate type and value exports?
        exports = self._exports = { }
        for member in members:
            if isinstance(member, (ValueMember, TypeMember)):
                lbl = member.id
                if lbl in exports:
                    raise ComponentFormationError(
                        "Duplicate label: " + lbl, member.tree)
                exports[lbl] = member

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
        _members = self._members
        body = [ ]
        for member in self._members:
            translation = member.translate(self.ctx)
            body.extend(translation)
        self._translation = ast.Module(
            body=body)
        self._translated = True

    def _evaluate(self):
        if self._evaluated: return
        self._translate()
        _translation = self._translation
        self._module = self.static_env.eval_module_ast(_translation)
        self._evaluated = True

    def kind_of(self, lbl):
        exports = self._exports
        if lbl in exports:
            member = exports[lbl]
            if isinstance(member, TypeMember):
                return member.kind

def is_component(x):
    return isinstance(x, Component)

class ComponentMember(object):
    """Base class for component members."""

class TypeMember(ComponentMember):
    """Type members."""
    def __init__(self, id, name_ast, uty_expr, tree):
        self.id = id
        self.name_ast = name_ast
        self.uty_expr = uty_expr
        self.tree = tree

    @classmethod
    def parse_Assign(cls, stmt):
        targets, value = stmt.targets, stmt.value
        if len(targets) != 1:
            raise ComponentFormationError(
                "Too many assignment targets.", stmt)
        target = targets[0]
        if isinstance(target, ast.Subscript):
            target_value = target.value
            if isinstance(target_value, ast.Name):
                slice = target.slice
                if isinstance(slice, ast.Index):
                    slice_value = slice.value
                    if isinstance(slice_value, ast.Name):
                        if slice_value.id == "type":
                            uty_expr = UTyExpr.parse(value)
                            return cls(target_value.id, 
                                       target_value, uty_expr, stmt)

    def check(self, ctx):
        ty = self.ty = ctx.ana_uty_expr(self.uty_expr, TypeKind)
        kind = self.kind = SingletonKind(ctx.canonicalize(ty))
        ctx.push_uty_expr_binding(self.name_ast, kind)

    def translate(self, ctx): 
        return []

class ValueMember(ComponentMember):
    """Value members."""
    def __init__(self, id, uty, tree):
        self.id = id
        self.uty = uty
        self.tree = tree

    @classmethod
    def parse_Assign(cls, stmt):
        targets, value = stmt.targets, stmt.value
        if len(targets) != 1:
            raise ComponentFormationError(
                "Too many assignment targets.", stmt)
        target = targets[0]
        if isinstance(target, ast.Subscript):
            target_value = target.value
            if isinstance(target_value, ast.Name):
                slice = target.slice
                if isinstance(slice, ast.Slice):
                    lower, upper, step = slice.lower, slice.upper, slice.step
                    if lower is None and upper is not None and step is None:
                        uty = UTyExpr.parse(upper)
                        return cls(target_value.id, uty, stmt)
        elif isinstance(target, ast.Name):
            return cls(target.id, None, stmt)

    @classmethod
    def parse_FunctionDef(cls, stmt):
        return cls(stmt.name, None, stmt)

    def check(self, ctx):
        uty = self.uty
        tree = self.tree
        if isinstance(tree, ast.Assign):
            value = tree.value
            if uty is None:
                ty = ctx.syn(value)
            else:
                ty = ctx.ana_uty_expr(uty, TypeKind)
                ctx.ana(value, ty)
        elif isinstance(tree, ast.FunctionDef):
            if uty is None:
                ty = ctx.syn(tree)
            else:
                ty = ctx.ana_uty_expr(uty, TypeKind)
                ctx.ana(tree, ty)
        else:
            raise InternalError("Invalid form.")
        ctx.add_id_var_binding(self.id, self.id, ty)
        self.ty = ctx.canonicalize(ty)

    def translate(self, ctx):
        tree = self.tree
        if isinstance(tree, ast.Assign):
            target = ast.copy_location(ast.Name(id=self.id, ctx=ast.Store()), tree)
            assignment = ast.copy_location(ast.Assign(
                targets=[target],
                value=ctx.trans(tree.value)), tree)
            translation = self.translation = (assignment,)
            return translation
        elif isinstance(tree, ast.FunctionDef):
            return ctx.trans_FunctionDef(tree, self.id)

class StmtMember(ComponentMember):
    """Statement members (not exported)."""
    def __init__(self, stmt):
        self.stmt = stmt

    def check(self, ctx):
        raise NotImplementedError()

    def translate(self, ctx):
        raise NotImplementedError()

#
# Static Environments
#

import ast
import types

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
            try:
                code = f.func_code
            except AttributeError:
                code = f.__code__
            return dict(cls._get_cell_contents(code.co_freevars, closure))

    @classmethod
    def _get_cell_contents(cls, co_freevars, closure):
        for x, c in zip(co_freevars, closure):
            try:
                yield x, c.cell_contents
            except ValueError:
                continue

    def eval_expr_ast(self, expr):
        expr = ast.Expression(expr)
        code = compile(expr, "<eval_expr_ast>", "eval")
        return eval(code, self.globals, self.closure)

    def eval_module_ast(self, module_ast):
        # print(astunparse.unparse(module_ast))
        code = compile(module_ast, "<eval_module_ast>", "exec")
        _module = types.ModuleType("TestModule", "Module test") # TODO properly name them
        _module_dict = _module.__dict__
        _module_dict.update(self.globals)
        _module_dict.update(self.closure)
        exec(code, _module_dict)
        return _module

import astunparse

#
# Type Expressions
#

import ast

class UTyExpr(object):
    @classmethod
    def parse(cls, expr):
        if isinstance(expr, ast.Name):
            return UName(expr)
        elif isinstance(expr, ast.Subscript):
            return UCanonicalTy(expr.value, expr.slice)
        elif isinstance(expr, ast.Attribute):
            return UProjection(expr.value, expr.attr)
        else:
            raise TypeFormationError("Malformed type.", expr)

class UCanonicalTy(UTyExpr):
    def __init__(self, fragment_ast, idx_ast):
        self.fragment_ast = fragment_ast
        self.idx_ast = idx_ast

class UName(UTyExpr):
    def __init__(self, name_ast):
        self.name_ast = name_ast
        self.id = name_ast.id

class UProjection(UTyExpr):
    def __init__(self, path_ast, lbl):
        self.path_ast = path_ast
        self.lbl = lbl

class TyExpr(object):
    pass

class CanonicalTy(TyExpr):
    def __init__(self, fragment, idx):
        self.fragment = fragment
        self.idx = idx

    @classmethod
    def new(cls, ctx, fragment, idx_ast):
        return cls(fragment, fragment.init_idx(ctx, idx_ast))

    def __str__(self):
        return self.fragment.__name__ + "[" + str(self.idx) + "]"

    def __repr__(self):
        return self.__str__()

class TyExprVar(TyExpr):
    def __init__(self, ctx, name_ast, uniq_id):
        self.ctx = ctx
        self.name_ast = name_ast
        self.uniq_id = uniq_id

    def __eq__(self, other):
        if isinstance(other, TyExprVar):
            return self.ctx == other.ctx and self.uniq_id == other.uniq_id
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class TyExprPrj(TyExpr):
    def __init__(self, path_ast, path_val, lbl):
        self.path_ast = path_ast
        self.path_val = path_val
        self.lbl = lbl

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
import typy.util as _util
import typy.util.astx as _astx

class Context(object):
    def __init__(self, static_env):
        self.static_env = static_env
        self.default_fragments = []

        # stack of maps from id to TyExprVar
        self.ty_ids = _util.DictStack([{}])         
        # stack of maps from uniq_id to kind 
        self.ty_vars = _util.DictStack([{}]) 
        # stack of maps from id to uniq_id
        self.exp_ids = _util.DictStack([{}]) 
        # map from uniq_id to ty
        self.exp_vars = _util.DictStack([{}]) 
        self.last_ty_var = 0
        self.last_exp_var = 0

    def push_uty_expr_binding(self, name_ast, k):
        uniq_id = "_ty_" + name_ast.id + "_" + str(self.last_ty_var)
        self.ty_ids[name_ast.id] = TyExprVar(self, name_ast, uniq_id)
        self.ty_vars[uniq_id] = k
        self.last_ty_var += 1

    def push_var_bindings(self, bindings):
        self.exp_ids.push({ })
        self.exp_vars.push({ })
        return self.add_bindings(bindings)

    def pop_var_bindings(self):
        self.exp_ids.pop()
        self.exp_vars.pop()

    def add_binding(self, name_ast, ty):
        uniq_id = "_" + name_ast.id + "_" + str(self.last_exp_var)
        self.exp_ids[name_ast.id] = uniq_id
        self.exp_vars[uniq_id] = ty
        self.last_exp_var += 1
        return (uniq_id, ty)

    def add_bindings(self, bindings):
        r = { }
        for (name_ast, ty) in bindings.items():
            uniq_id, ty = self.add_binding(name_ast, ty)
            r[name_ast.id] = (uniq_id, ty)
        return r

    def add_id_var_binding(self, id, var, ty):
        self.exp_ids[id] = var
        self.exp_vars[var] = ty

    def lookup_exp_var_by_id(self, id):
        uniq_id = self.exp_ids[id]
        return uniq_id, self.exp_vars[uniq_id]

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
        elif (isinstance(k1, SingletonKind) 
              and isinstance(k2, SingletonKind)):
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

    def syn_ty_expr(self, c):
        if isinstance(c, TyExprVar):
            uniq_id = c.uniq_id
            try:
                return self.ty_vars[uniq_id]
            except KeyError:
                raise KindError(
                    "Unbound type variable: " + c.name_ast.id,
                    c)
        elif isinstance(c, CanonicalTy):
            return SingletonKind(c)
        elif isinstance(c, TyExprPrj):
            path_val = c.path_val
            lbl = c.lbl
            return path_val.kind_of(lbl)
        else:
            raise UsageError("Invalid construction.")

    def ana_ty_expr(self, c, k):
        syn_k = self.syn_ty_expr(c)
        if self.subkind(syn_k, k): return
        else:
            raise KindError(
                "Kind mismatch. Expected: '" + str(k) + 
                "'. Got: '" + str(syn_k) + "'.",
                c)

    def con_eq(self, c1, c2, k):
        if c1 == c2:
            self.ana_ty_expr(c1, k) 
            return True
        elif k == TypeKind:
            if isinstance(c1, CanonicalTy):
                if isinstance(c2, CanonicalTy):
                    return (c1.fragment == c2.fragment 
                            and c1.fragment.idx_eq(self, c1.idx, c2.idx))
                else:
                    return self.con_eq(c1, self.canonicalize(c2), k)
            else:
                return self.con_eq(self.canonicalize(c1), c2, k)
        elif isinstance(k, SingletonKind):
            try:
                return self.ana_ty_expr(c1, k) and self.ana_ty_expr(c2, k)
            except KindError:
                return False
        else:
            raise KindError("Invalid kind.", k)

    def canonicalize(self, ty):
        if isinstance(ty, CanonicalTy): return ty
        elif isinstance(ty, TyExprVar) or isinstance(ty, TyExprPrj):
            k = self.syn_ty_expr(ty)
            if k == TypeKind:
                return ty
            elif isinstance(k, SingletonKind):
                return self.canonicalize(k.ty)
            else:
                raise UsageError("Invalid kind.")
        else:
            raise UsageError("Invalid construction.")

    def ana_uty_expr(self, uty_expr, k):
        if isinstance(uty_expr, UName):
            id = uty_expr.id
            static_env = self.static_env
            ty_ids = self.ty_ids
            if id in ty_ids:
                convar = ty_ids[id]
                self.ana_ty_expr(convar, k)
                return convar
            elif id in static_env:
                static_val = self.static_env[id]
                if is_fragment(static_val):
                    ty = CanonicalTy.new(self, static_val, 
                                         _astx.empty_tuple_ast)
                    self.ana_ty_expr(ty, k)
                    return ty
                else:
                    raise KindError(
                        "Type expression '" + 
                        id + 
                        "' is bound to static value '" + 
                        repr(static_val) + 
                        "', which is neither a fragment nor a " +
                        "type expression.", uty_expr)
            else:
                raise KindError(
                    "Type expression '" + 
                    id + 
                    "' is unbound.", uty_expr)
        elif isinstance(uty_expr, UCanonicalTy):
            fragment_ast = uty_expr.fragment_ast
            idx_ast = uty_expr.idx_ast
            static_env = self.static_env
            fragment = static_env.eval_expr_ast(fragment_ast)
            if is_fragment(fragment):
                ty = CanonicalTy.new(self, fragment, idx_ast)
                self.ana_ty_expr(ty, k)
                return ty
            else:
                raise KindError(
                    "Term did not evaluate to a fragment in "
                    "static environment.",
                    fragment_ast)
        elif isinstance(uty_expr, UProjection):
            path_ast, lbl = uty_expr.path_ast, uty_expr.lbl
            path_val = self.static_env.eval_expr_ast(path_ast)
            if is_component(path_val):
                con = TyExprPrj(path_ast, path_val, lbl)
                self.ana_ty_expr(con, k)
                return con
            else:
                raise KindError(
                    "Path did not evaluate to a component in "
                    "static environment.",
                    path_ast)
        else:
            raise KindError(
                "Invalid type expression: " + repr(uty_expr), uty_expr)

    def as_type(self, expr):
        uty_expr = UTyExpr.parse(expr)
        return self.ana_uty_expr(uty_expr, TypeKind)

    def ana(self, tree, ty):
        if _is_intro_form(tree):
            canonical_ty = self.canonicalize(ty)
            if canonical_ty is None:
                raise TyError(
                    "Cannot analyze an intro form against non-canonical "
                    "type.",
                    tree)
            tree.is_intro_form = True
            classname = tree.__class__.__name__
            ana_method_name = "ana_" + classname
            fragment = canonical_ty.fragment
            idx = canonical_ty.idx
            ana_method = getattr(fragment, ana_method_name)
            ana_method(self, tree, idx)
            ty = canonical_ty
            delegate = fragment
            delegate_idx = idx
            translation_method_name = "trans_" + classname
        else:
            syn_ty = self.syn(tree)
            if self.con_eq(ty, syn_ty, TypeKind):
                return
            else:
                raise TyError(
                    "Type inconsistency. Expected: " + str(ty) + 
                    ". Got: " + str(syn_ty) + ".", tree)
        tree.delegate = delegate
        tree.delegate_idx = delegate_idx
        tree.translation_method_name = translation_method_name

    def syn(self, tree):
        if hasattr(tree, "ty"): return tree.ty
        if isinstance(tree, ast.Name):
            try:
                uniq_id, ty = self.lookup_exp_var_by_id(tree.id)
                tree.uniq_id = uniq_id
                delegate = None
                delegate_idx = None
                translation_method_name = None
            except KeyError:
                try:
                    static_val = self.static_env[tree.id]
                except KeyError:
                    raise TyError("Invalid name: " + tree.id, tree)
                if isinstance(static_val, Component):
                    ty = CanonicalTy(component_singleton, static_val)
                    delegate = component_singleton
                    delegate_idx = static_val
                    translation_method_name = "trans_Name"
                else:
                    raise TyError("Invalid name.", tree)
        elif _is_targeted_form(tree):
            target, form_name = _target_and_name_of(tree)
            target_ty = self.syn(target)
            can_target_ty = self.canonicalize(target_ty)
            if isinstance(can_target_ty, CanonicalTy):
                delegate = can_target_ty.fragment
                delegate_idx = can_target_ty.idx
                syn_method_name = "syn_" + form_name
                syn_method = getattr(delegate, syn_method_name)
                ty = syn_method(self, tree, delegate_idx)
                translation_method_name = "trans_" + form_name
            else:
                raise TyError(
                    "Target type cannot be canonicalized.", target)
        elif isinstance(tree, ast.FunctionDef):
            decorator_list = tree.decorator_list
            if len(decorator_list) == 0:
                raise TyError(
                    "Cannot synthesize a type for an undecorated" 
                    "definition.",
                    tree)
            asc = decorator_list[0]
            fragment = self.static_env.eval_expr_ast(asc)
            if not issubclass(fragment, Fragment):
                raise TyError("First decorator is not a fragment.", asc)
            self.default_fragments.append(fragment)
            ty = fragment.syn_FunctionDef(self, tree)
            self.default_fragments.pop()
            self.ana_ty_expr(ty, TypeKind)
            delegate = fragment
            delegate_idx = None
            translation_method_name = None # TODO
        elif isinstance(tree, ast.BinOp):
            left = tree.left
            right = tree.right
            try:
                left_ty = self.syn(left)
            except:
                left_ty = None
            try:
                right_ty = self.syn(right)
            except:
                right_ty = None
            if left_ty is None and right_ty is None:
                raise TyError(
                    "Neither argument synthesizes a type.",
                    tree)
            elif left_ty is not None and right_ty is None:
                left_ty_c = self.canonicalize(left_ty)
                delegate = left_ty_c.fragment
                delegate_idx = None
                translation_method_name = "trans_BinOp"
                ty = delegate.syn_BinOp(self, tree)
            elif left_ty is None and right_ty is not None:
                right_ty_c = self.canonicalize(right_ty)
                delegate = right_ty_c.fragment
                delegate_idx = None
                translation_method_name = "trans_BinOp"
                ty = delegate.syn_BinOp(self, tree)
            else:
                left_ty_c = self.canonicalize(left_ty)
                right_ty_c = self.canonicalize(right_ty)
                left_fragment = left_ty_c.fragment
                right_fragment = right_ty_c.fragment
                if left_fragment is right_fragment:
                    delegate = left_fragment
                else:
                    left_precedence = left_fragment.precedence
                    right_precedence = right_fragment.precedence
                    if left_fragment in right_precedence:
                        if right_fragment in left_precedence:
                            raise TyError(
                                "Circular precedence sets.", tree)
                        delegate = right_fragment
                    elif right_fragment in left_precedence:
                        delegate = left_fragment
                    else:
                        raise TyError(
                            "Left and right of operator synthesize types where "
                            "the fragments are mutually non-precedent.", tree)
                delegate_idx = None
                translation_method_name = "trans_BinOp"
                ty = delegate.syn_BinOp(self, tree)
        else:
            raise NotImplementedError()
        tree.ty = ty
        tree.delegate = delegate
        tree.delegate_idx = delegate_idx
        tree.translation_method_name = translation_method_name
        return ty

    def check(self, stmt):
        if isinstance(stmt, ast.Assign):
            try:
                delegate = self.default_fragments[-1]
            except IndexError:
                raise TyError("No default fragment.", stmt)
            delegate_idx = None
            translation_method_name = "trans_Assign"
            delegate.check_Assign(self, stmt)
        elif isinstance(stmt, ast.Expr):
            try:
                delegate = self.default_fragments[-1]
            except IndexError:
                raise TyError("No default fragment.", stmt)
            delegate_idx = None
            translation_method_name = "trans_Expr"
            delegate.check_Expr(self, stmt)
        else:
            raise NotImplementedError(stmt.__class__.__name__)
        stmt.delegate = delegate
        stmt.delegate_idx = delegate_idx
        stmt.translation_method_name = translation_method_name

    def ana_pat(self, pat, ty):
        if isinstance(pat, ast.Name):
            id = pat.id
            if id == "_":
                return { }
            else:
                return { pat: ty }
        else:
            raise NotImplementedError()
        raise NotImplementedError()

    def trans(self, tree):
        if isinstance(tree, ast.Name):
            if hasattr(tree, "uniq_id"):
                uniq_id = tree.uniq_id
                translation = ast.copy_location(
                    ast.Name(id=uniq_id, ctx=tree.ctx),
                    tree)
            else:
                # component reference
                return ast.fix_missing_locations(ast.copy_location(
                    ast.Attribute(
                        value=tree,
                        attr="_module",
                        ctx=ast.Load()),
                    tree))
        else:
            delegate = tree.delegate
            idx = tree.delegate_idx
            translation_method_name = tree.translation_method_name
            translation_method = getattr(delegate, translation_method_name)
            if idx is not None:
                translation = translation_method(self, tree, idx)
            else:
                translation = translation_method(self, tree)
        tree.translation = translation
        return translation

    def trans_FunctionDef(self, stmt, id):
        if isinstance(stmt, ast.FunctionDef):
            delegate = stmt.delegate
            translation = stmt.translation = delegate.trans_FunctionDef(self, stmt, id)
            return translation
        else:
            raise NotImplementedError()
            

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

_targeted_forms = (
    ast.UnaryOp,
    ast.IfExp,
    ast.Call,
    ast.Attribute,
    ast.Subscript)
def _is_targeted_form(e):
    return isinstance(e, _targeted_forms)
def _target_and_name_of(e):
    if isinstance(e, ast.UnaryOp):
        return e.operand, "UnaryOp"
    elif isinstance(e, ast.IfExp):
        return e.test, "IfExp"
    elif isinstance(e, ast.Call):
        return e.func, "Call"
    elif isinstance(e, ast.Attribute):
        return e.value, "Attribute"
    elif isinstance(e, ast.Subscript):
        return e.value, "Subscript"
    else:
        raise UsageError("e is not a targeted expression.")

#
# Semantic Fragments
#

import inspect

class Fragment(object):
    def __init__(self):
        raise NotImplementedError()

    @classmethod
    def init_idx(cls, ctx, idx_ast):
        raise FragmentError(cls.__name__ + " does not implement init_idx.", cls)

    @classmethod
    def idx_eq(cls, ctx, idx1, idx2):
        return idx1 == idx2

    precedence = set()

    # intro forms
    @classmethod
    def ana_FunctionDef(cls, ctx, stmt, idx):
        raise TyError(cls.__name__ + " does not support def literals.", cls)

    @classmethod
    def trans_FunctionDef(cls, ctx, stmt, idx):
        raise FragmentError("Missing translation method: trans_FunctionDef.", cls)

    @classmethod
    def syn_FunctionDef(cls, ctx, stmt):
        raise TyError(cls.__name__ + " does not support fragment-decorated def literals.", cls)

    @classmethod
    def ana_Lambda(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support lambda literals.", cls)

    @classmethod
    def trans_Lambda(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Lambda.", cls)

    @classmethod
    def ana_Dict(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support dictionary literals.", cls)

    @classmethod
    def trans_Dict(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Dict.", cls)

    @classmethod
    def ana_Set(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support set literals.", cls)

    @classmethod
    def trans_Set(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Set.", cls)

    @classmethod
    def ana_Num(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support number literals.", cls)

    @classmethod
    def trans_Num(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Num.", cls)

    @classmethod
    def ana_Str(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support string literals.", cls)

    @classmethod
    def trans_Str(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Str.", cls)

    @classmethod # TODO what are these
    def ana_Bytes(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support byte literals.", cls)

    @classmethod
    def trans_Bytes(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Bytes.", cls)

    @classmethod # TODO what are these
    def ana_NameConstant(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support name constant literals.", cls)

    @classmethod
    def trans_NameConstant(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_NameTyExprstant.", cls)

    @classmethod
    def ana_List(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support list literals.", cls)
    
    @classmethod
    def trans_List(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_List.", cls)

    @classmethod
    def ana_Tuple(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support tuple literals.", cls)
    
    @classmethod
    def trans_Tuple(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Tuple.", cls)

    @classmethod
    def check_Assign(cls, ctx, stmt):
        raise TyError(cls.__name__ + " does not support assignment statements.", cls)

    @classmethod
    def trans_Assign(cls, ctx, stmt):
        raise FragmentError("Missing translation method: trans_Assign", cls)

    @classmethod
    def check_Expr(cls, ctx, stmt):
        raise TyError(cls.__name__ + " does not support expression statements.", cls)

    @classmethod
    def trans_Expr(cls, ctx, stmt):
        raise FragmentError("Missing translation method: trans_Expr", cls)

    # Targeted Forms
    @classmethod
    def syn_UnaryOp(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support unary operations.", cls)

    @classmethod
    def trans_UnaryOp(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_UnaryOp", cls)

    @classmethod
    def syn_IfExp(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support if expressions.", cls)

    @classmethod
    def trans_IfExp(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_IfExp", cls)

    @classmethod
    def syn_Call(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support call expressions.", cls)

    @classmethod
    def trans_Call(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Call", cls)

    @classmethod
    def syn_Attribute(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support attribute expressions.", cls)

    @classmethod
    def trans_Attribute(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Attribute", cls)

    @classmethod
    def syn_Subscript(cls, ctx, e, idx):
        raise TyError(cls.__name__ + " does not support subscript expressions.", cls)

    @classmethod
    def trans_Subscript(cls, ctx, e, idx):
        raise FragmentError("Missing translation method: trans_Subscript", cls)

    # Binary Forms
    @classmethod
    def syn_BinOp(cls, ctx, e):
        raise TyError(cls.__name__ + " does not support binary operators.", cls)

    @classmethod
    def trans_BinOp(cls, ctx, e):
        raise FragmentError("Missing translation method: trans_BinOp.", cls)

def is_fragment(x):
    return inspect.isclass(x) and issubclass(x, Fragment)

class component_singleton(Fragment):
    @classmethod
    def syn_Attribute(cls, ctx, e, idx):
        try:
            member = idx._exports[e.attr]
        except KeyError:
            raise TyError("Invalid component member: " + e.attr, e)
        if isinstance(member, ValueMember):
            return member.ty
        else:
            raise TyError("Component member is not a value member: " + e.attr, e)

    @classmethod
    def trans_Attribute(cls, ctx, e, idx):
        return ast.fix_missing_locations(ast.copy_location(
            ast.Attribute(
                value=ctx.trans(e.value),
                attr=e.attr,
                ctx=ast.Load()),
            e))

