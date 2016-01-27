"""typy standard library tests"""
import pytest

from utils import * 

import typy
import typy.fp as fp
import typy.std as std
from typy.std import int, int_, bool, bool_

#
# int
#

class TestIntegerIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: int]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), int]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")

class TestIntegerIncIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: int_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), int]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")

class TestIntegerLongIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: int]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), int]

    def test_translation(self, f):  
        translation_eq(f, """
            def f():
                return 1234567890123456789012345678901234567890123456789012345678901234567890L""")

def test_integer_ascription_on_float():
    @fp.fn
    def test():
        3.0 [: int]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_integer_ascription_on_string():
    @fp.fn
    def test():
        "3" [: int]
    with pytest.raises(typy.TypeError):
        test.typecheck()

#
# bool
#

class TestBooleanAscriptionTrue:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            True [: bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return True""")

class TestBooleanAscriptionFalse:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            False [: bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return False""")

class TestBooleanIncAscription:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            True [: bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return True""")

def test_bool_ascription_bad():
    @fp.fn
    def test():
        Bad [: bool]
    with pytest.raises(typy.TypeError):
        test.typecheck()
