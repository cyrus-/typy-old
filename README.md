**typy**
========
NOTE: Some of the statements below are false -- **WIP**!

A statically typed functional programming language with a semantics in the ML tradition implemented as a library inside Python, using[1] Python's own syntax.

[1] depending on your aesthetic preferences, this can also be pronounced "misusing"

### Summary of Features

If these words make you feel good, you'll probably like **typy**:
* Local type and type parameter inference
* Recursive datatypes
* Nested pattern matching
* A powerful ML-style module system (called the _component system_ in typy, to avoid conflicting with Python's existing use of the term "module")
* Low-cost, disciplined interaction with Python (by treating Python values as values of a big ol' recursive datatype called ``dyn`` that you can pattern match over, and using type inference to determine whether you want a piece of syntax to have type `dyn` or to have some other type)

If these words are only vaguely familiar to you, perhaps read on -- they sound more complicated now than they will ultimately seem to you, I'll bet. If these words are completely unfamiliar to you, the best thing to do would be to learn a language like Ocaml, Standard ML, Scala or Haskell (in decreasing order of similarity to typy) using some of the many wonderful resources out there -- if for no other reason than because, for the time being, there is no comparable introductory-level material for learning `typy`.

### Why Might I Want This?

If you're currently a Python programmer:
 - In short, by working within a semantics that enforces a static type discipline, you'll end up making fewer mistakes, writing fewer checks/assertions/tests, and your programs will run faster (though they will take a bit longer to compile). You'll save time in the long run. 
 - You can continue using existing libraries, and it's not even inconvenient.

If you're currently use/want to use a functional language like those I mentioned above:
 - Python has a lot of libraries that you don't have that may actually be really useful (e.g. numpy)
 - In my opinion, Python's syntax is a lot cleaner and less error-prone than Ocaml's.
 - typy is a fairly modern ML, and includes some conveniences that make it even easier to use than Ocaml/SML

### Installation
The easiest way to get it is off of PyPI, using pip:
  
    pip install typy

This is also how you should distribute libraries that use typy.

**Requirements**: Python 2.7 at the moment (though support for 3.4(?)+ is planned).

typy By Example
===============

```python
from typy.std import ty, component, finsum

@component
def Tree():
    tree(+a) [type] = finsum[
        Empty,
        Node: (tree(+a), tree(+a)),
        Leaf: +a
    ]

    def sum_over(t):
        {tree(+a)} > +a
        match[t]
        with Empty: 0
        with Node(left, right):
            left_sum = sum_over(left)
            right_sum = sum_over(right)
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
