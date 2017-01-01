"""typy term (statement/expression) model"""
import ast

from . import util as _util

# 
# Statements
# 

def is_match_scrutinizer(stmt):
    if isinstance(stmt, ast.Expr):
        value = stmt.value
        if isinstance(value, ast.Attribute):
            attribute_value = value.value
            if isinstance(attribute_value, ast.List) and value.attr == "match":
                return True
    return False

def is_match_rule(stmt):
    return isinstance(stmt, ast.With)

def is_stmt_expression(tree):
    return (isinstance(tree, StatementExpression) or 
            isinstance(tree, (ast.If, ast.Raise, ast.Try, ast.Expr, ast.Pass)))

class StatementExpression(object):
    pass

class MatchStatementExpression(StatementExpression):
    def __init__(self, scrutinizer, rules):
        self.scrutinizer = scrutinizer
        self.scrutinee = scrutinizer.value.value.elts[0]
        self.rules = rules

class MatchRule(object):
    def __init__(self, stmt, pat, branch):
        self.stmt = stmt
        self.pat = pat
        self.branch = branch

    @classmethod
    def parse_with_stmt(cls, stmt):
        return cls(stmt, stmt.items[0].context_expr, stmt.body)

_supported_stmt_forms = (
    ast.FunctionDef,
    ast.Return,
    ast.Delete,
    ast.Assign,
    ast.AugAssign,
    ast.For,
    ast.While,
    ast.If,
    ast.With,
    ast.Raise,
    ast.Try,
    ast.Assert,
    ast.Expr,
    ast.Pass,
    ast.Break,
    ast.Continue)

def is_supported_stmt_form(stmt):
    return isinstance(stmt, _supported_stmt_forms)

_unsupported_stmt_forms = (
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.AsyncFor,
    ast.AsyncWith,
    ast.Import,
    ast.ImportFrom,
    ast.Global,
    ast.Nonlocal)

def is_unsupported_stmt_form(stmt):
    return isinstance(stmt, _unsupported_stmt_forms)

def is_targeted_stmt_form(stmt):
    if isinstance(stmt, ast.Delete):
        targets = stmt.targets
        if len(targets) != 1:
            # TODO support multiple targets
            raise TyError(
                "typy does not support multiple deletion targets.", targets[1])
        target = targets[0]
        stmt._typy_target = target
        return True
    elif isinstance(stmt, ast.Assign):
        targets = stmt.targets
        if len(targets) != 1:
            # TODO support multiple targets
            raise TyError(
                "typy does not support multiple targets.", targets[1])
        target = targets[0]
        if isinstance(target, ast.Attribute):
            stmt._typy_target = target.value
            return True
        elif isinstance(target, ast.Subscript):
            # TODO exclude ascriptions
            stmt._typy_target = target.value
            return True
        else:
            return False
    elif isinstance(stmt, ast.AugAssign):
        stmt._typy_target = stmt.target
        return True
    elif isinstance(stmt, ast.For):
        stmt._typy_target = stmt.iter
        return True
    elif isinstance(stmt, ast.While):
        stmt._typy_target = stmt.test
        return True
    elif isinstance(stmt, ast.If):
        stmt._typy_target = stmt.test
        return True
    else:
        return False

def is_default_stmt_form(stmt):
    if isinstance(stmt, (
            ast.Return,
            ast.Raise,
            ast.Try,
            ast.Assert,
            ast.Expr,
            ast.Pass,
            ast.Break,
            ast.Continue)):
        return True
    elif isinstance(stmt, ast.Assign):
        targets = stmt.targets
        if len(targets) != 1:
            # TODO support multiple targets
            raise TyError(
                "typy does not support multiple targets.", targets[1])
        target = targets[0]
        if isinstance(target, ast.Attribute):
            return False
        elif isinstance(target, ast.Subscript):
            # TODO include ascriptions
            return False
        else:
            return True
    else:
        return False

_intro_expr_forms = (
    ast.Lambda, 
    ast.Dict, 
    ast.Set, 
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
    ast.Num, 
    ast.Str, 
    ast.Bytes,
    ast.NameConstant, 
    ast.List, 
    ast.Tuple)

_intro_forms = tuple(_util.seq_cons(
    ast.FunctionDef, _intro_expr_forms))

def is_Name_constructor(e):
    return isinstance(e, ast.Name) and e.id[0].isupper()

def is_Unary_literal(e):
    return isinstance(e, ast.UnaryOp) and isinstance(e.operand, ast.Num)

def is_intro_form(e):
    return isinstance(e, _intro_forms) or is_Name_constructor(e) or is_Unary_literal(e)

def is_targeted_expr_form(e):
    if isinstance(e, ast.UnaryOp):
        e._typy_target = e.operand
        return True
    elif isinstance(e, ast.IfExp):
        e._typy_target = e.test
        return True
    elif isinstance(e, ast.Call):
        e._typy_target = e.func
        return True
    elif isinstance(e, ast.Attribute):
        e._typy_target = e.value
        return True
    elif isinstance(e, ast.Subscript):
        # TODO exclude ascriptions
        e._typy_target = e.value
        return True
    else:
        return False

def is_targeted_form(tree):
    return is_targeted_expr_form(tree) or is_targeted_stmt_form(tree)

def is_ascription(e):
    if hasattr(e, 'ascription'): return True
    if isinstance(e, ast.Subscript):
        slice = e.slice
        if isinstance(slice, ast.Slice):
            lower, upper, step = slice.lower, slice.upper, slice.step
            if lower is None and upper is not None and step is None:
                e.ascription = upper
                return True
    return False

unsupported_expr_forms = (
    ast.Await,
    ast.Yield,
    ast.YieldFrom)

def parse_fn_body(body):
    for stmt in body:
        if isinstance(stmt, (
                ast.FunctionDef, 
                ast.Return, 
                ast.AugAssign,
                ast.For,
                ast.While,
                ast.If,
                ast.Raise,
                ast.Try,
                ast.Assert,
                ast.Pass,
                ast.Break,
                ast.Continue)):
            yield stmt
        elif isinstance(stmt, ast.Delete):
            targets = stmt.targets
            if len(targets) == 1:
                yield stmt
            else:
                # break multi-target deletes into multiple
                # single-target deletes so that each can 
                # delegate separately
                for target in targets:
                    yield ast.copy_location(
                        ast.Delete(targets=[target]),
                        stmt)
        elif isinstance(stmt, ast.Assign):
            # TODO handle ascriptions
            # TODO handle targeted assignment forms
            # TODO handle multiple targets
            raise NotImplementedError()
        elif isinstance(stmt, ast.With):
            # TODO pattern matching clauses
            raise NotImplementedError()
        elif isinstance(stmt, ast.Expr):
            # TODO pattern matching scrutinee
            raise NotImplementedError()
        elif isinstance(stmt, _unsupported_stmt_forms):
            raise TyError("Unsupported statement form: " +
                          stmt.__class__.__name__, stmt)
        else:
            raise TyError("Unknown statement form: " + 
                          stmt.__class__.__name__, stmt)

