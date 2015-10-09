"""typy functional programming primitives"""
import ast

import typy

class unit_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of unit type must be ().")
        return idx

    def ana_Tuple(self, ctx, e):
        elts = e.elts
        if len(elts) != 0:
            raise typy.TypeError(
                "Non-empty tuple forms cannot be used to introduce values of type unit.",
                e)

    @classmethod
    def syn_idx_Tuple(self, ctx, e, inc_idx):
        elts = e.elts 
        if len(elts) != 0:
            raise typy.TypeError(
                "Non-empty tuple forms cannot be used to introduce values of type unit.",
                e)
        return ()
        
unit = unit_[()]

class boolean_(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        if idx != ():
            raise typy.TypeFormationError("Index of boolean type must be ().")
        return idx

    def ana_Name_constructor(self, ctx, e):
        id = e.id
        if id != "True" and id != "False":
            raise typy.TypeError(
                "Must introduce a value of boolean type with either True or False.",
                e)

    @classmethod
    def syn_idx_Name_constructor(self, ctx, e):
        id = e.id
        if id != "True" and id != "False":
            raise typy.TypeError(
                "Must introduce a value of boolean type with either True or False.",
                e)

    # TODO: case/if operators
boolean = boolean_[()]

class fn(typy.FnType):
    @classmethod
    def init_idx(cls, idx):
        if isinstance(idx, tuple):
            idx = _normalize_fn_idx(idx)
            (arg_types, return_type) = idx
            for arg_type in arg_types:
                if not isinstance(arg_type, typy.Type):
                    raise typy.TypeFormationError(
                        "Argument type is not a type.")
            if not isinstance(return_type, typy.Type):
                raise typy.TypeFormationError(
                    "Return type is not a type.")
        else:
            raise typy.TypeFormationError(
                "Function type index is not a pair.")
        return idx

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx == Ellipsis: 
            # if no index is provided, we will extract signature from the fn body
            pass
        elif isinstance(inc_idx, tuple):
            inc_idx = _normalize_fn_idx(inc_idx)
            (arg_types, return_type) = inc_idx
            for arg_type in arg_types:
                if not isinstance(arg_type, typy.Type):
                    raise typy.TypeFormationError(
                        "Argument type is not a type.")
            if return_type != Ellipsis:
                raise typy.TypeFormationError(
                    "Return type for an incomplete fn type must be elided.")
        else:
            raise typy.TypeFormationError(
                "Incomplete fn type index is not an ellipsis or pair.")
        return inc_idx

    @classmethod
    def preprocess_FunctionDef_toplevel(cls, fn, tree):
        body = tree.body
        (docstring, post_docstring_body) = _extract_docstring(body)
        fn.__doc__ = fn.func_doc = docstring
        fn._post_docstring_body = post_docstring_body

    @classmethod
    def init_ctx(cls, ctx):
        ctx.variables = DictStack()
        ctx.variables.push({})
        ctx.return_type = None

    def ana_FunctionDef_toplevel(self, ctx, tree):
        name, args = tree.name, tree.args
        body = ctx.fn._post_docstring_body
        (arg_types, return_type) = self.idx
        ctx.return_type = return_type

        _setup_args(ctx, args, arg_types, tree)
        arg_names = _get_arg_names(args)
        if len(body) > 0:
            sig_idx = _process_function_signature(body[0], arg_names, ctx.fn.static_env)
            if sig_idx != None:
                if (sig_idx[0] != self.idx[0]) \
                        or (sig_idx[1] != Ellipsis and sig_idx[1] != self.idx[1]):
                    raise typy.TypeError(
                        "Function signature and function ascription do not match.", 
                        body[0])
                body = body[1:]

        if len(body) == 0:
            if return_type != unit:
                raise typy.TypeError(
                    "Empty function bodies must have unit return type.", tree)
            else: return

        all_but_last_stmt = body[0:-1]
        last_stmt = body[-1]
        for stmt in all_but_last_stmt:
            ctx.check(stmt) 
        if isinstance(last_stmt, ast.Pass):
            if return_type != unit:
                raise typy.TypeMismatchError(return_type, unit, last_stmt)
        elif isinstance(last_stmt, ast.Expr):
            ctx.ana(last_stmt.value, return_type)
        else:
            raise typy.TypeError("Last statement must be pass or an expression.",
                last_stmt)

    @classmethod
    def syn_idx_FunctionDef_toplevel(cls, ctx, tree, inc_ty):
        name, args = tree.name, tree.args 
        body = ctx.fn._post_docstring_body
        inc_idx = inc_ty.inc_idx

        arg_names = _get_arg_names(args)
        if len(body) == 0:
            if inc_idx == Ellipsis:
                raise typy.TypeError("Expected function signature.", tree)
        else:
            sig_idx = _process_function_signature(body[0], arg_names, ctx.fn.static_env)
            if inc_idx == Ellipsis:
                if sig_idx == None:
                    if len(arg_names) == 0:
                        inc_idx = ((), Ellipsis)
                    else:
                        raise typy.TypeError("Expected function signature.", tree)
                else:
                    inc_idx = sig_idx
                    body = body[1:]
            else:
                if sig_idx != None:
                    if inc_idx[0] != sig_idx[0]:
                        raise typy.TypeError(
                            "Argument signature and argument ascription do not match.", 
                            body[0])
                    inc_idx = sig_idx
                    body = body[1:]

        (arg_types, ctx.return_type) = inc_idx

        _setup_args(ctx, args, arg_types, tree)

        # iterate over body
        if len(body) == 0:
            if ctx.return_type == Ellipsis:
                ctx.return_type = unit
            elif ctx.return_type != unit:
                raise typy.TypeError(
                    "Function has empty body but return type is not unit.", 
                    tree)
        else:
            all_but_last_stmt = body[0:-1]
            last_stmt = body[-1]
            for stmt in all_but_last_stmt:
                ctx.check(stmt)
            if isinstance(last_stmt, ast.Pass):
                if ctx.return_type == Ellipsis:
                    ctx.return_type = unit
                elif ctx.return_type != unit:
                    raise typy.TypeError("Function return type mismatch.", last_stmt)
            elif isinstance(last_stmt, ast.Expr):
                if ctx.return_type == Ellipsis:
                    ty = ctx.syn(last_stmt.value)
                    ctx.return_type = ty
                else:
                    ctx.ana(last_stmt.value, ctx.return_type)
            else:
                raise typy.TypeError("Last statement must be pass or an expression.",
                    last_stmt)

        return (arg_types, ctx.return_type)

    @classmethod
    def check_Pass(cls, ctx, tree):
        return

    @classmethod
    def syn_Name(cls, ctx, e):
        id = e.id
        variables = ctx.variables
        try:
            return variables[id]
        except KeyError:
            raise typy.TypeError(
                "Variable not found in context.", e)

    @classmethod
    def check_Assign_Name(cls, ctx, stmt):
        target = stmt.targets[0]
        id = target.id 
        value = stmt.value
        variables = ctx.variables
        try:
            ty = variables[id]
            ctx.ana(value, ty)
        except KeyError:
            ty = ctx.syn(value)
            variables[id] = ty

    @classmethod
    def check_Assign_Subscript(cls, ctx, stmt):
        target = stmt.targets[0]
        target_value, slice = target.value, target.slice
        if isinstance(target_value, ast.Name):
            if isinstance(slice, ast.Slice):
                lower, upper, step = slice.lower, slice.upper, slice.step
                if lower == None and upper is not None and step is None:
                    ty = ctx.fn.static_env.eval_expr_ast(upper)
                    if isinstance(ty, typy.Type):
                        id = target_value.id
                        variables = ctx.variables
                        try:
                            existing_ty = variables[id]
                        except KeyError: pass
                        else: 
                            if ty != existing_ty:
                                raise typy.TypeError("Inconsistent type annotations.", target_value)
                        ctx.ana(stmt.value, ty)
                        ctx.variables[id] = ty
                        return 
                    else:
                        raise typy.TypeError(
                            "Type ascription is not a type.", upper)
        raise typy.TypeError("Form not supported.", stmt)

def _normalize_fn_idx(idx):
    len_idx = len(idx)
    if len_idx < 2:
        raise typy.TypeFormationError(
            "Function type index missing argument and return types.")
    elif len_idx == 2:
        arg_types = idx[0]
        return_type = idx[1]
        if not isinstance(arg_types, tuple):
            if isinstance(arg_types, typy.Type):
              idx = ((arg_types,), return_type)
            else: raise typy.TypeFormationError(
                "Argument signature is not a tuple.") 
    elif len_idx > 2:
        arg_types = idx[0:-1]
        return_type = idx[-1]
        idx = (arg_types, return_type)
    return idx

def _extract_docstring(body):
    docstring_loc = body[0]
    if isinstance(docstring_loc, ast.Expr):
        value = docstring_loc.value
        if isinstance(value, ast.Str):
            return (value.s, body[1:])
    return (None, body)

def _get_arg_names(args):
    return tuple(arg.id for arg in args.args)

def _process_function_signature(stmt, arg_names, static_env):
    return_type = Ellipsis
    if isinstance(stmt, ast.Expr):
        value = stmt.value
        if isinstance(value, ast.BinOp):
            left, op, right = value.left, value.op, value.right
            if isinstance(op, ast.RShift):
                arg_types = _process_argument_signature(left, arg_names, static_env)
                return_type = static_env.eval_expr_ast(right)
            else:
                return None
        elif isinstance(value, ast.Dict) or isinstance(value, ast.Set):
            arg_types = _process_argument_signature(value, arg_names, static_env)
        else:
            return None
    else:
        return None
    if arg_types is None: return None
    return (arg_types, return_type)

def _process_argument_signature(value, arg_names, static_env):
    arg_types = []
    if isinstance(value, ast.Dict):
        keys, values = value.keys, value.values
        n_keys = len(keys)
        n_args = len(arg_names)
        if n_keys != n_args:
            raise typy.TypeError(
                "Function specifies {0} arguments, but function signature specifies {1} arguments."
                .format(n_args, n_keys), value)
        for key, value, arg_name in zip(keys, values, arg_names):
            if not isinstance(key, ast.Name):
                raise typy.TypeError("Argument name must be an identiifer.", key)
            sig_arg_name = key.id
            if sig_arg_name != arg_name:
                raise typy.TypeError(
                    "Function specifies argument name {0}, but function signature specifies argument name {1}."
                    .format(arg_name, key), key)
            arg_types.append(static_env.eval_expr_ast(value))
    elif isinstance(value, ast.Set):
        elts = value.elts
        n_elts = len(elts)
        n_args = len(arg_names)
        if n_elts != n_args:
            raise typy.TypeError(
                "Function specifies {0} arguments, but function signature specifies {1} arguments."
                .format(n_args, n_elts), value)
        for elt in elts:
            arg_types.append(static_env.eval_expr_ast(elt))
    else:
        raise typy.TypeError(
            "Argument signature must have the form of either a set or dict literal.", value)
    return tuple(arg_types)

def _setup_args(ctx, args, arg_types, tree):
    # var and kw args are not supported
    if args.vararg:
        raise typy.TypeError("Varargs are not supported.", args.vararg)
    if args.kwarg:
        raise typy.TypeError("Kwargs are not supported.", args.kwarg)

    # set up arguments in context
    variables = ctx.variables
    arguments = args.args
    n_args, n_arg_types = len(arguments), len(arg_types)
    if n_args != n_arg_types:
        raise typy.TypeError(
            "Type specifies {0} arguments but function has {1}.".format(n_arg_types, n_args), 
            tree)
    if len(args.defaults) != 0:
        raise typy.TypeError("Defaults are not supported.", tree)
    for arg, arg_type in zip(arguments, arg_types):
        if not isinstance(arg, ast.Name):
            raise typy.TypeError("Argument must be an identifier.", arg)
        arg_id = arg.id
        variables[arg_id] = arg_type

class DictStack(object):
    # TODO: move to cypy
    def __init__(self, stack=None):
        if stack is None:
            stack = [ ]
        self.stack = stack 

    def push(self, d):
        self.stack.append(d)
        return self

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def __getitem__(self, key):
        for d in reversed(self.stack):
            try:
                return d[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.peek()[key] = value

    def __contains__(self, key):
        for d in reversed(self.stack):
            if key in d: return True
        return False 
