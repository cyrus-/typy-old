"""Tests of pattern matching."""
import pytest

import typy
from typy.std import *

from utils import *

# pattern matching basics
class TestVariablePatternAna:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {unit} >> unit
            {x} is {y: y}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[unit, unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: ((lambda y: y)(__typy_scrutinee__) if True else (_ for _ in ()).throw(__builtin__.Exception('Match failure.'))))(x)""") # noqa

    #def test_translation(self, f):
    #    translation_eq(f, """
    #        def f(x):
    #            return (lambda x: x if True else raise __builtin__.Exception('Match failure'))(x)""") # noqa

class TestVariablePatternAnaPropagates:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean} >> boolean
            {x} is {y: True}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: ((lambda y: True)(__typy_scrutinee__) if True else (_ for _ in ()).throw(__builtin__.Exception('Match failure.'))))(x)""") # noqa

class TestVariablePatternSyn:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean}
            {x} is {y: y}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: ((lambda y: y)(__typy_scrutinee__) if True else (_ for _ in ()).throw(__builtin__.Exception('Match failure.'))))(x)""") # noqa

def test_underscore_pattern():
    @fn
    def test(x):
        {boolean}
        {x} is {_: _}

    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_invalid_pattern_form():
    @fn
    def test(x):
        {boolean}
        {x} is {3 + 3: x}

    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestMultipleRulesAna:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean} >> boolean
            {x} is {y: True, y: y}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: ((lambda y: True)(__typy_scrutinee__) if True else ((lambda y: y)(__typy_scrutinee__) if True else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))))(x)""") # noqa

def test_pop():
    @fn
    def test(x):
        {boolean}
        {x} is {y: True, z: y}
    
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_invalid_form():
    @fn
    def test(x):
        {num}
        {x} is {y: y} + 5
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestOperations:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {num}
            ({x} is {y: y}) + 5
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]
    
    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return ((lambda __typy_scrutinee__: ((lambda y: y)(__typy_scrutinee__) if True else (_ for _ in ()).throw(__builtin__.Exception('Match failure.'))))(x) + 5)""") # noqa

class TestBooleanPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {boolean}
            {{x} is {True: x, False: x}} is {
                False: x,
                _: x
            }
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[boolean, boolean]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: (x if (not __typy_scrutinee__) else (x if True else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))))((lambda __typy_scrutinee__: (x if __typy_scrutinee__ else (x if (not __typy_scrutinee__) else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))))(x))""") # noqa

class TestNumPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {num}
            {x} is {0: x, 5: x + x}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[num, num]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: (x if (__typy_scrutinee__ == 0) else ((x + x) if (__typy_scrutinee__ == 5) else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))))(x)""") # noqa

class TestIEEEPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {ieee}
            {x} is {0: x, 5.5: x + x}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[ieee, ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: (x if (__typy_scrutinee__ == 0.0) else ((x + x) if (__typy_scrutinee__ == 5.5) else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))))(x)""") # noqa

class TestCplxNumPattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {cplx}
            {x} is {0: x, 5.5: x + x, 6j: x + x + x}
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[cplx, cplx]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: (x if (__typy_scrutinee__ == 0j) else ((x + x) if (__typy_scrutinee__ == (5.5+0j)) else (((x + x) + x) if (__typy_scrutinee__ == 6j) else (_ for _ in ()).throw(__builtin__.Exception('Match failure.'))))))(x)""") # noqa

class TestCplxTuplePattern:
    @pytest.fixture
    def f(self):
        @fn
        def f(x):
            {cplx} >> ieee
            {x} is {
                (0, 1.0): 0, 
                (y, 2.0): y,
                (3.0, y): y,
                (y, z): y + z
            }
        return f

    def test_type(self, f):
        assert f.typecheck() == fn[cplx, ieee]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (lambda __typy_scrutinee__: (0.0 if ((__typy_scrutinee__.real == 0.0) and (__typy_scrutinee__.imag == 1.0)) else ((lambda y: y)(__typy_scrutinee__.real) if (True and (__typy_scrutinee__.imag == 2.0)) else ((lambda y: y)(__typy_scrutinee__.imag) if ((__typy_scrutinee__.real == 3.0) and True) else ((lambda y, z: (y + z))(__typy_scrutinee__.real, __typy_scrutinee__.imag) if (True and True) else (_ for _ in ()).throw(__builtin__.Exception('Match failure.')))))))(x)""") # noqa

def test_cplx_tuple_duplicate_vars():
    @fn
    def test(x):
        {cplx} >> ieee
        {x} is {
            (y, y): y + y
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_cplx_tuple_nested():
    @fn
    def test(x):
        {cplx} >> ieee
        {x} is {
            ((y, z), q): y + y
        }
    with pytest.raises(typy.TypeError):
        test.typecheck()

