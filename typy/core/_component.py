from typy import *

class TODO(Exception): pass

class ComponentType(object):
    """Component types (i.e. generalized signatures)"""
    @classmethod
    def init_idx(self, idx):
        raise TODO

    @classmethod
    def init_inc_idx(self, inc_idx):
        raise TODO

    def __init__(self, idx, from_construct_component_ty=False):
        if not from_construct_component_ty:
            raise TODO
        self.idx = idx

class interface(ComponentType):
    """a singleton classifier of interfaces"""
    def init_idx(self, idx):
        # odict of sigitems
        pass

    def init_inc_idx(self, inc_idx):
        if inc_idx != Ellipsis:
            raise TODO
    
class component_fn(ComponentType):
    """ala ML's functor types"""

def component(f):
    """Use this as a decorator to signify that the component
    type should be synthesized from the component definition.
    """
    pass

class Component(object):
    """Python representation of components."""
    pass

# Component examples:

@component
def Vec():
    append_hd [: vec(+a) > +a > vec(+a)]
    
    hd_tl [: vec(+a) > opt]

@interface
def ISeq():
    seq [:: type > type]

    Nil [: seq(+a)] 
    Cons [: (+a, seq(+a)) > list(+a)]
    
    case [: list(+a) > {
        Nil: () > (+b),
        Cons: (+a, list(+a)) > +b
    } > +b]

@IList
def VecList():
    list [:: type > type] = vec

    Vec [component] = Vec

    Nil = [] # noqa
    Cons = Vec.append_hd # noqa

    def case(xs, rules):
        match[xs]
        with []: rules.Nil()
        with _:
            Some(hd, tl) [match] = Vec.hd_tl(xs)
            rules.Cons(hd, tl)

@component
def LinkedList():
    list(+t) [type] = Nil or Cons(+t, list(t))

    Nil [:+a > list(+a)] = Nil [: list(+a)]
    Cons = Cons(_, _)
    
    def case(xs, rules):
        match[xs]
        with Nil: rules.Nil()
        with Cons(y, ys): rules.Cons(y, ys)
LinkedList [: IList]

{
    + Empty
    + Node[tree[+a], tree[+a]]
    + Leaf[+a]
}
