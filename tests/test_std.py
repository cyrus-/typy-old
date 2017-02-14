"""Standard library tests.

To run:
  $ py.test test_std.py
"""
import pytest
import ast

from typy.util.testing import ast_eq, trans_str, trans_truth

import typy
from typy._ty_exprs import CanonicalTy
from typy.std import component, boolean, unit, num, ieee, record, string, py, fn, variant, tpl

# 
# unit
# 

def test_unit_intro():
    @component
    def c():
        x [: typy.std.unit] = ()
        y = () [: typy.std.unit]

    # typechecking 
    assert c._members[0].ty == CanonicalTy(unit, ()) 
    assert c._members[1].ty == CanonicalTy(unit, ())

    # translation
    assert ast_eq(c._translation, """
        import builtins as __builtins__
        x = ()
        y = ()""")

    # evaluation
    assert c._module.x == ()
    assert c._module.y == ()

def test_unit_match():
    @component
    def c():
        x = () [: unit]
        [x].match
        with (): x

    assert ast_eq(c._translation, """
        import builtins as __builtins__
        x = ()
        __typy_scrutinee__ = x
        if True:
            x
        else:
            raise Exception('typy match failure')""")

def test_unit_intro_bad():
    with pytest.raises(typy.TyError):
        @component
        def c():
            x = ((), ()) [: unit]

def test_unit_match_bad():
    with pytest.raises(typy.TyError):
        @component
        def c():
            x = () [: unit]
            [x].match
            with (y, z): y

def test_unit_compare():
    @component
    def c():
        x = () [: unit]
        y = () [: unit]
        b1 = x == y
        b2 = x != y
        b3 = x is y
        b4 = x is not y

    # typechecking
    ty_unit = CanonicalTy(unit, ())
    ty_boolean = CanonicalTy(boolean, ())
    assert c._val_exports['x'].ty == ty_unit
    assert c._val_exports['y'].ty == ty_unit
    assert c._val_exports['b1'].ty == ty_boolean
    assert c._val_exports['b2'].ty == ty_boolean
    assert c._val_exports['b3'].ty == ty_boolean
    assert c._val_exports['b4'].ty == ty_boolean

# 
# boolean
# 

def test_boolean():
    @component
    def c():
        x [: boolean] = True
        y [: boolean] = False
        [x].match
        with True: y
        with False: y
        b1 = x == y
        b2 = x != y
        b3 = x is y
        b4 = x is not y
        b5 = x and y and x
        b6 = x or y or x
        if x:
            y
        else:
            y
        b7 = y if x else x
        b8 [: unit] = () if x else ()

    # typechecking
    assert c._val_exports['x'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['y'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b1'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b2'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b3'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b4'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b5'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b6'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b7'].ty == CanonicalTy(boolean, ())
    assert c._val_exports['b8'].ty == CanonicalTy(unit, ())

    # translation
    assert ast_eq(c._translation, """
        import builtins as __builtins__
        x = True
        y = False
        __typy_scrutinee__ = x
        if __typy_scrutinee__:
            y
        elif (not __typy_scrutinee__):
            y
        else:
            raise Exception('typy match failure')
        b1 = (x == y)
        b2 = (x != y)
        b3 = (x is y)
        b4 = (x is not y)
        b5 = (x and y and x)
        b6 = (x or y or x)
        if x:
            y
        else:
            y
        b7 = (y if x else x)
        b8 = (() if x else ())""")

    # evaluation
    assert c._module.x == True
    assert c._module.y == False
    assert c._module.b1 == False
    assert c._module.b2 == True
    assert c._module.b3 == False
    assert c._module.b4 == True
    assert c._module.b5 == False
    assert c._module.b6 == True
    assert c._module.b7 == False
    assert c._module.b8 == ()

# 
# num
# 

def test_num():
    @component
    def c():
        x [: num] = 42
        y [: num] = -42
        [x].match
        with 42: y
        with -42: y
        with -z: z
        with +z: z
        b1 = x + y
        b2 = x - y
        b3 = x * y
        b4 = x / y
        b5 = x % y
        b6 = x ** y
        b7 = x << 2
        b8 = x >> 2
        b9 = x | 2
        b10 = x ^ 2
        b11 = x & 2
        b12 = x // 2
        b13 = ~x
        b14 = +x
        b15 = -x
        b16 = x == y
        b17 = x != y
        b18 = x < y <= y
        b19 = x > y >= y
        b20 = x is y
        b21 = x is not y
        # TODO methods?

    # typechecking
    num_ty = CanonicalTy(num, ())
    ieee_ty = CanonicalTy(ieee, ())
    boolean_ty = CanonicalTy(boolean, ())
    assert c._val_exports['x'].ty == num_ty
    assert c._val_exports['y'].ty == num_ty
    assert c._val_exports['b1'].ty == num_ty
    assert c._val_exports['b2'].ty == num_ty
    assert c._val_exports['b3'].ty == num_ty
    assert c._val_exports['b4'].ty == ieee_ty
    assert c._val_exports['b5'].ty == num_ty
    assert c._val_exports['b6'].ty == num_ty
    assert c._val_exports['b7'].ty == num_ty
    assert c._val_exports['b8'].ty == num_ty
    assert c._val_exports['b9'].ty == num_ty
    assert c._val_exports['b10'].ty == num_ty
    assert c._val_exports['b11'].ty == num_ty
    assert c._val_exports['b12'].ty == num_ty
    assert c._val_exports['b13'].ty == num_ty
    assert c._val_exports['b14'].ty == num_ty
    assert c._val_exports['b15'].ty == num_ty
    assert c._val_exports['b16'].ty == boolean_ty
    assert c._val_exports['b17'].ty == boolean_ty
    assert c._val_exports['b18'].ty == boolean_ty
    assert c._val_exports['b19'].ty == boolean_ty
    assert c._val_exports['b20'].ty == boolean_ty
    assert c._val_exports['b21'].ty == boolean_ty

    # translation
    assert ast_eq(c._translation, """
        import builtins as __builtins__
        x = 42
        y = (- 42)
        __typy_scrutinee__ = x
        if (__typy_scrutinee__ == 42):
            y
        elif ((__typy_scrutinee__ < 0) and ((- __typy_scrutinee__) == 42)):
            y
        elif ((__typy_scrutinee__ < 0) and True):
            _z_0 = (- __typy_scrutinee__)
            _z_0
        elif ((__typy_scrutinee__ > 0) and True):
            _z_1 = __typy_scrutinee__
            _z_1
        else:
            raise Exception('typy match failure')
        b1 = (x + y)
        b2 = (x - y)
        b3 = (x * y)
        b4 = (x / y)
        b5 = (x % y)
        b6 = (x ** y)
        b7 = (x << 2)
        b8 = (x >> 2)
        b9 = (x | 2)
        b10 = (x ^ 2)
        b11 = (x & 2)
        b12 = (x // 2)
        b13 = (~ x)
        b14 = (+ x)
        b15 = (- x)
        b16 = (x == y)
        b17 = (x != y)
        b18 = (x < y <= y)
        b19 = (x > y >= y)
        b20 = (x is y)
        b21 = (x is not y)""")

# 
# ieee
# 

def test_ieee():
    @component
    def c():
        x1 [: ieee] = 42
        x2 [: ieee] = 42.5
        y1 [: ieee] = -42
        y2 [: ieee] = -42.5
        nan [: ieee] = NaN
        inf [: ieee] = Inf
        ninf [: ieee] = -Inf
        n [: num] = 2
        [x1].match
        with 42: y1
        with 42.5: y1
        with -42: y2
        with -42.5: y2
        with NaN: inf
        with Inf: inf
        with -Inf: inf
        with -z: z
        with +z: z
        b1 = x1 + y1
        b1n = x1 + n
        b2 = x1 - y1
        b2n = n - y1
        b3 = x1 * y1
        b4 = x1 / y1
        b5 = x1 % y1
        b6 = x1 ** y1
        b12 = x1 // 2
        b14 = +x1
        b15 = -x1
        b16 = x1 == y1
        b17 = x1 != y1
        b18 = x1 < y1 <= y2
        b19 = x1 > y1 >= y2
        b20 = x1 is y1
        b21 = x1 is not y1
        # TODO: methods

    # typechecking
    num_ty = CanonicalTy(num, ())
    ieee_ty = CanonicalTy(ieee, ())
    boolean_ty = CanonicalTy(boolean, ())
    assert c._val_exports['x1'].ty == ieee_ty
    assert c._val_exports['x2'].ty == ieee_ty
    assert c._val_exports['y1'].ty == ieee_ty
    assert c._val_exports['y2'].ty == ieee_ty
    assert c._val_exports['nan'].ty == ieee_ty
    assert c._val_exports['inf'].ty == ieee_ty
    assert c._val_exports['ninf'].ty == ieee_ty
    assert c._val_exports['n'].ty == num_ty
    assert c._val_exports['b1'].ty == ieee_ty
    assert c._val_exports['b1n'].ty == ieee_ty
    assert c._val_exports['b2'].ty == ieee_ty
    assert c._val_exports['b2n'].ty == ieee_ty
    assert c._val_exports['b3'].ty == ieee_ty
    assert c._val_exports['b4'].ty == ieee_ty
    assert c._val_exports['b5'].ty == ieee_ty
    assert c._val_exports['b6'].ty == ieee_ty
    assert c._val_exports['b12'].ty == ieee_ty
    assert c._val_exports['b14'].ty == ieee_ty
    assert c._val_exports['b15'].ty == ieee_ty
    assert c._val_exports['b16'].ty == boolean_ty
    assert c._val_exports['b17'].ty == boolean_ty
    assert c._val_exports['b18'].ty == boolean_ty
    assert c._val_exports['b19'].ty == boolean_ty
    assert c._val_exports['b20'].ty == boolean_ty
    assert c._val_exports['b21'].ty == boolean_ty

    # translation
    assert trans_str(c._translation) == trans_truth("""
        import math as _typy_import_0
        import builtins as __builtins__
        x1 = 42
        x2 = 42.5
        y1 = (- 42)
        y2 = (- 42.5)
        nan = __builtins__.float('NaN')
        inf = __builtins__.float('Inf')
        ninf = (- __builtins__.float('Inf'))
        n = 2
        __typy_scrutinee__ = x1
        if (__typy_scrutinee__ == 42):
            y1
        elif (__typy_scrutinee__ == 42.5):
            y1
        elif ((__typy_scrutinee__ < 0.0) and ((- __typy_scrutinee__) == 42)):
            y2
        elif ((__typy_scrutinee__ < 0.0) and ((- __typy_scrutinee__) == 42.5)):
            y2
        elif _typy_import_0.isnan(__typy_scrutinee__):
            inf
        elif (__typy_scrutinee__ == __builtins__.float('Inf')):
            inf
        elif ((__typy_scrutinee__ < 0.0) and ((- __typy_scrutinee__) == __builtins__.float('Inf'))):
            inf
        elif ((__typy_scrutinee__ < 0.0) and True):
            _z_0 = (- __typy_scrutinee__)
            _z_0
        elif ((__typy_scrutinee__ > 0.0) and True):
            _z_1 = __typy_scrutinee__
            _z_1
        else:
            raise Exception('typy match failure')
        b1 = (x1 + y1)
        b1n = (x1 + n)
        b2 = (x1 - y1)
        b2n = (n - y1)
        b3 = (x1 * y1)
        b4 = (x1 / y1)
        b5 = (x1 % y1)
        b6 = (x1 ** y1)
        b12 = (x1 // 2)
        b14 = (+ x1)
        b15 = (- x1)
        b16 = (x1 == y1)
        b17 = (x1 != y1)
        b18 = (x1 < y1 <= y2)
        b19 = (x1 > y1 >= y2)
        b20 = (x1 is y1)
        b21 = (x1 is not y1)""")

# 
# string
# 

def test_string():
    @component
    def c():
        x1 [: string] = "test"
        [x1].match
        with "": x1
        with "a" + y: y
        with y + "a": y
        with "t" + y + "t": y
        x2 = x1 + "a"
        x3 = "a" + x1
        x4 = x1[0]
        x5 = x1[0:3]
        x6 = x1[0:3:2]
        x7 = x1 == x2
        x8 = x1 != x2
        x9 = x1 < x2 <= x3
        x10 = x1 > x2 >= x3
        x11 = x1 is x2
        x12 = x1 is not x2
        # TODO * operator for repetition?
        # TODO in/not in?
        # TODO methods
        # TODO to_string logic for other primitives
        # TODO string formating?
        # TODO char patterns? separate type?
    
    string_ty = CanonicalTy(string, ())
    boolean_ty = CanonicalTy(boolean, ())
    v = c._val_exports
    assert v['x1'].ty == string_ty
    assert v['x2'].ty == string_ty
    assert v['x3'].ty == string_ty
    assert v['x4'].ty == string_ty
    assert v['x5'].ty == string_ty
    assert v['x6'].ty == string_ty
    assert v['x7'].ty == boolean_ty
    assert v['x8'].ty == boolean_ty
    assert v['x9'].ty == boolean_ty
    assert v['x10'].ty == boolean_ty
    assert v['x11'].ty == boolean_ty
    assert v['x12'].ty == boolean_ty

# 
# record
# 

def test_record():
    @component
    def c():
        t [type] = record[
            a : string,
            b : num]
        x [: t] = {
            a: "test",
            b: 2 }
        y [: t] = {
            b: 2,
            a: "test" }
        [x].match
        with {a: x, b: y}: x
        with {b: y, a: x}: x
        with {a, b}: a
        xa [: string] = x.a
        xb [: num] = x.b
        t2 [type] = record[
            b : num,
            a : string]
        y2 [: t2] = x

# 
# tpl
# 

def test_tpl():
    @component
    def c():
        t1 [type] = tpl[string]
        t2 [type] = tpl[a : string]
        t3 [type] = tpl[a : string, num]
        t4 [type] = tpl[string, b : num]
        t [type] = tpl[
            a : string,
            b : num]
        x1 [: t] = {
            a: "test",
            b: 2 }
        x2 [: t] = {
            b: 2,
            a: "test" }
        x3 [: t] = ("test", 2)
        [x1].match
        with {a: x, b: y}: x
        with {b: y, a: x}: x
        with {a, b}: a
        with {b, a}: a
        with (x, y): x
        xa [: string] = x1.a
        xb [: num] = x1.b
        t5 [type] = tpl[string, num]
        y1 [: t5] = ("test", 2)
        y_0 [: string] = y1[0]
        y_1 [: num] = y1[1]

# 
# variant
# 

def test_variant():
    @component
    def c():
        t0 [type] = variant[A]
        t1 [type] = variant[A(num)]
        t2 [type] = variant[A(num), B(string)]
        t3 [type] = variant[A(num, string), B(string, num)]
        x1 [: t3] = A(3, "test")
        x2 [: t3] = B("test", 3)
        [x2].match
        with A(x, y): x
        with B(x, y): y
        void [type] = variant[()]

# 
# fn
# 

def test_fn():
    @component
    def c():
        t0 [type] = fn[() > num]
        t1 [type] = fn[string > string]
        t2 [type] = fn[string, num > num]
        @t0
        def f1(): 3
        @t0
        def f1b() -> num: 3
        @t1
        def f2(x): x
        @t1
        def f2b(x : string) -> string: x
        @t2
        def f3(x, y): y
        @t2
        def f3b(x : string, y : num) -> num: y
        x1 [: t0] = lambda: 3 
        x2 [: t1] = lambda x: x
        x3 [: t2] = lambda x, y: y
        @fn
        def f11(x : string): x
        f11 [: t1]
        @fn
        def f12(x : string) -> string: ""
        f12 [: t1]
        f1()
        f2("string")
        f3("string", 0)
        @fn
        def f4(x : string):
            y [: string] = "ABC"
            y
        f4 [: fn[string > string]]
        @fn
        def f5(x : string) -> string:
            y [: string] = "ABC"
            "DEF"
        f5 [: fn[string > string]]
        @fn
        def f6(x : num) -> string:
            [x].match
            with 0: 
                "ABC"
            with x:
                "DEF"
        f6 [: fn[num > string]]
        @fn
        def f7(x : num):
            [x].match
            with 0:
                x
            with x:
                x
        f7 [: fn[num > num]]
        rfty [type] = fn[() > unit]
        @rfty
        def rf0():
            rf0()
        @fn
        def rf1() -> unit:
            rf1()
        rf1 [: fn[() > unit]]
        @fn
        def rf2(x : num) -> num:
            rf2(3)
        rf2 [: fn[num > num]]
        @fn
        def rf3(x : num) -> num:
            rf3(3)
        rf3 [: fn[num > num]]
        # TODO nested function definitions
        @fn
        def f8(x : num):
            @fn
            def fi1(y : num):
                x + y
            fi1
        @fn
        def f9(x : num):
            @fn
            def fi2(y : num):
                x + y
        @fn
        def f10(x : num) -> fn[num > num]:
            @fn
            def f(y):
                42
        @fn
        def f20(x : num):
            @fn
            def f(y : num):
                @fn
                def g(z : num):
                    x + y + z
        @fn
        def f21(x : num) -> fn[num > fn[num > num]]:
            def f(y):
                def g(z):
                    x + y + z

    # assert ast_eq(c._translation, "")
    
