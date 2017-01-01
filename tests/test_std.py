"""Standard library tests.

To run:
  $ py.test test_std.py
"""
import pytest
import ast

from typy.util.testing import ast_eq

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


# 
# string
# 

def test_string_intro():
    @component
    def c():
        x [: string] = "test"

    # typechecking
    assert c._members[0].ty == CanonicalTy(string, ())

    # translation
    # typechecking
    assert c._members[0].ty == CanonicalTy(unit, ())

    # translation
    assert ast_eq(c._translation, """
        x = 'test'""")

    # evaluation
    assert c._module.x == "test"

def test_string_match():
    @component
    def c():
        x [: string] = "test"
        [x].match
        with "test": x
        with "": x
        with _: x

    assert ast_eq(c._translation, """
        x = 'test'
        __typy_scrutinee__ = x
        if x == 'test':
            x
        else:
            if x == '':
                x
            else:
                raise Exception('typy match failure')""")

# 
# tpl
# 

