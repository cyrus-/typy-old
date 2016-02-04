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

class TestIntegerUnaryOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: int]
            x_plus = +x
            x_plus [: int]
            x_minus = -x
            x_minus [: int]
            x_invert = ~x
            x_invert [: int]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), int]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123
                x_plus = (+ x)
                x_plus
                x_minus = (- x)
                x_minus
                x_invert = (~ x)
                return x_invert""")

def test_integer_no_not():
    @fp.fn
    def test():
        not (3 [: int])
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestIntegerBinops:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: int]
            y = 456 [: int]
            x_plus_y = x + y
            x_plus_y [: int]
            x_minus_y = x - y
            x_minus_y [: int]
            x_mult_y = x * y
            x_mult_y [: int]
            x_mod_y = x % y
            x_mod_y [: int]
            x_pow_y = x ** y
            x_pow_y [: int]
            x_lshift_y = x << y
            x_lshift_y [: int]
            x_rshift_y = x >> y
            x_rshift_y [: int]
            x_bitor_y = x | y
            x_bitor_y [: int]
            x_bitxor_y = x ^ y
            x_bitxor_y [: int]
            x_bitand_y = x & y
            x_bitand_y [: int]
            x_floordiv_y = x // y
            x_floordiv_y [: int]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), int]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123
                y = 456
                x_plus_y = (x + y)
                x_plus_y
                x_minus_y = (x - y)
                x_minus_y
                x_mult_y = (x * y)
                x_mult_y
                x_mod_y = (x % y)
                x_mod_y
                x_pow_y = (x ** y)
                x_pow_y
                x_lshift_y = (x << y)
                x_lshift_y
                x_rshift_y = (x >> y)
                x_rshift_y
                x_bitor_y = (x | y)
                x_bitor_y
                x_bitxor_y = (x ^ y)
                x_bitxor_y
                x_bitand_y = (x & y)
                x_bitand_y
                x_floordiv_y = (x // y)
                return x_floordiv_y""")

class TestIntegerCompareOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: int]
            x_eq_y = (x == 456 == 789)
            x_eq_y [: bool]
            x_neq_y = (x != 456 != 789)
            x_neq_y [: bool]
            x_lt_y = (x < 456 < 789)
            x_lt_y [: bool]
            x_lte_y = (x <= 456 <= 789)
            x_lte_y [: bool]
            x_gt_y = (x > 456 > 789)
            x_gt_y [: bool]
            x_gte_y = (x >= 456 >= 789)
            x_gte_y [: bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123
                x_eq_y = (x == 456 == 789)
                x_eq_y
                x_neq_y = (x != 456 != 789)
                x_neq_y
                x_lt_y = (x < 456 < 789)
                x_lt_y
                x_lte_y = (x <= 456 <= 789)
                x_lte_y
                x_gt_y = (x > 456 > 789)
                x_gt_y
                x_gte_y = (x >= 456 >= 789)
                return x_gte_y""")
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
