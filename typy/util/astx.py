"""Utilities for working with python's standard ast library"""
import ast 
import re

def copy_node(node, *args, **kwargs):
    """Shallow copies the provided ast node.

    Non-keyword arguments are set according to the order in the Python ast documentation.
    Keyword arguments are set explicitly.
    """
    cls = node.__class__
    new_node = cls()

    set_attrs = {}

    # non-keyword args
    for name, value in zip(cls._fields, args):
        set_attrs[name] = value

    # keyword args
    for name, value in kwargs.iteritems():
        set_attrs[name] = value

    # attributes
    for name, value in node.__dict__.iteritems():
        if name not in set_attrs:
            set_attrs[name] = value

    # apply set_attrs
    for name, value in set_attrs.iteritems():
        setattr(new_node, name, value)

    return new_node

def deep_copy_node(node, *args, **kwargs):
    """Deep copies the provided ast node.

    Non-keyword arguments are set according to the order in the Python ast documentation.

    Keyword arguments are set explicitly."""
    cls = node.__class__
    new_node = cls()

    set_attrs = {}

    # non-keyword args
    for name, value in zip(cls._fields, args):
        set_attrs[name] = value

    # keyword args
    for name, value in kwargs.iteritems():
        set_attrs[name] = value

    # deep copy attributes
    for name, value in node.__dict__.iteritems():
        if name not in set_attrs:
            if isinstance(value, ast.AST):
                set_attrs[name] = deep_copy_node(value)
            else:
                set_attrs[name] = value

    # apply set_attrs
    for name, value in set_attrs.iteritems():
        setattr(new_node, name, value)

    return new_node

def builtin_call(name, args):
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(
                id='__builtin__', ctx=ast.Load()), 
            attr=name, ctx=ast.Load()),
        args=args, 
        keywords=[], 
        starargs=None, 
        kwargs=None)


_name_re = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*$")
def is_identifier(id):
    return bool(_name_re.match(id))

def make_Lambda(arg_vars, body):
    return ast.Lambda(
        args=ast.arguments(
            args=[
                ast.Name(id=arg_var, ctx=ast.Param())
                for arg_var in arg_vars],
            vararg=None,
            kwarg=None,
            defaults=[]),
        body=body)

def make_simple_Call(func, args):
    return ast.Call(
        func=func,
        args=args,
        keywords=[],
        starargs=None,
        kwargs=None)

def expr_Raise_Exception_string(message):
    # hack: (_ for _ in ()).throw(Exception(message))
    return ast.Call(
        func=ast.Attribute(
            value=ast.GeneratorExp(
                elt=ast.Name(id='_', ctx=ast.Load()),
                generators=[
                    ast.comprehension(
                        target=ast.Name(id='_', ctx=ast.Store()),
                        iter=ast.Tuple(
                            elts=[], 
                            ctx=ast.Load()), 
                        ifs=[])]), 
            attr='throw', ctx=ast.Load()),
        args=[builtin_call('Exception', [ast.Str(s=message)])],
        keywords=[],
        starargs=None,
        kwargs=None)

def make_binary_And(left, right):
    return ast.BoolOp(
        op=ast.And(),
        values=[left, right])

def make_Attribute(value, attr):
    return ast.Attribute(
        value=value,
        attr=attr,
        ctx=ast.Load())

