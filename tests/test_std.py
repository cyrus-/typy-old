"""typy standard library tests"""
import pytest

from utils import * 

import typy
import typy.fp as fp
import typy.std as std
from typy.std import int, int_, float, float_, bool, bool_, complex, complex_, str, str_

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

def test_float_ascription_on_string():
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
                return x_minus""")

def test_float_no_not():
    @fp.fn
    def test():
        not (3 [: float])
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_float_no_invert():
    @fp.fn
    def test():
        x [: float] = 3
        ~x
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
                x_div_y = (x / y)
                x_div_y
                x_floordiv_y = (x // y)
                return x_floordiv_y""")

def test_float_no_lshift():
    @fp.fn
    def test():
        x [: float] = 3
        x << x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_float_no_rshift():
    @fp.fn
    def test():
        x [: float] = 3
        x >> x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_float_no_bitor():
    @fp.fn
    def test():
        x [: float] = 3
        x | x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_float_no_bitxor():
    @fp.fn
    def test():
        x [: float] = 3
        x ^ x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_float_no_bitand():
    @fp.fn
    def test():
        x [: float] = 3
        x & x
    with pytest.raises(typy.TypeError):
        test.typecheck()
 
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

#
# complex
#

class TestComplexIntroI:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestComplexIntroF:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3.0 [: complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestComplexIntroL:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (1.2345678901234567e+69+0j)""")

class TestComplexIntroC:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3j [: complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3j""")

class TestComplexIncIntroI:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestComplexIncIntroF:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3.0 [: complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestComplexIncIntroL:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (1.2345678901234567e+69+0j)""")

class TestComplexIncIntroC:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3j [: complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3j""")

def test_complex_intro_tuple_short():
    @fp.fn
    def f():
        (0,) [: complex]
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_complex_intro_tuple_long():
    @fp.fn
    def f():
        (0, 0, 0) [: complex]
    with pytest.raises(typy.TypeError):
        f.typecheck()

class TestComplexIntroTuple:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            (1, 0) [: complex] # II
            (1, 0) [: complex_]
            (2.0, 3) [: complex] # FI
            (2.0, 3) [: complex_]
            (3.0, 3.0) [: complex] # FF
            (3.0, 3.0) [: complex_]
            (4, 3j) [: complex] # IC
            (4, 3j) [: complex_]
            x [: int] = 1
            (x, 5) [: complex]
            (x, 6) [: complex_]
            (7, x) [: complex]
            (8, x) [: complex_]
            y [: float] = 1
            (y, 9) [: complex]
            (y, 10) [: complex_]
            (11, y) [: complex]
            (12, y) [: complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                __builtin__.complex(1.0, 0)
                __builtin__.complex(1.0, 0)
                __builtin__.complex(2.0, 3)
                __builtin__.complex(2.0, 3)
                __builtin__.complex(3.0, 3.0)
                __builtin__.complex(3.0, 3.0)
                __builtin__.complex(4.0, 3.0)
                __builtin__.complex(4.0, 3.0)
                x = 1
                __builtin__.complex(x, 5)
                __builtin__.complex(x, 6)
                __builtin__.complex(7.0, x)
                __builtin__.complex(8.0, x)
                y = 1.0
                __builtin__.complex(y, 9)
                __builtin__.complex(y, 10)
                __builtin__.complex(11.0, y)
                return __builtin__.complex(12.0, y)""")

def test_complex_intro_tuple_rl_bad():
    @fp.fn
    def f():
        x [: bool] = True
        (x, 0) [: complex]
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_complex_intro_tuple_im_bad():
    @fp.fn
    def f():
        x [: bool] = True
        (0, x) [: complex]
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_complex_ascription_on_string():
    @fp.fn
    def test():
        "3" [: complex]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestComplexUnaryOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: complex]
            x_plus = +x
            x_plus [: complex]
            x_minus = -x
            x_minus [: complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (123+0j)
                x_plus = (+ x)
                x_plus
                x_minus = (- x)
                return x_minus""")

def test_complex_no_not():
    @fp.fn
    def test():
        not (3 [: complex])
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_no_invert():
    @fp.fn
    def test():
        x [: complex] = 3
        ~x
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestFloatBinopsCC:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: complex]
            y = 456 [: complex]
            x_plus_y = x + y
            x_plus_y [: complex]
            x_minus_y = x - y
            x_minus_y [: complex]
            x_mult_y = x * y
            x_mult_y [: complex]
            x_pow_y = x ** y
            x_pow_y [: complex]
            x_div_y = x / y
            x_div_y [: complex]
            x_floordiv_y = x // y
            x_floordiv_y [: complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (123+0j)
                y = (456+0j)
                x_plus_y = (x + y)
                x_plus_y
                x_minus_y = (x - y)
                x_minus_y
                x_mult_y = (x * y)
                x_mult_y
                x_pow_y = (x ** y)
                x_pow_y
                x_div_y = (x / y)
                x_div_y
                x_floordiv_y = (x // y)
                return x_floordiv_y""")

def test_complex_no_mod():
    @fp.fn
    def test():
        x [: complex] = 3
        x % x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_no_lshift():
    @fp.fn
    def test():
        x [: complex] = 3
        x << x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_no_rshift():
    @fp.fn
    def test():
        x [: complex] = 3
        x >> x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_no_bitor():
    @fp.fn
    def test():
        x [: complex] = 3
        x | x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_no_bitxor():
    @fp.fn
    def test():
        x [: complex] = 3
        x ^ x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_no_bitand():
    @fp.fn
    def test():
        x [: complex] = 3
        x & x
    with pytest.raises(typy.TypeError):
        test.typecheck()
 
class TestComplexCompareOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: complex]
            x_eq_y = (x == 456 == 789)
            x_eq_y [: bool]
            x_neq_y = (x != 456 != 789)
            x_neq_y [: bool]
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
                x = (123+0j)
                x_eq_y = (x == (456+0j) == (789+0j))
                x_eq_y
                x_neq_y = (x != (456+0j) != (789+0j))
                x_neq_y
                x_is_y = (x is (456+0j) is (789+0j))
                x_is_y
                x_isnot_y = (x is not (456+0j) is not (789+0j))
                return x_isnot_y""")

def test_complex_Lt():
    @fp.fn
    def test():
        x [: complex] = 123
        y [: complex] = 456
        x < y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_LtE():
    @fp.fn
    def test():
        x [: complex] = 123
        y [: complex] = 456
        x <= y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_Gt():
    @fp.fn
    def test():
        x [: complex] = 123
        y [: complex] = 456
        x > y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_GtE():
    @fp.fn
    def test():
        x [: complex] = 123
        y [: complex] = 456
        x >= y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_In():
    @fp.fn
    def test():
        x [: complex] = 123
        y [: complex] = 456
        x in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_NotIn():
    @fp.fn
    def test():
        x [: complex] = 123
        y [: complex] = 456
        x not in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_And():
    @fp.fn
    def test():
        x [: complex] = 123
        y [: complex] = 456
        x and y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_complex_Or():
    @fp.fn
    def test():
        x [: complex] = 123
        y [: complex] = 456
        x or y
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestComplexComponents():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: complex] = 456
            r [: float] = x.real
            x.imag
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (456+0j)
                r = x.real
                return x.imag""")

class TestComplexConjugate():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: complex] = 456
            x.conjugate()
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (456+0j)
                return x.conjugate()""")

# 
# conversions
#

class TestConvertIF():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: int] = 456
            x.f
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 456
                return __builtin__.float(x)""")

class TestConvertIC():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: int] = 456
            x.c
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 456
                return __builtin__.complex(x)""")

class TestConvertFC():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: float] = 456
            x.c
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 456.0
                return __builtin__.complex(x)""")

#
# str
# 

class TestStringIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            "test" [: str]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), str]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 'test'""")

class TestStringIncIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            "test" [: str_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), str]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 'test'""")

def test_string_num_intro():
    @fp.fn
    def test(self):
        123 [: str]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestStringAdd:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            ("test" [: str]) + "test"
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), str]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ('test' + 'test')""")

class TestStringCompare:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = "abc" [: str] == "def" == "ghi"
            x [: bool]
            x = "abc" [: str] != "def" != "ghi"
            x [: bool]
            x = "abc" [: str] is "def" is "ghi"
            x [: bool]
            x = "abc" [: str] is not "def" is not "ghi"
            x [: bool]
            x = "abc" [: str] in "def" in "ghi"
            x [: bool]
            x = "abc" [: str] not in "def" not in "ghi"
            x [: bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = ('abc' == 'def' == 'ghi')
                x
                x = ('abc' != 'def' != 'ghi')
                x
                x = ('abc' is 'def' is 'ghi')
                x
                x = ('abc' is not 'def' is not 'ghi')
                x
                x = ('abc' in 'def' in 'ghi')
                x
                x = ('abc' not in 'def' not in 'ghi')
                return x""") 

class TestStringSubscript:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: str] = "abcdefg"
            y = x[0]
            y [: str]
            y = x[0:1]
            y [: str]
            y = x[0:1:2]
            y [: str]
            y = x[0:]
            y [: str]
            # no x[:1] because that's ascription syntax
            # can always use x[0:1] for this
            y = x[0:1:]
            y [: str]
            y = x[0::1]
            y [: str]
            y = x[:0:1]
            y [: str]
            y = x[0::]
            y [: str]
            y = x[:0:]
            y [: str]
            y = x[::0]
            y [: str]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), str]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 'abcdefg'
                y = x[0]
                y
                y = x[0:1]
                y
                y = x[0:1:2]
                y
                y = x[0:]
                y
                y = x[0:1]
                y
                y = x[0::1]
                y
                y = x[:0:1]
                y
                y = x[0:]
                y
                y = x[:0]
                y
                y = x[::0]
                return y""")

# 
# tpl
#
from typy.std import tpl
import ordereddict
OD = ordereddict.OrderedDict

def test_tpl_formation_unit():
    assert isinstance(tpl[()], typy.Type)
    assert tpl[()].idx == OD(())

def test_tpl_formation_single_ty():
    assert isinstance(tpl[int], typy.Type)
    assert tpl[int].idx == OD(((0, (0, int)),))

def test_tpl_formation_two_ty():
    assert isinstance(tpl[int, int], typy.Type)
    assert tpl[int, int].idx == OD((
        (0, (0, int)),
        (1, (1, int))
    ))

def test_tpl_formation_single_noty():
    with pytest.raises(typy.TypeFormationError):
        tpl["int"]

def test_tpl_formation_two_noty():
    with pytest.raises(typy.TypeFormationError):
        tpl[int, "int"]

def test_tpl_formation_single_label():
    assert tpl["lbl0" : int].idx == OD((
        ("lbl0", (0, int)),
    ))

def test_tpl_formation_two_labels():
    assert tpl["lbl0": int, "lbl1": str].idx == OD((
        ("lbl0", (0, int)),
        ("lbl1", (1, str))
    ))

def test_tpl_formation_duplicate_labels():
    with pytest.raises(typy.TypeFormationError):
        tpl["lbl0": int, "lbl0": str]

def test_tpl_formation_empty_lbl():
    with pytest.raises(typy.TypeFormationError):
        tpl["": int]

def test_tpl_formation_int_labels():
    assert tpl[1 : int, 0 : int].idx == OD((
        (1, (0, int)),
        (0, (1, int))
    ))

def test_tpl_formation_neg_label():
    with pytest.raises(typy.TypeFormationError):
        tpl[-1 : int]

def test_tpl_formation_non_string_label():
    with pytest.raises(typy.TypeFormationError):
        tpl[None : int]

def test_tpl_formation_non_type_component():
    with pytest.raises(typy.TypeFormationError):
        tpl["lbl0" : None]

def test_tpl_inc_ty_formation():
    assert isinstance(tpl[...], typy.IncompleteType)

def test_tpl_inc_ty_formation_bad():
    with pytest.raises(typy.TypeFormationError):
        tpl[..., 'lbl0' : int]

class TestTplTupleIntroUnit:
    @pytest.fixture
    def f(self):
        @fp.fn 
        def f():
            () [: tpl[()]]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl[()]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

class TestTplTupleIncIntroUnit:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            () [: tpl]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl[()]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ()""")

class TestTplTupleIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: str] = "test"
            y [: int] = 0
            z1 [: tpl[str]] = (x,)
            z2 [: tpl[str, int]] = (x, y)
            z3 [: tpl['lbl0': str]] = (x,)
            z4 [: tpl['lbl0': str, 'lbl1': int]] = (x, y)
            z4
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl['lbl0': str, 'lbl1': int]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 'test'
                y = 0
                z1 = (x,)
                z2 = (x, y)
                z3 = (x,)
                z4 = (x, y)
                return z4""")

def test_tpl_Tuple_intro_few():
    @fp.fn
    def test():
        x [: str] = "test"
        z [: tpl[str, int]] = (x,)
        z
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Tuple_intro_many():
    @fp.fn
    def test():
        x [: str] = "test"
        z [: tpl[str, str, int]] = (x, x)
        z
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestTplTupleIncIntro():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: str] = "test"
            y [: int] = 0
            z1 [: tpl]  = () 
            z2 [: tpl] = (x, y)
            z2
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl[str, int]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 'test'
                y = 0
                z1 = ()
                z2 = (x, y)
                return z2""")

class TestTplDictIntro():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            z1 [: tpl[str, int]] = {0 : "test", 1 : 0}
            z2 [: tpl['lbl0' : str, 'lbl1' : int]] = {'lbl0': "test", 'lbl1': 0}
            z3 [: tpl['lbl0' : str, 'lbl1' : int]] = {'lbl1': 0, 'lbl0': "test"}
            z3
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl['lbl0' : str, 'lbl1' : int]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                z1 = (lambda x: (x[0], x[1]))(('test', 0))
                z2 = (lambda x: (x[0], x[1]))(('test', 0))
                z3 = (lambda x: (x[1], x[0]))((0, 'test'))
                return z3""")

def test_tpl_Dict_intro_few():
    @fp.fn
    def test():
        z1 [: tpl[str, int]] = {0 : "test"}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Dict_intro_many():
    @fp.fn 
    def test():
        z1 [: tpl[str, int]] = {0 : "test", 1 : 0, 2 : 0}
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestTplDictIncIntro():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: str] = "test"
            y [: int] = 0
            z1 [: tpl] = {'lbl0' : x, 'lbl1' : y}
            z1
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl['lbl0' : str, 'lbl1' : int]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 'test'
                y = 0
                z1 = (lambda x: (x[0], x[1]))((x, y))
                return z1""")

def test_tpl_Dict_empty_lbl():
    @fp.fn
    def test():
        x [: str] = "test"
        z1 [: tpl] = {'' : x}
        z1
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Dict_neg_lbl():
    @fp.fn
    def test():
        x [: str] = "test"
        z1 [: tpl] = {-1 : x}
        z1
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Dict_bad_lbl():
    @fp.fn 
    def test():
        x [: str] = "test"
        z1 [: tpl] = {None : x}
        z1
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Dict_duplicate_lbl():
    @fp.fn
    def test():
        x [: str] = "test"
        y [: int] = 0
        z1 [: tpl] = {"lbl0": x, "lbl0": y}
        z1
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestTplDictAttribute():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f(x):
            {x : tpl['lbl0' : str]}
            x.lbl0
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[tpl['lbl0' : str], str]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return x[0]""")

class TestTplDictAttribute():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f(x):
            {x : tpl[str, 'lbl1' : int]}
            (x[0], x['lbl1']) [: tpl]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[tpl[str, 'lbl1' : int], tpl[str, int]]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (x[0], x[1])""")
