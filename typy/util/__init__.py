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

def contains_ellipsis(idx):
    if idx is Ellipsis: 
        return True
    elif isinstance(idx, tuple):
        for item in idx:
            if item is Ellipsis: 
                return True
    return False 

# 
# odict
# 

import ordereddict
odict = ordereddict.OrderedDict 
# may use a different library later, so only use typy.util.odict, 
# not ordereddict.OrderedDict directly

def odict_idx_of(od, key):
    for idx, k in enumerate(od.iterkeys()):
        if k == key:
            return idx
    raise KeyError(key)

def odict_lookup_with_idx(od, key):
    for idx, (k, v) in enumerate(od.iteritems()):
        if k == key:
            return (idx, v)
    raise KeyError(key)

