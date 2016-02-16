"""typy product types"""
import ast 

import six
import ordereddict

import typy
import typy.util
import typy.util.astx as astx

import _boolean

#
# tpl
#

class tpl(typy.Type):
    @classmethod
    def init_idx(cls, idx):
        return ordereddict.OrderedDict(_normalize_tuple_idx(idx)) 

    @classmethod
    def init_inc_idx(cls, inc_idx):
        if inc_idx == Ellipsis:
            return inc_idx
        else:
            raise typy.TypeFormationError(
                "Incomplete tuple type must have Ellipsis index.")

    def __str__(self):
        idx = self.idx
        return (
            "Tpl[" + 
            (str.join(", ", _idx_to_str(idx)) if len(idx) > 0 else "()") + 
            "]"
        )

    def ana_Tuple(self, ctx, e):
        elts = e.elts
        idx = self.idx

        n_elts, n_idx = len(elts), len(idx)
        if n_elts < n_idx:
            raise typy.TypeError(
                "Too few components provided.", e)
        elif n_elts > n_idx:
            raise typy.TypeError(
                "Too many components provided.", elts[n_idx])

        for elt, (_, ty) in zip(elts, idx.itervalues()):
            ctx.ana(elt, ty)

    @classmethod
    def syn_idx_Tuple(self, ctx, e, inc_idx):
        elts = e.elts
        idx = tuple(
            (i, ctx.syn(elt))
            for i, elt in enumerate(elts)
        )
        return idx

    def translate_Tuple(self, ctx, e):
        translation = astx.copy_node(e)
        translation.elts = tuple(
            ctx.translate(elt)
            for elt in e.elts)
        return translation 

    def ana_pat_Tuple(self, ctx, pat):
        elts = pat.elts
        idx = self.idx
        n_elts, n_idx = len(elts), len(idx)
        if n_elts < n_idx:
            raise typy.TypeError(
                "Too few components in tpl pattern.", pat)
        elif n_elts > n_idx:
            raise typy.TypeError(
                "Too many components in tpl pattern.", elts[n_idx])
        
        bindings = ordereddict.OrderedDict()
        n_bindings = 0
        for elt, (_, ty) in zip(elts, idx.itervalues()):
            elt_bindings = ctx.ana_pat(elt, ty)
            n_elt_bindings = len(elt_bindings)
            bindings.update(elt_bindings)
            if len(bindings) != n_bindings + n_elt_bindings:
                raise typy.TypeError("Duplicate variable in pattern.", pat)
            n_bindings = n_bindings + n_elt_bindings
        
        return bindings

    def translate_pat_Tuple(self, ctx, pat, scrutinee_trans):
        scrutinee_trans_copy = astx.copy_node(scrutinee_trans)
        elts = pat.elts
        idx = self.idx
        conditions = []
        binding_translations = ordereddict.OrderedDict()
        for elt, (n, ty) in zip(elts, idx.itervalues()):
            elt_scrutinee_trans = astx.make_Subscript_Num_Index(
                scrutinee_trans_copy,
                n)
            elt_condition, elt_binding_translations = ctx.translate_pat(
                elt, elt_scrutinee_trans)
            conditions.append(elt_condition)
            binding_translations.update(elt_binding_translations)
        condition = ast.BoolOp(
            op=ast.And(),
            values=conditions)
        return (condition, binding_translations)

    def ana_Dict(self, ctx, e):
        keys, values = e.keys, e.values
        idx = self.idx
        n_keys, n_idx = len(keys), len(idx)
        if n_keys < n_idx:
            raise typy.TypeError(
                "Too few components provided.", e)
        elif n_keys > n_idx:
            raise typy.TypeError(
                "Too many components provided.", e)

        used_labels = set()
        for key, value in zip(keys, values):
            label = ctx.fn.static_env.eval_expr_ast(key)
            if label in used_labels:
                raise typy.TypeError(
                    "Duplicate label: " + str(label), key)
            try:
                (_, ty) = idx[label]
            except KeyError:
                raise typy.TypeError(
                    "Invalid label: " + str(label), key)
            used_labels.add(label)
            key.evaluated = label
            ctx.ana(value, ty)

    @classmethod
    def syn_idx_Dict(self, ctx, e, inc_idx):
        keys, values = e.keys, e.values
        idx = ordereddict.OrderedDict()
        for key, value in zip(keys, values):
            label = ctx.fn.static_env.eval_expr_ast(key)
            if isinstance(label, six.string_types):
                if len(label) == 0:
                    raise typy.TypeError(
                        "String label must be non-empty.", key)
            elif isinstance(label, (int, long)):
                if label < 0:
                    raise typy.TypeError(
                        "Integer label must be non-negative.", key)
            else:
                raise typy.TypeError(
                    "Label must be string or integer.", key)
            if label in idx:
                raise typy.TypeError(
                    "Duplicate label: " + str(label), key)
            ty = ctx.syn(value)
            idx[label] = (label, ty)
            key.evaluated = label
        return tuple(idx.itervalues())

    def translate_Dict(self, ctx, e):
        keys, values = e.keys, e.values
        idx = self.idx
        elt_translation = []
        idx_mapping = []
        for key, value in zip(keys, values):
            label = key.evaluated
            elt_translation.append(ctx.translate(value))
            idx_mapping.append(idx[label][0])
        arg_translation = ast.Tuple(elts=elt_translation)

        return ast.copy_location(_translation(idx_mapping, arg_translation), e)

    def ana_Call_constructor(self, ctx, e):
        id = e.func.id
        if id != 'X':
            raise typy.TypeError("tpl only supports the X constructor")
        if e.starargs is not None:
            raise typy.TypeError("No support for starargs", e)
        if e.kwargs is not None:
            raise typy.TypeError("No support for kwargs", e)

        idx = self.idx
        args = e.args
        keywords = e.keywords

        # check counts
        n_idx = len(idx)
        n_args, n_keywords = len(args), len(keywords)
        n_elts = n_args + n_keywords
        if n_elts < n_idx:
            raise typy.TypeError("Too few elements.", e)
        elif n_elts > n_idx:
            raise typy.TypeError("Too many elements.", e)

        # process non-keywords
        for i, arg in enumerate(args):
            try:
                (_, ty) = idx[i]
            except KeyError:
                raise typy.TypeError("No component labeled " + str(i), arg)
            ctx.ana(arg, ty)

        # process keywords
        for keyword in keywords:
            label = keyword.arg
            try:
                (_, ty) = idx[label]
            except KeyError:
                raise typy.TypeError("No component labeled " + arg, arg)
            value = keyword.value
            ctx.ana(value, ty)

    @classmethod
    def syn_idx_Call_constructor(self, ctx, e, inc_idx):
        id = e.func.id
        if id != 'X':
            raise typy.TypeError("tpl only supports the X constructor")
        if e.starargs is not None:
            raise typy.TypeError("No support for starargs", e)
        if e.kwargs is not None:
            raise typy.TypeError("No support for kwargs", e)

        args = e.args
        keywords = e.keywords

        idx = []

        # process non-keywords
        for i, arg in enumerate(args):
            idx.append((i, ctx.syn(arg)))

        # process keywords
        for keyword in keywords:
            label = keyword.arg
            ty = ctx.syn(keyword.value)
            idx.append((label, ty))

        return tuple(idx)

    def translate_Call_constructor(self, ctx, e):
        args, keywords = e.args, e.keywords
        idx = self.idx

        elt_translation = []
        idx_mapping = []
        for i, arg in enumerate(args):
            elt_translation.append(ctx.translate(arg))
            idx_mapping.append(idx[i][0])
        for keyword in keywords:
            label = keyword.arg
            value = keyword.value
            elt_translation.append(ctx.translate(value))
            idx_mapping.append(idx[label][0])
        arg_translation = ast.Tuple(elts=elt_translation)

        return ast.copy_location(_translation(idx_mapping, arg_translation), e)

    def syn_Attribute(self, ctx, e):
        idx = self.idx
        attr = e.attr
        try:
            (_, ty) = idx[attr]
        except KeyError:
            raise typy.TypeError("Cannot project component labeled " + attr, e)
        return ty 

    def translate_Attribute(self, ctx, e):
        (n, _) = self.idx[e.attr]
        return ast.copy_location(ast.Subscript(
            value=ctx.translate(e.value),
            slice=ast.Num(n=n),
            ctx=ast.Load()
        ), e)

    def syn_Subscript(self, ctx, e):
        slice_ = e.slice
        if not isinstance(slice_, ast.Index):
            raise typy.TypeError("Must provide a single label.", slice_)
        value = slice_.value
        label = ctx.fn.static_env.eval_expr_ast(value)
        try:
            (_, ty) = self.idx[label]
        except KeyError:
            raise typy.TypeError("Cannot project component labeled " + str(label), e)
        value.evaluated = label
        return ty

    def translate_Subscript(self, ctx, e):
        value = e.value 
        label = e.slice.value.evaluated
        (n, _) = self.idx[label]
        return ast.copy_location(ast.Subscript(
            value=ctx.translate(value),
            slice=ast.Num(n=n),
            ctx=ast.Load()
        ), e)

    def syn_Compare(self, ctx, e):
        left, ops, comparators = e.left, e.ops, e.comparators
        for op in ops:
            if isinstance(op, (ast.Eq, ast.NotEq)):
                if not len(self.idx) == 0:
                    raise typy.TypeError("Can only compare unit values for equality.", e)
            elif not isinstance(op, (ast.Is, ast.IsNot)):
                raise typy.TypeError("Invalid comparison operator.", op)

        for e_ in typy.util.tpl_cons(left, comparators):
            if hasattr(e_, "match"): 
                continue # already synthesized
            ctx.ana(e_, self)

        return _boolean.boolean

    def translate_Compare(self, ctx, e):
        translation = astx.copy_node(e)
        translation.left = ctx.translate(e.left)
        translation.comparators = tuple(
            ctx.translate(comparator)
            for comparator in e.comparators)
        return translation

    # TODO: x + y
    # TODO: x - "label"
    # TODO: x - ("l1", "l2", "l3")
    # TODO: x % "label"
    # TODO: x % ("l1", "l2", "l3")
    # TODO: multi-projection, e.g. x['l1', 'l2', 'l3']

def _normalize_tuple_idx(idx):
    if not isinstance(idx, tuple):
        idx = (idx,)
    used_labels = set()
    for i, component in enumerate(idx):
        if isinstance(component, typy.Type):
            if i in used_labels:
                raise typy.TypeFormationError(
                    "Duplicate label: " + str(i))
            used_labels.add(i)
            yield (i, (i, component))
            continue
        elif isinstance(component, slice):
            label = component.start
            ty = component.stop
        elif isinstance(component, tuple):
            if len(component) != 2:
                raise typy.TypeFormationError(
                    "Tuple component must have two components.")
            label = component[0]
            ty = component[1]
        else:
            raise typy.TypeFormationError(
                "Invalid component definition.")

        if isinstance(label, six.string_types):
            if len(label) == 0:
                raise typy.TypeFormationError(
                    "String label must be non-empty.")
        elif isinstance(label, (int, long)):
            if label < 0:
                raise typy.TypeFormationError(
                    "Integer label must be non-negative.")
        else:
            raise typy.TypeFormationError(
                "Label must be a string or integer.")
        if label in used_labels:
            raise typy.TypeFormationError(
                "Duplicate label: " + str(i))
        used_labels.add(label)

        if not isinstance(ty, typy.Type):
            raise typy.TypeFormationError(
                "Component labeled " + label + " has invalid type specification.")

        yield (label, (i, ty))

def _idx_to_str(idx):
    label_seen = False
    for label, (i, ty) in idx.iteritems():
        if i == label:
            if not label_seen:
                yield str(ty)
                continue
        else:
            label_seen = True
        yield repr(label) + " : " + str(ty)

def _translation(idx_mapping, arg_translation):
    lambda_translation = ast.Lambda(
        args=ast.arguments(
            args=[ast.Name(id='x', ctx=ast.Param())],
            vararg=None,
            kwarg=None,
            defaults=[]),
        body=ast.Tuple(
            elts=list(
                ast.Subscript(
                    value=ast.Name(
                        id='x',
                        ctx=ast.Load()),
                    slice=ast.Index(
                        value=ast.Num(n=n)),
                    ctx=ast.Load())
                for n in idx_mapping
            ),
            ctx=ast.Load()
        )
    )
    return ast.Call(
        func=lambda_translation,
        args=[arg_translation],
        keywords=[],
        starargs=[],
        kwargs=None
    )

unit = tpl[()]
