"""typy functions"""
import ast

import ordereddict
_odict = ordereddict.OrderedDict

import typy
import typy.util 
import typy.util.astx as astx

import _product

#
# fn
#

class fn(typy.FnType):
    @classmethod
    def init_idx(cls, idx):
        if isinstance(idx, tuple):
            idx = cls._normalize_fn_idx(idx)
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
            inc_idx = cls._normalize_fn_idx(inc_idx)
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
    def _normalize_fn_idx(cls, idx):
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

    @classmethod
    def preprocess_FunctionDef_toplevel(cls, fn, tree):
        body = tree.body
        (docstring, post_docstring_body) = cls._extract_docstring(body)
        fn.__doc__ = fn.func_doc = docstring
        tree._post_docstring_body = post_docstring_body

    @classmethod
    def _extract_docstring(cls, body):
        docstring_loc = body[0]
        if isinstance(docstring_loc, ast.Expr):
            value = docstring_loc.value
            if isinstance(value, ast.Str):
                return (value.s, body[1:])
        return (None, body)

    @classmethod
    def init_ctx(cls, ctx):
        # ctx.variables is a dict stack mapping identifiers to 
        # a pair consisting of the translation of the identifier 
        # and its type
        ctx.variables = typy.util.DictStack()
        ctx.variables.push({})

    def ana_FunctionDef_toplevel(self, ctx, tree):
        args = tree.args
        body = tree._post_docstring_body
        (arg_types, return_type) = self.idx

        tree.uniq_id = fn._setup_recursive_fn(ctx, self, tree.name)
        arg_names = tuple(fn._setup_args(ctx, args, arg_types, tree))

        if len(body) > 0:
            sig_idx = fn._process_function_signature(
                body[0], arg_names, ctx.fn.static_env)
            if sig_idx is not None:
                if (sig_idx[0] != arg_types) \
                        or (sig_idx[1] != Ellipsis 
                            and sig_idx[1] != return_type):
                    raise typy.TypeError(
                        "Function signature and function ascription do not match.", 
                        body[0])
                body = tree._post_sig_body = body[1:]
            else:
                tree._post_sig_body = body

        if len(body) == 0:
            raise typy.TypeError("Function body is empty.", tree)

        body_block = tree.body_block = Block.from_stmts(body)
        body_block.ana(ctx, return_type)

    @classmethod
    def syn_idx_FunctionDef_toplevel(cls, ctx, tree, inc_ty):
        args = tree.args 
        body = tree._post_docstring_body
        inc_idx = inc_ty.inc_idx

        if len(body) > 0:
            arg_names = astx._get_arg_names(args)
            sig_idx = cls._process_function_signature(body[0], arg_names, ctx.fn.static_env)
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
        tree.uniq_id = cls._setup_recursive_fn(ctx, fn_ty, tree.name)
        tuple(cls._setup_args(ctx, args, arg_types, tree))
        
        body_block = tree.body_block = Block.from_stmts(body)
        if return_type == Ellipsis:
            return_type = body_block.syn(ctx)
        else:
            body_block.ana(ctx, return_type)

        return (arg_types, return_type)

    @classmethod
    def _process_function_signature(cls, stmt, arg_names, static_env):
        return_type = Ellipsis
        if isinstance(stmt, ast.Expr):
            value = stmt.value
            if isinstance(value, ast.BinOp):
                left, op, right = value.left, value.op, value.right
                if isinstance(op, ast.RShift):
                    arg_types = cls._process_argument_signature(left, arg_names, static_env)
                    return_type = static_env.eval_expr_ast(right)
                else:
                    return None
            elif isinstance(value, ast.Dict) or isinstance(value, ast.Set):
                arg_types = cls._process_argument_signature(value, arg_names, static_env)
            else:
                return None
        else:
            return None
        if arg_types is None: 
            return None
        return (arg_types, return_type)

    @classmethod
    def _process_argument_signature(cls, value, arg_names, static_env):
        arg_types = []
        if isinstance(value, ast.Dict):
            keys, values = value.keys, value.values
            n_keys = len(keys)
            n_args = len(arg_names)
            if n_keys != n_args:
                raise typy.TypeError(
                    "Function specifies {0} arguments, "
                    "but function signature specifies {1} arguments."
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

    @classmethod
    def _setup_recursive_fn(cls, ctx, fn_ty, name):
        uniq_id = ctx.generate_fresh_id(name)
        if fn_ty is not None:
            ctx.variables[name] = (uniq_id, fn_ty)
        return uniq_id

    @classmethod
    def _setup_args(cls, ctx, args, arg_types, tree):
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

    def translate_FunctionDef_toplevel(self, ctx, tree):
        body_block = tree.body_block
        body_block_translation = body_block.translate(ctx)
        argument_translation = ast.arguments(
            args=[
                ast.Name(id=arg.uniq_id)
                for arg in tree.args.args
            ],
            vararg=None,
            kwarg=None,
            defaults=[])
        return ast.FunctionDef(
            name=tree.uniq_id,
            args=argument_translation,
            body=body_block_translation,
            decorator_list=[])

    @classmethod
    def syn_Name(cls, ctx, e):
        id = e.id
        try:
            (uniq_id, ty) = ctx.variables[id]
        except KeyError:
            raise typy.TypeError(
                "Variable not found in context: " + id, e)
        e.uniq_id = uniq_id
        return ty

    def translate_Name(cls, ctx, e):
        translation = astx.copy_node(e)
        translation.id = e.uniq_id
        return translation

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

    @classmethod
    def ana_match_expr(cls, ctx, e, ty):
        elts = e.left.elts
        n_elts = len(elts)
        if n_elts == 0:
            raise TypeError("Scrutinee missing.", e)
        elif n_elts > 1:
            raise TypeError("Too many scrutinees.", e)
        scrutinee = elts[0]
        scrutinee_ty = ctx.syn(scrutinee)
        rule_dict_lit = e.comparators[0]
        rules = zip(rule_dict_lit.keys, rule_dict_lit.values)
        for (pat, branch) in rules:
            bindings = ctx.ana_pat(pat, scrutinee_ty)
            ctx_update = pat.ctx_update = cls._pat_ctx_update(ctx, bindings)
            ctx.variables.push(ctx_update)
            ctx.ana(branch, ty)
            ctx.variables.pop()

    @classmethod
    def syn_match_expr(cls, ctx, e):
        elts = e.left.elts
        n_elts = len(elts)
        if n_elts == 0:
            raise TypeError("Scrutinee missing.", e)
        elif n_elts > 1:
            raise TypeError("Too many scrutinees.", e)
        scrutinee = elts[0]
        scrutinee_ty = ctx.syn(scrutinee)
        rule_dict = e.comparators[0]
        rules = zip(rule_dict.keys, rule_dict.values)
        syn_ty = None
        for (pat, branch) in rules:
            bindings = ctx.ana_pat(pat, scrutinee_ty)
            ctx_update = pat.ctx_update = cls._pat_ctx_update(ctx, bindings)
            ctx.variables.push(ctx_update)
            branch_ty = ctx.syn(branch)
            ctx.variables.pop()
            if syn_ty is None:
                syn_ty = branch_ty
            else:
                if syn_ty != branch_ty:
                    raise TypeError("Inconsistent branch types.", branch)
        return syn_ty

    @classmethod
    def _pat_ctx_update(cls, ctx, bindings):
        return dict(
            (id, (ctx.generate_fresh_id(id), ty))
            for (id, ty) in bindings.iteritems())

    @classmethod
    def translate_match_expr(cls, ctx, e):
        scrutinee = e.left.elts[0]
        scrutinee_trans = ctx.translate(scrutinee)
        scrutinee_var = ast.Name(id="__typy_scrutinee__", ctx=ast.Load())
        rules = e.comparators[0]
        rules = zip(rules.keys, rules.values)
        rule_translations = tuple(cls._translate_rules(ctx, rules, scrutinee_var))
        if len(rule_translations) == 0:
            compiled_rules = astx.expr_Raise_Exception_string("Match failure.")
        else:
            rt_0 = rule_translations[0]
            rt_rest = rule_translations[1:]
            compiled_rules = cls._compile_rule(rt_0, rt_rest)
        translation = astx.make_simple_Call(
            astx.make_Lambda(('__typy_scrutinee__',), compiled_rules),
            [scrutinee_trans])
        return translation

    @classmethod
    def _translate_rules(cls, ctx, rules, scrutinee_trans):
        for (pat, branch) in rules:
            (condition, binding_translations) = ctx.translate_pat(pat, scrutinee_trans)
            if not pat.bindings.keys() == binding_translations.keys():
                raise typy.UsageError("All bindings must have translations.")
            for binding_translation in binding_translations.itervalues():
                if not isinstance(binding_translation, ast.expr):
                    raise typy.UsageError("Binding translation must be an expression.")
            ctx_update = pat.ctx_update
            ctx.variables.push(ctx_update)
            branch_translation = ctx.translate(branch)
            ctx.variables.pop()
            yield condition, binding_translations, ctx_update, branch_translation

    @classmethod
    def _compile_rule(cls, rule_translation, rest):
        test, binding_translations, ctx_update, branch_translation = rule_translation

        if len(binding_translations) == 0:
            body = branch_translation
        else:
            body_lambda = astx.make_Lambda(
                (ctx_update[id][0] 
                 for id in binding_translations.iterkeys()),
                branch_translation)
            body = astx.make_simple_Call(
                body_lambda, 
                binding_translations.values())

        if len(rest) == 0:
            orelse = astx.expr_Raise_Exception_string("Match failure.")
        else:
            orelse = cls._compile_rule(rest[0], rest[1:])

        return ast.IfExp(
            test=test,
            body=body,
            orelse=orelse)

class Block(object):
    def __init__(self, bindings, last_expr):
        self.bindings = bindings
        self.last_expr = last_expr

    @classmethod
    def from_stmts(cls, stmts):
        bindings = tuple(cls._yield_bindings(stmts))
        all_but_last = bindings[0:-1]
        last_binding = bindings[-1]
        if not isinstance(last_binding, BlockNoBinding):
            raise typy.TypeError(
                "Block does not end with an expression.",
                last_binding.stmt)
        return cls(all_but_last, last_binding.expr)

    @classmethod
    def _yield_bindings(cls, stmts):
        for stmt in stmts:
            if isinstance(stmt, ast.Assign):
                yield BlockAssignBinding(stmt)
            elif isinstance(stmt, ast.Expr):
                yield BlockNoBinding(BlockExprExpr(stmt))
            elif isinstance(stmt, ast.Pass):
                yield BlockNoBinding(BlockPassExpr(stmt))
            else:
                raise typy.TypeError("Statement form not supported.", stmt)

    def ana(self, ctx, ty):
        bindings = self.bindings
        for binding in bindings:
            binding.check_and_push(ctx)
        self.last_expr.ana(ctx, ty)
        for binding in bindings:
            binding.pop(ctx)

    def syn(self, ctx):
        bindings = self.bindings
        for binding in bindings:
            binding.check_and_push(ctx)
        ty = self.last_expr.syn(ctx)
        for binding in bindings:
            binding.pop(ctx)
        return ty

    def translate(self, ctx):
        translation = []
        for binding in self.bindings:
            translation.extend(binding.translate(ctx))
        translation.extend(self.last_expr.translate_return(ctx))
        return translation

class BlockBinding(object):
    def check_and_push(self, ctx):
        raise typy.UsageError("Missing implementation.")

    def pop(self, ctx):
        raise typy.UsageError("Missing implementation.")

    def translate(self, ctx):
        raise typy.UsageError("Missing implementation.")

class BlockNoBinding(object):
    def __init__(self, expr):
        self.expr = expr

    def check_and_push(self, ctx):
        self.expr.syn(ctx)

    def pop(self, ctx):
        pass

    def translate(self, ctx):
        return self.expr.translate_no_binding(ctx)

class BlockAssignBinding(BlockBinding):
    def __init__(self, stmt):
        print "ASSIGN BINDING"
        self.stmt = stmt

    def check_and_push(self, ctx):
        stmt = self.stmt
        targets, value = stmt.targets, stmt.value
        asc = self._get_asc(ctx, targets)
        print "GOT ASC"
        if asc is None:
            ty = ctx.syn(value)
        elif isinstance(asc, typy.Type):
            ctx.ana(value, asc)
            ty = asc
        elif isinstance(asc, typy.IncompleteType):
            ty = ctx.ana_intro_inc(value, asc)
        else:
            raise typy.UsageError("Unexpected ascription from _get_asc.")
        self._check_and_push_targets(ctx, targets, ty)

    def _get_asc(self, ctx, targets):
        asc = None
        for target in targets:
            if isinstance(target, (
                    ast.Name, 
                    ast.Tuple, 
                    ast.Dict, # Py3 only
                    ast.List)):
                # no ascription
                pass
            elif isinstance(target, ast.Subscript):
                target_value, slice_ = target.value, target.slice
                if isinstance(target_value, ast.Name):
                    id = target_value.id
                    if id == "let":
                        if len(targets) != 1:
                            raise typy.TypeError(
                                "Cannot use multiple assignment form with let.", targets)
                        if isinstance(slice_, ast.Index):
                            # no ascription
                            continue
                        elif isinstance(slice_, ast.Slice):
                            pat, asc_ast, step = slice_.lower, slice_.upper, slice_.step
                            if pat is not None and asc_ast is not None and step is None:
                                cur_asc = self._process_asc_ast(ctx, asc_ast)
                                if asc is None:
                                    asc = cur_asc
                                elif asc != cur_asc:
                                    raise typy.TypeError("Inconsistent ascriptions", asc_ast)
                                continue
                            else:
                                raise typy.TypeError("Invalid let format.", slice_)
                        else:
                            raise typy.TypeError("Invalid let format.", slice_)
                if isinstance(slice_, ast.Slice):
                    lower, asc_ast, step = slice_.lower, slice_.upper, slice_.step
                    if lower is None and asc_ast is not None and step is None:
                        cur_asc = self._process_asc_ast(ctx, asc_ast)
                        if asc is None:
                            asc = cur_asc
                        elif asc != cur_asc:
                            raise typy.TypeError("Inconsistent ascriptions", asc_ast)
                    else:
                        raise typy.TypeError("Invalid ascription format.", slice_)
                else:               
                    raise typy.TypeError("Invalid ascription format.", slice_)
            else:
                raise typy.TypeError("Unknown assignment form.", target)
        return asc

    def _process_asc_ast(self, ctx, asc_ast):
        asc = ctx.fn.static_env.eval_expr_ast(asc_ast)
        if (isinstance(asc, typy.Type) or 
                isinstance(asc, typy.IncompleteType)):
            return asc
        elif issubclass(asc, typy.Type):
            return asc[...]
        else:
            raise typy.TypeError("Invalid ascription.", asc_ast)

    def _check_and_push_targets(self, ctx, targets, ty):
        for target in targets:
            if isinstance(target, (
                    ast.Name,
                    ast.Tuple,
                    ast.Dict, # Py3 only
                    ast.List)):
                ctx.ana_pat(target, ty)
                self._push_pat_bindings(ctx, target)
            elif isinstance(target, ast.Subscript):
                target_value, slice_ = target.value, target.slice
                if isinstance(target_value, ast.Name):
                    id = target_value.id
                    if id == "let":
                        if isinstance(slice_, ast.Index):
                            # no ascription
                            pat = slice_.value
                            ctx.ana_pat(pat, ty)
                            self._push_pat_bindings(ctx, pat)
                            continue
                        elif isinstance(slice_, ast.Slice):
                            # ascription
                            # already valid by _get_asc
                            pat = slice_.lower
                            ctx.ana_pat(pat, ty)
                            self._push_pat_bindings(ctx, pat)
                            continue
                    ctx.ana_pat(target_value, ty)
                    self._push_pat_bindings(ctx, target_value)

    def _push_pat_bindings(self, ctx, pat):
        print "PUSHING STUFF"
        ctx_update = dict(
            (id, (ctx.generate_fresh_id(id), ty))
            for (id, ty) in pat.bindings.iteritems())
        print ctx_update
        pat.ctx_update = ctx_update
        ctx.variables.push(ctx_update)

    def pop(self, ctx):
        for target in self.stmt.targets:
            print "POPPING"
            ctx.variables.pop()

    def translate(self, ctx):
        stmt = self.stmt
        targets, value = stmt.targets, stmt.value

        value_translation = ctx.translate(value)

        scrutinee_trans = ast.Name(
            id='__typy_let_scrutinee__',
            ctx=ast.Load())
        target_translation_data = tuple(_target_translation_data(
            ctx, 
            targets, 
            scrutinee_trans))

        is_simple_assignment = True
        for (condition, binding_translations), _ in target_translation_data:
            if astx.cond_vacuously_true(condition):
                for binding_translation in binding_translations.itervalues():
                    if binding_translation != scrutinee_trans:
                        is_simple_assignment = False
                        break
            else:
                is_simple_assignment = False
                break

        if is_simple_assignment:
            return [ast.Assign(
                targets=[
                    ast.Name(id=ctx_update[id][0])
                    for (_, binding_translations), ctx_update in
                    target_translation_data
                    for id in binding_translations.iterkeys() 
                ],
                value=value_translation)]
        else:
            translation = []
            scrutinee_assign = ast.Assign(
                targets=[scrutinee_trans],
                value=value_translation)
            translation.append(scrutinee_assign)
            for (condition, binding_translations), ctx_update \
                    in target_translation_data:
                translation.append(ast.If(
                    test=condition,
                    body=list(
                        _translate_binding_translations(
                            binding_translations, ctx_update)),
                    orelse=[astx.stmt_Raise_Exception_string("Match failure.")]))
            return translation

class BlockExpr(object):
    def ana(self, ctx, ty):
        raise typy.UsageError("Missing implementation.")

    def syn(self, ctx):
        raise typy.UsageError("Missing implementation.")

    def translate_no_binding(self, ctx):
        raise typy.UsageError("Missing implementation.")

    def translate_return(self, ctx):
        raise typy.UsageError("Missing implementation.")

class BlockExprExpr(BlockExpr):
    def __init__(self, stmt):
        print "BLOCK EXPR"
        self.stmt = stmt

    def ana(self, ctx, ty):
        expr = self.stmt.value
        ctx.ana(expr, ty)

    def syn(self, ctx):
        expr = self.stmt.value
        return ctx.syn(expr)
    
    def translate_no_binding(self, ctx):
        return [ast.Expr(value=ctx.translate(self.stmt.value))]

    def translate_return(self, ctx):
        return [ast.Return(value=ctx.translate(self.stmt.value))]

class BlockPassExpr(BlockExpr):
    def __init__(self, stmt):
        self.stmt = stmt

    def ana(self, ctx, ty):
        unit = _product.unit
        if ty != unit:
            raise typy.TypeMismatchError(unit, ty, self.stmt)

    def syn(self, ctx):
        return _product.unit

    def translate_no_binding(self, ctx):
        return [ast.Pass()]

    def translate_return(self, ctx):
        return [ast.Return(value=ast.Tuple(elts=[]))]

def _target_translation_data(ctx, targets, scrutinee_trans):
    for target in targets:
        if isinstance(target, (ast.Name, ast.Tuple, ast.Dict, ast.List)):
            yield (ctx.translate_pat(target, scrutinee_trans), target.ctx_update)
        elif isinstance(target, ast.Subscript):
            target_value, slice_ = target.value, target.slice
            if isinstance(target_value, ast.Name):
                id = target_value.id
                if id == "let":
                    if isinstance(slice_, ast.Index):
                        pat = slice_.value
                        yield (ctx.translate_pat(pat, scrutinee_trans),
                               pat.ctx_update)
                        continue
                    elif isinstance(slice_, ast.Slice):
                        pat = slice_.lower
                        yield (ctx.translate_pat(pat, scrutinee_trans),
                               pat.ctx_update)
                        continue
            yield (ctx.translate_pat(target_value, scrutinee_trans), 
                   target_value.ctx_update)

def _translate_binding_translations(binding_translations, ctx_update):
    if len(binding_translations) == 0:
        yield ast.Pass()
    else:
        for id, translation in binding_translations.iteritems():
            uniq_id = ctx_update[id][0]
            yield ast.Assign(
                targets=[ast.Name(id=uniq_id)],
                value=translation)

