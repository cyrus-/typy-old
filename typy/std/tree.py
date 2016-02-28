from typy import component

@component
def Tree():
    @component
    def Internal():
        """Trees with values at both internal nodes and leaves."""
        tree(+a) [type] = [
            + Empty
            + Node(+a, vec[tree(+a)])
            + Leaf(+a)
        ]

        def map(tree, f):
            {tree(+a), +a > +b} > +b
            match[tree]
            with Empty: tree
            with Node(v, children):
                Node(f(v), children.map(map(_, f)))
            with Leaf(v):
                Leaf(f(v))

        folder(+a, +b) [type] = {
            empty : +b,
            node : (+a, vec[+b]) > +b,
            leaf : +a > +b
        }
        def fold(tree, folder):
            {tree(+a), folder(+a, +b)} > tree(+b)
            match[tree]
            with Empty:
                folder.empty
            with Node(v, children):
                children_v = children.fold(fold(_, folder))
                folder.node(v, children_v)
            with Leaf(v):
                folder.leaf(v)

    @component
    def External():
        """Trees with values only at leaves."""
        tree(+a) [type] = [
            + Empty
            + Node(vec[tree(+a)])
            + Leaf(+a)
        ]

        def map(tree, f):
            {tree(+a), +a > +b} > tree(+b)
            match[tree]
            with Empty: tree
            with Node(children): Node(children.map(map(_, f)))
            with Leaf(v): Leaf(f(v))

        folder(+a, +b) [type] = {
            empty : +b,
            node : vec[+b] > +b,
            leaf : +a > +b
        }
        def fold(tree, folder):
            {tree(+a), folder(+a, +b)} > +b
            match[tree]
            with Empty:
                folder.empty
            with Node(children):
                folder.node(children.fold(fold(_, folder)))
            with Leaf(v):
                folder.leaf(a)

@component
def Nat():
    T [type] <> num
    zero [: T] = 0
    succ [: T > T] = _ + 1
    case [: { n : T, z : () > +A, s : T > +A } > +A]
    nat.T 
    case [: { 
                n : t,
                z : () > +a, 
                s : t > +a
            } 
                > +a]

    def case(n, z, s):
        if n == 0: z()
        else: s(n - 1)
    exn += NaNat
    def of_num(n):

    of_num [: num > t] = lambda x: x if x >= 0 else throw(NaNat)

INat = interface(Nat)

@INat
def Nat2():
    t [type] = [Zero ++ Succ(t)]
    zero = Zero
    succ = Succ(_)
    def case(n, z, s):
        match [n]
        with Zero: z()
        with Succ(p): s(p)
    exn += NaNat
    def of_num(n):
        if n < 0: raise NaNat
        elif n == 0: Zero
        else: Succ(of_num(n - 1))

    



@interface
def INat2():
    t    [type]
    zero [: t]
    succ [: t > t]
    case [: {n : t, 
             z : () > +a,
             s : t > +a} 
          > +a]

assert static[INat == INat2]


