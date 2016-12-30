"""Standard library tests.

To run:
  $ py.test test_std.py
"""
import pytest
import ast

from typy.util.testing import ast_eq

import typy
from typy._ty_exprs import CanonicalTy
from typy.std import component, boolean, unit, record, string, py, fn, finsum, tpl

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
    assert c._members[0].ty == ty_unit
    assert c._members[1].ty == ty_unit
    assert c._members[2].ty == ty_boolean
    assert c._members[3].ty == ty_boolean
    assert c._members[4].ty == ty_boolean
    assert c._members[5].ty == ty_boolean

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
    assert c._members[0].ty == CanonicalTy(boolean, ())
    assert c._members[1].ty == CanonicalTy(boolean, ())
    assert c._members[3].ty == CanonicalTy(boolean, ())
    assert c._members[4].ty == CanonicalTy(boolean, ())
    assert c._members[5].ty == CanonicalTy(boolean, ())
    assert c._members[6].ty == CanonicalTy(boolean, ())
    assert c._members[7].ty == CanonicalTy(boolean, ())
    assert c._members[8].ty == CanonicalTy(boolean, ())
    assert c._members[10].ty == CanonicalTy(boolean, ())
    assert c._members[11].ty == CanonicalTy(unit, ())

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

