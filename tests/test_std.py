"""Standard library tests.

To run:
  $ py.test test_std.py
"""
import pytest
import ast

from typy.util.testing import ast_eq, trans_str, trans_truth

import typy
from typy._ty_exprs import CanonicalTy
from typy.std import component, boolean, unit, num, ieee, record, string, py, fn, finsum, tpl

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
        with "a" + y + "b": y
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
        # TODO methods
        # TODO to_string logic for other primitives
    
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
# tpl
# 

