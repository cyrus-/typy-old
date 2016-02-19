"""Useful utilities for working with typy."""

class DictStack(object):
    def __init__(self, stack=None):
        if stack is None:
            stack = []
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
            if key in d: 
                return True
        return False 

def tpl_cons(hd, tl):
    yield hd
    for x in tl:
        yield x 

def _contains_ellipsis(idx):
    if idx is Ellipsis: 
        return True
    elif isinstance(idx, tuple):
        for item in idx:
            if item is Ellipsis: 
                return True
    return False 

