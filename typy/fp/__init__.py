"""typy functional programming primitives"""
import ast

import typy
import typy.util 
import typy.util.astx as astx
import typy.std

#
# unit
#

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

    def translate_Tuple(self, ctx, e):
        return ast.Name("None", ast.Load())

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if not isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
                raise typy.TypeError(
                    "Unit type does not support this operator.", e)
        for e_ in typy.util.tpl_cons(left, comparators):
            if hasattr(e_, "match"): continue # already synthesized
            ctx.ana(e_, self)
        return typy.std.bool

    def translate_Compare(self, ctx, e):
        translation=astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.comparators = tuple(
            ctx.translate(comparator)
            for comparator in e.comparators)
        return translation

unit = unit_[()]

#
# fn
#

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
        tree._post_docstring_body = post_docstring_body

    @classmethod
    def init_ctx(cls, ctx):
        ctx.variables = typy.util.DictStack()
        ctx.variables.push({})
        ctx.return_type = None

    def ana_FunctionDef_toplevel(self, ctx, tree):
        name, args = tree.name, tree.args
        body = tree._post_docstring_body
        tree._post_sig_body = body # will update below if needed
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
                body = tree._post_sig_body = body[1:]

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
        body = tree._post_docstring_body
        tree._post_sig_body = body # will update below if needed
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
                    body = tree._post_sig_body = body[1:]
            else:
                if sig_idx != None:
                    if inc_idx[0] != sig_idx[0]:
                        raise typy.TypeError(
                            "Argument signature and argument ascription do not match.", 
                            body[0])
                    inc_idx = sig_idx
                    body = tree._post_sig_body = body[1:]

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

    def translate_FunctionDef_toplevel(self, ctx, tree):
        body_translation = [ ]
        body = tree._post_sig_body
            
        if len(body) == 0:
            body_translation.append(ast.Pass())
        else:
            all_but_last_stmt = body[0:-1]
            last_stmt = body[-1]
            for stmt in all_but_last_stmt:
                body_translation.append(ctx.translate(stmt))
            if isinstance(last_stmt, ast.Pass):
                body_translation.append(ast.Pass())
            elif isinstance(last_stmt, ast.Expr):
                body_translation.append(ast.Return(ctx.translate(last_stmt.value)))

        return ast.FunctionDef(
            name=tree.name,
            args=astx.deep_copy_node(tree.args),
            body=body_translation,
            decorator_list=[])

    @classmethod
    def check_Pass(cls, ctx, tree):
        return

    def translate_Pass(self, ctx, tree):
        return astx.copy_node(tree)

    @classmethod
    def syn_Name(cls, ctx, e):
        id = e.id
        variables = ctx.variables
        try:
            return variables[id]
        except KeyError:
            raise typy.TypeError(
                "Variable not found in context.", e)

    def translate_Name(cls, ctx, e):
        return astx.copy_node(e)

    @classmethod
    def check_Assign(cls, ctx, stmt):
        targets, value = stmt.targets, stmt.value
        asc_ty = _process_targets(ctx, targets)
        if asc_ty == None:
            ty = ctx.syn(value)
        else:
            ty = asc_ty 
            ctx.ana(value, ty)
        _update_targets(ctx, targets, ty)

    def translate_Assign(self, ctx, stmt):
        targets, value = stmt.targets, stmt.value
        target_translation = [ ]
        for target in targets:
            if isinstance(target, ast.Name):
                target_translation.append(astx.copy_node(target))
            elif isinstance(target, ast.Subscript):
                target_translation.append(astx.copy_node(target.value))
        value_translation = ctx.translate(value)
        return ast.Assign(target_translation, value_translation)

    @classmethod
    def check_Expr(cls, ctx, stmt):
        ctx.syn(stmt.value)

    def translate_Expr(self, ctx, stmt):
        return ast.Expr(ctx.translate(stmt.value))

    def syn_Call(self, ctx, e):
        args, keywords, starargs, kwargs = e.args, e.keywords, e.starargs, e.kwargs
        if len(keywords) != 0 or kwargs != None:
            raise typy.TypeError("Keyword arguments are not supported.",
                e)
        if starargs != None:
            raise typy.TypeError("Star arguments are not supported.",
                e)
        arg_types, return_type = self.idx
        n_args = len(args)
        n_arg_types = len(arg_types)
        if n_args < n_arg_types:
            raise typy.TypeError("Too few arguments.", e)
        elif n_args > n_arg_types:
            raise typy.TypeError("Too many arguments.", args[n_arg_types])
        for (arg, arg_type) in zip(args, arg_types):
            ctx.ana(arg, arg_type)
        return return_type 

    def translate_Call(self, ctx, e):
        func, args = e.func, e.args
        translation = astx.copy_node(e)
        translation.func = ctx.translate(func)
        translation.args = list(
            ctx.translate(arg)
            for arg in args)
        return translation

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

def _process_targets(ctx, targets):
    asc_ty = None
    for target in targets:
        if isinstance(target, ast.Name):
            id = target.id
            variables = ctx.variables
            try:
                ctx_ty = variables[id]
            except KeyError: pass
            else:
                if asc_ty is None:
                    asc_ty = ctx_ty
                elif asc_ty != ctx_ty:
                    raise typy.TypeError(
                        "Variable {0} has conflicting types.".format(id), target)
        elif isinstance(target, ast.Subscript):
            target_value, slice_ = target.value, target.slice
            if isinstance(target_value, ast.Name):
                if isinstance(slice_, ast.Slice):
                    lower, upper, step = slice_.lower, slice_.upper, slice_.step
                    if lower is None and upper is not None and step is None:
                        id = target_value.id
                        variables = ctx.variables
                        cur_asc_ty = ctx.fn.static_env.eval_expr_ast(upper)
                        if isinstance(cur_asc_ty, typy.Type):
                            try:
                                ctx_ty = variables[id]
                            except KeyError: pass
                            else:
                                if cur_asc_ty != ctx_ty:
                                    raise typy.TypeError(
                                        "Variable {0} has conflicting types.".format(target_value.id), target)
                            if asc_ty is None: asc_ty = cur_asc_ty
                            elif asc_ty != cur_asc_ty:
                                raise typy.TypeError(
                                    "Variable {0} has conflicting types.".format(target_value.id), target)
                        else:
                            raise typy.TypeError(
                                "Variable type ascription is not a type.", upper)
        else:
            raise typy.TypeError(
                "Form not supported for assignment.", target)
    return asc_ty 

def _update_targets(ctx, targets, ty):
    for target in targets:
        if isinstance(target, ast.Name):
            ctx.variables[target.id] = ty
        elif isinstance(target, ast.Subscript):
            ctx.variables[target.value.id] = ty
