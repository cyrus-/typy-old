"""Utilities for working with python's standard ast library"""
import ast 

def copy_node(node, *args, **kwargs):
    """Shallow copies the provided ast node.

    Non-keyword arguments are set according to the order in the Python ast documentation.
    Keyword arguments are set explicitly.
    """
    cls = node.__class__
    new_node = cls()

    set_attrs = { }

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

    set_attrs = { }

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
