"""typy standard library tests"""
import pytest

from utils import * 

import typy
import typy.fp as fp
import typy.std as std
from typy.std import int, int_, float, float_, bool, bool_

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
            True [: bool_]
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

class TestBooleanNot:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: bool] = True
            not x
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                return (not x)""")

def test_bool_Invert():
    @fp.fn
    def test():
        x [: bool] = True
        ~x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_bool_UAdd():
    @fp.fn
    def test():
        x [: bool] = True
        +x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_bool_USub():
    @fp.fn
    def test():
        x [: bool] = True
        -x
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestBooleanCompareOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: bool] = True
            x_eq_y = (x == True)
            x_eq_y [: bool]
            x_neq_y = (x != True)
            x_neq_y [: bool]
            x_is_y = (x is True)
            x_is_y [: bool]
            x_isnot_y = (x is not True)
            x_isnot_y
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                x_eq_y = (x == True)
                x_eq_y
                x_neq_y = (x != True)
                x_neq_y
                x_is_y = (x is True)
                x_is_y
                x_isnot_y = (x is not True)
                return x_isnot_y""")

def test_bool_Lt():
    @fp.fn
    def test():
        x [: bool] = True
        y [: bool] = False
        x < y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_bool_LtE():
    @fp.fn
    def test():
        x [: bool] = True
        y [: bool] = False
        x <= y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_bool_Gt():
    @fp.fn
    def test():
        x [: bool] = True
        y [: bool] = False
        x > y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_bool_GtE():
    @fp.fn
    def test():
        x [: bool] = True
        y [: bool] = False
        x >= y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_bool_In():
    @fp.fn
    def test():
        x [: bool] = True
        y [: bool] = False
        x in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_bool_NotIn():
    @fp.fn
    def test():
        x [: bool] = True
        y [: bool] = False
        x not in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestBooleanBoolOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: bool] = True
            x_and_y = (x and True and True and True)
            x_and_y [: bool]
            x_or_y = (x or True or True or True)
            x_or_y [: bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                x_and_y = (x and True and True and True)
                x_and_y
                x_or_y = (x or True or True or True)
                return x_or_y""")

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

def test_integer_ascription_on_complex():
    @fp.fn
    def test():
        3.0j [: int]
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

# see TestIntFloatDiv for integer/float division
def test_integer_int_div():
    @fp.fn
    def test():
        x [: int] = 3
        x / x
    with pytest.raises(typy.TypeError):
        test.typecheck()

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
            x_is_y = (x is 456 is 789)
            x_is_y [: bool]
            x_isnot_y = (x is not 456 is not 789)
            x_isnot_y [: bool]
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
                x_gte_y
                x_is_y = (x is 456 is 789)
                x_is_y
                x_isnot_y = (x is not 456 is not 789)
                return x_isnot_y""")

def test_int_In():
    @fp.fn
    def test():
        x [: int] = 123
        y [: int] = 456
        x in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_int_NotIn():
    @fp.fn
    def test():
        x [: int] = 123
        y [: int] = 456
        x not in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_int_And():
    @fp.fn
    def test():
        x [: int] = 123
        y [: int] = 456
        x and y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_int_Or():
    @fp.fn
    def test():
        x [: int] = 123
        y [: int] = 456
        x or y
    with pytest.raises(typy.TypeError):
        test.typecheck()

#
# float
#

class TestFloatIntroF:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3.0 [: float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestFloatIntroI:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestFloatIntroL:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 1.2345678901234567e+69""")

class TestIntegerIncIntroF:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3.0 [: float_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestIntegerIncIntroI:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: float_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestFloatIntroL:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: float_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 1.2345678901234567e+69""")

def test_float_ascription_on_complex():
    @fp.fn
    def test():
        3.0j [: float]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_integer_ascription_on_string():
    @fp.fn
    def test():
        "3" [: float]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestFloatUnaryOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: float]
            x_plus = +x
            x_plus [: float]
            x_minus = -x
            x_minus [: float]
            x_invert = ~x
            x_invert [: float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123.0
                x_plus = (+ x)
                x_plus
                x_minus = (- x)
                x_minus
                x_invert = (~ x)
                return x_invert""")

def test_float_no_not():
    @fp.fn
    def test():
        not (3 [: float])
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestFloatBinops:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: float]
            y = 456 [: float]
            x_plus_y = x + y
            x_plus_y [: float]
            x_minus_y = x - y
            x_minus_y [: float]
            x_mult_y = x * y
            x_mult_y [: float]
            x_mod_y = x % y
            x_mod_y [: float]
            x_pow_y = x ** y
            x_pow_y [: float]
            x_lshift_y = x << y
            x_lshift_y [: float]
            x_rshift_y = x >> y
            x_rshift_y [: float]
            x_bitor_y = x | y
            x_bitor_y [: float]
            x_bitxor_y = x ^ y
            x_bitxor_y [: float]
            x_bitand_y = x & y
            x_bitand_y [: float]
            x_div_y = x / y
            x_div_y [: float]
            x_floordiv_y = x // y
            x_floordiv_y [: float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123.0
                y = 456.0
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
                x_div_y = (x / y)
                x_div_y
                x_floordiv_y = (x // y)
                return x_floordiv_y""")

class TestFloatCompareOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: float]
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
            x_is_y = (x is 456 is 789)
            x_is_y [: bool]
            x_isnot_y = (x is not 456 is not 789)
            x_isnot_y [: bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123.0
                x_eq_y = (x == 456.0 == 789.0)
                x_eq_y
                x_neq_y = (x != 456.0 != 789.0)
                x_neq_y
                x_lt_y = (x < 456.0 < 789.0)
                x_lt_y
                x_lte_y = (x <= 456.0 <= 789.0)
                x_lte_y
                x_gt_y = (x > 456.0 > 789.0)
                x_gt_y
                x_gte_y = (x >= 456.0 >= 789.0)
                x_gte_y
                x_is_y = (x is 456.0 is 789.0)
                x_is_y
                x_isnot_y = (x is not 456.0 is not 789.0)
                return x_isnot_y""")

def test_float_In():
    @fp.fn
    def test():
        x [: float] = 123
        y [: float] = 456
        x in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_float_NotIn():
    @fp.fn
    def test():
        x [: float] = 123
        y [: float] = 456
        x not in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_float_And():
    @fp.fn
    def test():
        x [: float] = 123
        y [: float] = 456
        x and y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_float_Or():
    @fp.fn
    def test():
        x [: float] = 123
        y [: float] = 456
        x or y
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestIntFloatDiv:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: int] = 3
            x / 2
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 3
                return (x / 2.0)""")
