"""Utilities for working with python's standard ast library"""

def copy_node(node, *args, **kwargs):
	"""Shallow copies the provided ast node.

	Non-keyword arguments are set according to the order in the Python ast documentation.
	Keyword arguments are set explicitly.
	"""
    cls = node.__class__
    new_node = cls()

    # shallow copy attributes
    for name, value in node.__dict__.iteritems():
        setattr(new_node, name, value)            
    
    # non-keyword args
    for name, value in zip(cls._fields, args):
        setattr(new_node, name, value)
    
    # keyword args
    for name, value in kwargs.iteritems():
        setattr(new_node, name, value)
        
    return new_node
