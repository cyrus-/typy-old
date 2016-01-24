"""Tests for typy.pybool"""
import pytest

from utils import * 

import typy
import typy.fp as fp
from typy.pybool import pybool, pybool_

# pybool

class TestBooleanAscriptionTrue:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            True [: pybool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), pybool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return True""")

class TestBooleanAscriptionFalse:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            False [: pybool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), pybool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return False""")

def test_pybool_ascription_bad():
    @fp.fn
    def test():
        Bad [: pybool]
    with pytest.raises(typy.TypeError):
        test.typecheck()
