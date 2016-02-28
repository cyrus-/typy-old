**typy**
========
A programming language with a type system  in the ML (i.e. Standard ML, Caml) tradition, implemented as a library within Python.

NOTE: This is not even remotely ready to be released. Some of the statements below are not true, and may never be true. Don't get too excited/disappointed juuuust yet.

### Feature Summary
Here are the three most powerful features of ``typy``:
* Recursive datatypes
* Nested pattern matching
* ML-style modules (called _**components**_ in typy, to avoid conflicting with Python's existing use of the term "module")

``typy`` differs from most other ML dialects in a few ways, the most pervasive of which is that it has a _bidirectional type system_, in lieu of a Hindley-Milner-style type inference mechanism. There are several semantic reasons for this, which we will get to, as well as a tooling reason: it makes it easier for ``typy`` to provide you with clear and localized error messages.

##### A who in the what now?
If you're a Python programmer and the words above are approximately gibberish, that's great too -- I think ``typy`` is a unique vehicle for learning about them, and integrating the concepts they encompass gradually into your work and play, because:
 * ``typy`` uses Python's syntax (and parser) without modification and adopts many of its syntactic conventions (while introducing a few novel ones that will look strange at first.)
 * You can import and use existing Python libraries  exactly as you're used to using them (and, once you get the hang of things, also in a uniquely more disciplined way) -- Python values are available to ``typy`` components as values of a recursive type called ``dyn`` (that you can pattern match over, in addition to the usual operations). This is particularly important if you work or play in an area where Python has a lot of library support, like many scientific disciplines (e.g. ``scipy`` et al.)

As for _why_ you should learn about these things? Much ink has been spilled on this topic. Here are some of my favorite arguments:

### Installation
The easiest way to get ``typy`` is from PyPI: ``pip install typy``. It only works in Python 2.7 at the moment (though support for 3.4(?)+ is planned).

Trees
===============
OK an example.
```python
from typy import component

@component
def Tree():
    # first, define a recursive sum type
    numtree [type] = [Empty + Node(numtree, numtree) + Leaf(num)]
    """the type of binary trees with numbers at the leaves"""
    
    # then a recursive function over values of that type
    sum_leaves [: numtree > num]
    """sums up all the leaves of the tree"""
    def sum_leaves(tree):
        match[tree]
        with Empty: 0
        with Node(left, right):
            left_sum = sum_leaves(left)
            right_sum = sum_leaves(right)
            left_sum + right_sum
        with Leaf(n): n
```

Tree is a component that defines:
    - a recursive type function, tree, that takes one 
      type parameter, +a, returning a finite sum type
      with three variants:
          - a variant labeled Empty, with payload type unit
          - a variant labeled Node, with payload of the tpl type 
            (tree(+a), (tree(+a)). 
          - a a variant labeled Leaf, with payload type +a
    - a recursive function, sum_over, that takes one
      argument of type tree(num), i.e. tree applied to num, 
      returning a value of type num
    - sum_over proceeds by structural pattern matching on the first 
      argument, identified as t
             - if t matches the pattern Empty, the match expression 
             - if t matches the pattern Node(left, right), for any 
               values of type tree(+a) bound to variables left and right,
               the match expression returns the value of
                    sum_over(left) + sum_over(right)
             - if t matches the pattern Leaf(n), for any value of type
               num bound to variable n, the match expression returns n
             - the semantics guarantees that there are no other cases to
               consider

```ocaml
module Tree = 
struct
    type 'a tree = 
        Empty
        | Node of 'a tree * 'a tree 
        | Leaf of 'a

    fun sum_over(t : int tree) : int = 
        match(t) with 
        | Empty -> 0
        | Node(left, right) -> 
            let left_sum = sum_over left in 
            let right_sum = sum_over right in 
            left_sum + right_sum
        | Leaf(n) -> n
end
```

Interfaces are module types are signatures are structural object types with type members are 
```python
@interface
def ITree():
    tree(+a) [type] = finsum[
        Empty,
        Node: (tree(+a), tree(+a)),
        Leaf: +a]
    sum_over [: tree(num) > num]
```

```ocaml
module type ITree =
sig
    type 'a tree = 
        Empty
      | Node of 'a tree * 'a tree
      | Leaf of 'a
    val sum_over : num tree -> num
end
```


Interaction with Python
=======================
Not the best example:

```python
import sys
from typy.std import fn, dyn

@fn
def main(argv):
	{argv : dyn}
    match[argv]
	with [str(_), str(name)] or [str(_), str(_), str(name)]: 
		print("Hello, " + name + "!")
    with [_]:
		print("Hm, something went wrong.")

main(sys.argv)
```

Hypothetical error message once I get dyn AND pattern matching exhaustiveness checking together:

```
Exception: typy.TyErr
Lines 10-12.
typy.TyErr: Pattern matching non-exhaustive.
Here are some examples of patterns that are not matched:
  
    with None: _
    with True or False: _
    with 0 | 1 | 2 | int(_): _
    with "" | "abc" | str(_): _
    with () | (_,) | (_, _) | tuple(_): _
    with {} | {_: _} | {_: _, _: _} | dict(_): _
	with [] | [_] | list(_): _
    with ast.Func[_ | _.func is ast.Name[_ | _.id is id], 
                      match[_.args]]:
        with []: _
        with _: _

This list is not exhaustive.
```

```python
if isinstance(e, ast.Func) and isinstance(e.func, ast.Name):
    id = e.func.id
    if isinstance(e.func.args, []) and len(e.func.args) == 0:
        _
    else:
        _
```

Differences Between Ocaml and typy
==================================
    Summary of Syntactic Differences
    Equirecursive vs. Isorecursive Types
        type [list(+a)] = finsum[
            Nil,
            Cons: (+a, list(+a))
        ]
        type [t(+a)] = finsum[
            Nil,
            Cons: (+a, list(+a))
        ]
        # Isorecursive: list(+a) and t(+a) are different types.
        # Equirecursive: list(+a) and t(+a) are equal types.
        # Infinite regress is prevented by forcing all 
        # recursive type definitions to immediately apply a type
        # operator, so definitions like this are not allowed:
        type [list(+a)] = list(+a)

        # types like this can be defined
        type [t] = (num, t)

        # no self-reference via binding
        x [: t] = (0, x) # TyErr: x is unbound
        
        # you can do stuff like this, but you'll just get 
        # an infinite loop
        def f(x):
            {num} > t
            (x, f(x+1))
        f(0) # = (0, f(1)) = (0, (1, f(2)) = ...

        xrange [: coroutine[(num, num, num), num]]

    Bidirectional Typing vs. Local Type Inference
        Introductory Forms
    Currying and Named Arguments
    Components vs. Modules vs. Objects
        Generative component functions
        First-class modules (~ like 1ML)
        Operations on values of abstract type
        Subtyping

Implementation
==============

Why Mightn't I Want This?
-------------------------
This library is not currently for you if:
* You think you'll write a huge code base in `typy` before the contributors to this project get to the point where optimizing for compilation speed is an important priority (which, I mean, eventually, it will be).
* You don't have any time to play with new technology that's not 100% mature.
* If when your program goes wrong, bad things happen to good people, or good things happen to bad people.

Contributors
============

@cyrus-

License
=======
Copyright 2016 Cyrus Omar.

typy is released under the permissive MIT License, requiring only attribution in derivative works. See LICENSE for full terms.
