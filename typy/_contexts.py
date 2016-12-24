"""typy contexts"""

import ast
from . import util as _util
from .util import astx as _astx
from ._ty_exprs import (
    TyExprVar, TypeKind, SingletonKind, UName, 
    CanonicalTy, UCanonicalTy, UTyExpr, UProjection, 
    TyExprPrj)
from ._errors import UsageError, KindError, TyError
from ._fragments import is_fragment, Fragment
from . import _components
from . import _terms

__all__ = ("Context",)

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

    #
    # Bindings
    # 
    # TODO clean up all this

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

    # 
    # Statements and expressions
    # 

    def check(self, stmt):
        if _terms.is_targeted_stmt_form(stmt):
            target = stmt._typy_target # side effect of the guard call
            form_name = stmt.__class__.__name__
            target_ty = self.syn(target)
            c_target_ty = self.canonicalize(c_target_ty)
            delegate = c_target_ty.fragment
            delegate_idx = c_target_ty.idx
            check_method_name = "check_" + form_name
            translation_method_name = "trans_" + form_name
            check_method = getattr(delegate, check_method_name)
            check_method(self, stmt, delegate_idx)
        elif _terms.is_default_stmt_form(stmt):
            try:
                delegate = self.default_fragments[-1]
            except IndexError:
                raise TyError("No default fragment.", stmt)
            delegate_idx = None
            cls_name = stmt.__class__.__name__
            check_method_name = "check_" + cls_name
            translation_method_name = "trans_" + cls_name
            check_method = getattr(delegate, check_method_name)
            check_method(self, stmt)
        elif False:
            # TODO function def
            pass
        elif _terms.is_unsupported_stmt_form(stmt):
            raise TyError("Unsupported statement form.", stmt)
        else:
            raise TyError("Unknown statement form: " + 
                          stmt.__class__.__name__, stmt)

        stmt.delegate = delegate
        stmt.delegate_idx = delegate_idx
        stmt.translation_method_name = translation_method_name

    def ana(self, tree, ty):
        # handle the case where neither left or right synthesize a type
        if isinstance(tree, ast.BinOp):
            left, right = tree.left, tree.right
            try:
                self.syn(left)
            except:
                try:
                    self.syn(right)
                except:
                    ty = self.canonicalize(ty)
                    delegate = ty.fragment
                    delegate_idx = None

                    # will get picked up by subsumption below
                    tree.ty = delegate.syn_BinOp(self, tree)
                    tree.delegate = delegate
                    tree.delegate_idx = delegate_idx
                    tree.translation_method_name = "trans_BinOp"

        subsumed = False
        if _terms.is_intro_form(tree):
            ty = self.canonicalize(ty)
            if ty is None:
                raise TyError(
                    "Cannot analyze an intro form against non-canonical "
                    "type.",
                    tree)
            tree.is_intro_form = True
            classname = tree.__class__.__name__
            ana_method_name = "ana_" + classname
            delegate = ty.fragment
            delegate_idx = ty.idx
            ana_method = getattr(delegate, ana_method_name)
            ana_method(self, tree, delegate_idx)
            translation_method_name = "trans_" + classname
        else:
            subsumed = True
            syn_ty = self.syn(tree)
            if self.ty_expr_eq(ty, syn_ty, TypeKind):
                return
            else:
                raise TyError(
                    "Type inconsistency. Expected: " + str(ty) + 
                    ". Got: " + str(syn_ty) + ".", tree)

        if not subsumed:
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
                if isinstance(static_val, _components.Component):
                    delegate = _components.component_singleton
                    ty = CanonicalTy(delegate, static_val)
                    delegate_idx = static_val
                    translation_method_name = "trans_Name"
                else:
                    raise TyError("Invalid name.", tree)
        elif _terms.is_targeted_expr_form(tree):
            target = tree._typy_target # side effect of guard call
            form_name = tree.__class__.__name__
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

    # 
    # Patterns
    # 

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

    # 
    # Kinds and type expressions
    # 

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
            return self.ty_expr_eq(k1.ty, k2.ty, TypeKind)
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

    def ty_expr_eq(self, c1, c2, k):
        if c1 == c2:
            self.ana_ty_expr(c1, k) 
            return True
        elif k == TypeKind:
            if isinstance(c1, CanonicalTy):
                if isinstance(c2, CanonicalTy):
                    return (c1.fragment == c2.fragment 
                            and c1.fragment.idx_eq(self, c1.idx, c2.idx))
                else:
                    return self.ty_expr_eq(c1, self.canonicalize(c2), k)
            else:
                return self.ty_expr_eq(self.canonicalize(c1), c2, k)
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
            if _components.is_component(path_val):
                con = TyExprPrj(path_ast, path_val, lbl)
                self.ana_ty_expr(con, k)
                return con
            else:
                try:
                    fragment = getattr(path_val, lbl)
                except AttributeError:
                    raise KindError(
                        "Invalid projection.", path_ast)
                else:
                    if is_fragment(fragment):
                        ty = CanonicalTy.new(self, fragment, _astx.empty_tuple_ast)
                        self.ana_ty_expr(ty, k)
                        return ty
                    else:
                        raise KindError(
                            "Invalid projection.", path_ast)
        else:
            raise KindError(
                "Invalid type expression: " + repr(uty_expr), uty_expr)

    def as_type(self, expr):
        uty_expr = UTyExpr.parse(expr)
        return self.ana_uty_expr(uty_expr, TypeKind)

