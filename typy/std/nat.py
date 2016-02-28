"""Natural numbers, modularly.

This is aspirational -- a lot of the features used below haven't been implemented yet.
"""
from .. import *
from . import boolean, opt, num

@component
def Nat():
    @interface
    def INat():
        t [type]
        zero [: t]
        succ [: t > t]
        rules(+a) [type] = {
            zero : +a,
            succ : t > +a
        }
        case [: {t, rules(+a)} > +a]
        eq [: (t, t) > boolean]
        of_num [: num > opt(t)]
        to_num [: t > num]

    _rules(+t, +a) [type] = {
        zero : +a,
        succ : +t > +a
    }

    @INat
    def NumNat():
        t [type] = num
        zero = 0
        succ = _ + 1
        rules(+a) [type] = _rules(+t, +a)
        def case(n, rules):
            if n == 0: rules.zero
            else: rules.succ(n - 1)
        def eq(n1, n2):
            n1 == n2
        def of_num(n):
            if n < 0: N
            else: Y(n)
        def to_num(n): n

    @INat
    def UnaryNat():
        t [type] = [Z + S(t)]
        zero = Z
        succ = S(_)
        rules(+a) [type] = _rules(+t, +a)
        def case(n, rules):
            match[n]
            with Z: rules.zero
            with S(p): rules.succ(p)
        def eq(*n):
            match[n]
            with (Z, Z): True
            with (Z, _): False
            with (S(p1), S(p2)): eq(p1, p2)
            with (_, _): False
        def of_num(n):
            if n < 0: N
            else: Y(S(of_num(n - 1)))
        def to_num(n):
            match[n]
            with Z: 0
            with S(p): to_num(p) + 1

@component
def TestNat():
    @component_fn
    def TestINat(N):
        {N : Nat.INat}
        assert N.zero.succ.succ.succ.to_num == 3
        assert {N.of_num(3)} is {Y(_): True, N: False}
        assert {N.of_num(-4)} is {Y(_): False, N: True}
        assert {N.of_num(3), N.of_num(4)} is {(Y(three), Y(four)): three != four, _: False}

    TestINat(Nat.NumNat)
    TestINat(Nat.UnaryNat)

