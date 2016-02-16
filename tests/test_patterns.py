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

