"""typy product types"""
import ast 

import six
import ordereddict

import typy
import typy.util
import typy.util.astx as astx

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

    def ana_Tuple(self, ctx, e):
        elts = e.elts
        idx = self.idx

        n_elts, n_idx = len(elts), len(idx)
        if n_elts < n_idx:
            raise typy.TypeError(
                "Too few components provided.", e)
        elif n_elts > n_idx:
            raise typy.TypeError(
                "Too many components provided.", elts[n_elts])

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
        idx = { }
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
        return ast.copy_location(ast.Call(
            func=lambda_translation,
            args=[arg_translation],
            keywords=[],
            starargs=[],
            kwargs=None
        ), e)

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
