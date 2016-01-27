"""typy standard library tests"""
import pytest

from utils import * 

import typy
import typy.fp as fp
import typy.std as std
from typy.std import I, I_, B, B_

#
# I (integers)
#

class TestIntegerIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: I]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), I]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")

class TestIntegerIncIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: I_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), I]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")

#
# B (booleans)
#

class TestBooleanAscriptionTrue:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            True [: B]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), B]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return True""")

class TestBooleanAscriptionFalse:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            False [: B]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), B]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return False""")

class TestBooleanIncAscription:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            True [:B_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), B]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return True""")

def test_pybool_ascription_bad():
    @fp.fn
    def test():
        Bad [: B]
    with pytest.raises(typy.TypeError):
        test.typecheck()
