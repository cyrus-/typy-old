"""Tests for typy.pynum"""
import pytest

from utils import * 

import typy
import typy.fp as fp
from typy.pynum import pyint

#
# pyint
#
class TestIntegerIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: pyint]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), pyint]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")


