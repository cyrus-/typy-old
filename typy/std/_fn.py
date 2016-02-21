"""typy functions"""
import ast

import ordereddict
_odict = ordereddict.OrderedDict

import typy
import typy.util 
import typy.util.astx as astx

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
        # ctx.variables is a dict stack mapping identifiers to 
        # a pair consisting of the translation of the identifier and its type
        ctx.variables = typy.util.DictStack()
        ctx.variables.push({})

    @classmethod
    def push_bindings(cls, ctx, bindings):
        variable_update = _odict(
            (id, (ctx.generate_fresh_id(id), ty))
            for (id, ty) in bindings.iteritems())
        ctx.variables.push(variable_update)
        return variable_update

    @classmethod
    def push_variable_update(cls, ctx, variable_update):
        ctx.variables.push(variable_update)

    @classmethod
    def pop_bindings(cls, ctx):
        ctx.variables.pop()

    @classmethod
    def pop_variable_update(cls, ctx):
        ctx.variables.pop()

    def ana_FunctionDef_toplevel(self, ctx, tree):
        args = tree.args
        body = tree._post_docstring_body
        (arg_types, return_type) = self.idx

        tree.uniq_id = _setup_recursive_fn(ctx, self, tree.name)
        arg_names = tuple(_setup_args(ctx, args, arg_types, tree))

        if len(body) > 0:
            sig_idx = _process_function_signature(body[0], arg_names, ctx.fn.static_env)
            if sig_idx is not None:
                if (sig_idx[0] != arg_types) \
                        or (sig_idx[1] != Ellipsis and sig_idx[1] != return_type):
                    raise typy.TypeError(
                        "Function signature and function ascription do not match.", 
                        body[0])
                body = tree._post_sig_body = body[1:]
            else:
                tree._post_sig_body = body

        if len(body) == 0:
            raise typy.TypeError("Function body is empty.", tree)

        block = tree.block = Block(body)
        block.ana(ctx, return_type)

    @classmethod
    def syn_idx_FunctionDef_toplevel(cls, ctx, tree, inc_ty):
        args = tree.args 
        body = tree._post_docstring_body
        inc_idx = inc_ty.inc_idx

        if len(body) > 0:
            arg_names = astx._get_arg_names(args)
            sig_idx = _process_function_signature(body[0], arg_names, ctx.fn.static_env)
            if inc_idx == Ellipsis:
                if sig_idx is None:
                    if len(arg_names) == 0:
                        inc_idx = ((), Ellipsis)
                        tree._post_sig_body = body
                    else:
                        raise typy.TypeError("Missing argument signature.", tree)
                else:
                    inc_idx = sig_idx
                    body = tree._post_sig_body = body[1:]
            else:
                if sig_idx is None:
                    tree._post_sig_body = body
                else:
                    if inc_idx[0] != sig_idx[0]:
                        raise typy.TypeError(
                            "Argument signature and ascription do not match.",
                            body[0])
                    inc_idx = sig_idx
                    body = tree._post_sig_body = body[1:]

        if len(body) == 0:
            raise typy.TypeError("Function body is empty.", tree)

        (arg_types, return_type) = inc_idx
        if return_type != Ellipsis:
            fn_ty = cls[arg_types, return_type]
        else:
            fn_ty = None
        tree.uniq_id = _setup_recursive_fn(ctx, fn_ty, tree.name)
        _setup_args(ctx, args, arg_types, tree)
        
        block = tree.block = Block(body)
        if return_type == Ellipsis:
            return_type = block.syn(ctx)
        else:
            block.ana(ctx, return_type)

        return (arg_types, return_type)

    def translate_FunctionDef_toplevel(self, ctx, tree):
        # body = tree._post_sig_body
        # if len(body) == 0:
        #     body_translation.append(ast.Return(ast.Tuple(elts=[], ctx=ast.Load())))
        # else:
        #     ctx.translate_block(body)
        
        # return ast.FunctionDef(
        #     name=tree.name,
        #     args=astx.deep_copy_node(tree.args),
        #     body=body_translation,
        #     decorator_list=[])
        pass

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
            (uniq_id, ty) = variables[id]
            e.uniq_id = uniq_id
            if ty is None:
                raise typy.TypeError("Variable has no available type: " + id, e)
            return ty
        except KeyError:
            raise typy.TypeError(
                "Variable not found in context.", e)

    def translate_Name(cls, ctx, e):
        translation = astx.copy_node(e)
        translation.id = e.uniq_id
        return translation

    @classmethod
    def check_Assign(cls, ctx, stmt):
        targets, value = stmt.targets, stmt.value
        asc = _get_asc(ctx, targets)
        if asc is None:
            ty = ctx.syn(value)
        elif isinstance(asc, typy.Type):
            ctx.ana(value, asc)
            ty = asc
        elif isinstance(asc, typy.IncompleteType):
            ty = ctx.ana_intro_inc(value, asc)
        else:
            raise typy.UsageError("Invalid ascription")
        _ana_patterns(ctx, targets, ty)

    def translate_Assign(self, ctx, stmt):
        targets, value = stmt.targets, stmt.value

        value_translation = ctx.translate(value)

        scrutinee_trans = ast.Name(
            id='__typy_let_scrutinee__',
            ctx=ast.Load())
        target_translation_data = tuple(_target_translation_data(
            ctx, 
            targets, 
            scrutinee_trans))

        try:
            for (condition, binding_translations), _ in target_translation_data:
                if astx.cond_vacuously_true(condition):
                    for binding_translation in binding_translations.itervalues():
                        if binding_translation != scrutinee_trans:
                            raise _NotSimpleAssignment(0)
                else:
                    raise _NotSimpleAssignment(1)
            return ast.Assign(
                targets=[
                    ast.Name(id=variables_update[id][0])
                    for (_, binding_translations), variables_update in
                    target_translation_data
                    for id in binding_translations.iterkeys() 
                ],
                value=value_translation)
        except _NotSimpleAssignment:
            translation = []
            scrutinee_assign = ast.Assign(
                targets=[scrutinee_trans],
                value=value_translation)
            translation.append(scrutinee_assign)
            for (condition, binding_translations), variables_update \
                    in target_translation_data:
                translation.append(ast.If(
                    test=condition,
                    body=list(
                        _translate_binding_translations(
                            binding_translations, variables_update)),
                    orelse=[astx.stmt_Raise_Exception_string("Match failure.")]))
            return translation

        # translation = []
        # value_assign = ast.Assign(
        #   targets=[value_tmp],
        #    value=value_translation)
        #translation.append(value_assign)
        #for target_trans in _translate_targets(ctx, targets, value_tmp):
        #    translation.extend(target_trans)
        #return translation

    @classmethod
    def check_Expr(cls, ctx, stmt):
        ctx.syn(stmt.value)

    def translate_Expr(self, ctx, stmt):
        return ast.Expr(ctx.translate(stmt.value))

    def syn_Call(self, ctx, e):
        args, keywords, starargs, kwargs = e.args, e.keywords, e.starargs, e.kwargs
        if len(keywords) != 0 or kwargs is not None:
            raise typy.TypeError("Keyword arguments are not supported.",
                e)
        if starargs is not None:
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

class Block(object):
    """A block is a sequence of BlockExpr's"""
    def __init__(self, stmts):
        self.stmts = stmts
        self.block_exprs = Block._block_exprs(stmts)

    @classmethod
    def _block_exprs(cls, stmts):
        cur_bindings = []
        for stmt in stmts:
            if isinstance(stmt, ast.Assign):
                cur_bindings.append(BlockAssignBinding(stmt))
            elif isinstance(stmt, ast.Expr):
                block_expr = BlockExprExpr(stmt)
                if len(cur_bindings) == 0:
                    yield block_expr
                else:
                    yield BlockLetExpr(cur_bindings, block_expr)
                    cur_bindings = []
            elif isinstance(stmt, ast.Pass):
                block_expr = BlockPassExpr(stmt)
                if len(cur_bindings) == 0:
                    yield block_expr
                else:
                    yield BlockLetExpr(cur_bindings, block_expr)
                    cur_bindings = []
            else:
                raise typy.TypeError("Statement form not supported.", stmt)
        if len(cur_bindings) != 0:
            raise typy.TypeError("Incomplete block expression.", stmt)

class BlockExpr(object):
    pass

class BlockLetExpr(BlockExpr):
    def __init__(self, bindings, in_expr):
        self.bindings = bindings
        self.in_expr = in_expr

class BlockExprExpr(BlockExpr):
    def __init__(self, stmt):
        self.stmt = stmt

class BlockPassExpr(BlockExpr):
    def __init__(self, stmt):
        self.stmt = stmt

class BlockBinding(object):
    pass

class BlockAssignBinding(BlockBinding):
    def __init__(self, stmt):
        self.stmt = stmt

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
            else: 
                raise typy.TypeFormationError(
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

def _setup_recursive_fn(ctx, fn_ty, name):
    variables = ctx.variables
    uniq_id = ctx.generate_fresh_id(name)
    variables[name] = (uniq_id, fn_ty)
    return uniq_id

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
    if arg_types is None: 
        return None
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
                    "Function specifies argument name {0}, but function signature specifies argument name {1}." # noqa
                    .format(arg_name, key), key)
            arg_types.append(static_env.eval_expr_ast(value))
    elif isinstance(value, ast.Set):
        elts = value.elts
        n_elts = len(elts)
        n_args = len(arg_names)
        if n_elts != n_args:
            raise typy.TypeError(
                "Function specifies {0} arguments, but function"
                "signature specifies {1} arguments."
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
    if len(args.defaults) != 0:
        raise typy.TypeError("Defaults are not supported.", tree)

    variables = ctx.variables
    arguments = args.args
    n_args, n_arg_types = len(arguments), len(arg_types)
    if n_args != n_arg_types:
        raise typy.TypeError(
            "Type specifies {0} arguments but function has {1}.".format(
                n_arg_types, n_args), 
            tree)
    for arg, arg_type in zip(arguments, arg_types):
        if not isinstance(arg, ast.Name):
            raise typy.TypeError("Argument must be an identifier.", arg)
        arg_id = arg.id
        uniq_id = ctx.generate_fresh_id(arg_id)
        arg.uniq_id = uniq_id
        variables[arg_id] = (uniq_id, arg_type)
        yield arg_id

def _get_asc(ctx, targets):
    asc = None
    for target in targets:
        if isinstance(target, (ast.Name, ast.Tuple, ast.Dict, ast.List)):
            continue
        elif isinstance(target, ast.Subscript):
            target_value, slice_ = target.value, target.slice
            if isinstance(target_value, ast.Name):
                id = target_value.id
                if id == "let":
                    if len(targets) != 1:
                        raise typy.TypeError(
                            "Cannot use multiple assignment form with let.", targets)
                    if isinstance(slice_, ast.Index):
                        continue
                    elif isinstance(slice_, ast.Slice):
                        pat, asc_ast, step = slice_.lower, slice_.upper, slice_.step
                        if pat is not None and asc_ast is not None and step is None:
                            cur_asc = _process_asc_ast(ctx, asc_ast)
                            if asc is None:
                                asc = cur_asc
                            elif asc != cur_asc:
                                raise typy.TypeError("Inconsistent ascriptions", asc_ast)
                            continue
                        else:
                            raise typy.TypeError("Invalid let format.", slice_)
                    else:
                        raise typy.TypeError("Invalid let format.", slice_)
            if not isinstance(target_value, (ast.Name, ast.Tuple, ast.Dict, ast.List)):
                raise typy.TypeError("Unknown assignment form.", target_value)
            if isinstance(slice_, ast.Slice):
                lower, asc_ast, step = slice_.lower, slice_.upper, slice_.step
                if lower is None and asc_ast is not None and step is None:
                    cur_asc = _process_asc_ast(ctx, asc_ast)
                    if asc is None:
                        asc = cur_asc
                    elif asc != cur_asc:
                        raise typy.TypeError("Inconsistent ascriptions", asc_ast)
                else:
                    raise typy.TypeError("Invalid ascription format.", slice_)
        else:
            raise typy.TypeError("Unknown assignment form.", target)
    return asc

def _process_asc_ast(ctx, asc_ast):
    asc = ctx.fn.static_env.eval_expr_ast(asc_ast)
    if (isinstance(asc, typy.Type) or 
            isinstance(asc, typy.IncompleteType)):
        return asc
    elif issubclass(asc, typy.Type):
        return asc[...]
    else:
        raise typy.TypeError("Invalid ascription.", asc_ast)

def _ana_patterns(ctx, targets, ty):
    for target in targets:
        if isinstance(target, (ast.Name, ast.Tuple, ast.Dict, ast.List)):
            ctx.ana_pat(target, ty)
            _process_bindings(ctx, target)
        elif isinstance(target, ast.Subscript):
            target_value, slice_ = target.value, target.slice
            if isinstance(target_value, ast.Name):
                id = target_value.id
                if id == "let":
                    if isinstance(slice_, ast.Index):
                        pat = slice_.value
                        ctx.ana_pat(pat, ty)
                        _process_bindings(ctx, pat)
                        continue
                    elif isinstance(slice_, ast.Slice):
                        pat = slice_.lower
                        ctx.ana_pat(pat, ty)
                        _process_bindings(ctx, pat)
                        continue
            ctx.ana_pat(target_value, ty)
            _process_bindings(ctx, target_value)

def _process_bindings(ctx, pat):
    bindings = pat.bindings
    variables_update = pat.variables_update = {}
    for id, ty in bindings.iteritems():
        uniq_id = ctx.generate_fresh_id(id)
        variables_item = (uniq_id, ty)
        variables_update[id] = variables_item
        ctx.variables[id] = variables_item

def _target_translation_data(ctx, targets, scrutinee_trans):
    for target in targets:
        if isinstance(target, (ast.Name, ast.Tuple, ast.Dict, ast.List)):
            yield (ctx.translate_pat(target, scrutinee_trans), target.variables_update)
        elif isinstance(target, ast.Subscript):
            target_value, slice_ = target.value, target.slice
            if isinstance(target_value, ast.Name):
                id = target_value.id
                if id == "let":
                    if isinstance(slice_, ast.Index):
                        pat = slice_.value
                        yield (ctx.translate_pat(pat, scrutinee_trans),
                               pat.variables_update)
                        continue
                    elif isinstance(slice_, ast.Slice):
                        pat = slice_.lower
                        yield (ctx.translate_pat(pat, scrutinee_trans),
                               pat.variables_update)
                        continue
            yield (ctx.translate_pat(target_value, scrutinee_trans), 
                   target_value.variables_update)

def _translate_binding_translations(binding_translations, variables_update):
    if len(binding_translations) == 0:
        yield ast.Pass()
    else:
        for id, translation in binding_translations.iteritems():
            uniq_id = variables_update[id][0]
            yield ast.Assign(
                targets=[ast.Name(id=uniq_id)],
                value=translation)

class _NotSimpleAssignment(Exception):
    pass

