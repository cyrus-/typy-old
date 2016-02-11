"""typy standard library tests"""
import pytest

from utils import * 

import typy
import typy.fp as fp
import typy.std as std

#
# Bool
#

from typy.std import Bool
from typy.std.boolean import Bool_

class TestBooleanAscriptionTrue:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            True [: Bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return True""")

class TestBooleanAscriptionFalse:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            False [: Bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return False""")

class TestBooleanIncAscription:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            True [: Bool_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return True""")

def test_Bool_ascription_bad():
    @fp.fn
    def test():
        Bad [: Bool]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestBooleanNot:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: Bool] = True
            not x
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                return (not x)""")

def test_Bool_Invert():
    @fp.fn
    def test():
        x [: Bool] = True
        ~x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Bool_UAdd():
    @fp.fn
    def test():
        x [: Bool] = True
        +x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Bool_USub():
    @fp.fn
    def test():
        x [: Bool] = True
        -x
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestBooleanCompareOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: Bool] = True
            x_eq_y = (x == True)
            x_eq_y [: Bool]
            x_neq_y = (x != True)
            x_neq_y [: Bool]
            x_is_y = (x is True)
            x_is_y [: Bool]
            x_isnot_y = (x is not True)
            x_isnot_y
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

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

def test_Bool_Lt():
    @fp.fn
    def test():
        x [: Bool] = True
        y [: Bool] = False
        x < y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Bool_LtE():
    @fp.fn
    def test():
        x [: Bool] = True
        y [: Bool] = False
        x <= y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Bool_Gt():
    @fp.fn
    def test():
        x [: Bool] = True
        y [: Bool] = False
        x > y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Bool_GtE():
    @fp.fn
    def test():
        x [: Bool] = True
        y [: Bool] = False
        x >= y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Bool_In():
    @fp.fn
    def test():
        x [: Bool] = True
        y [: Bool] = False
        x in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Bool_NotIn():
    @fp.fn
    def test():
        x [: Bool] = True
        y [: Bool] = False
        x not in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestBooleanBoolOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: Bool] = True
            x_and_y = (x and True and True and True)
            x_and_y [: Bool]
            x_or_y = (x or True or True or True)
            x_or_y [: Bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                x_and_y = (x and True and True and True)
                x_and_y
                x_or_y = (x or True or True or True)
                return x_or_y""")

#
# Int
#

from typy.std import Int
from typy.std.numeric import Int_

class TestIntegerIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: Int]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Int]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")

class TestIntegerIncIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: Int_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Int]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3""")

class TestIntegerLongIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: Int]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Int]

    def test_translation(self, f):  
        translation_eq(f, """
            def f():
                return 1234567890123456789012345678901234567890123456789012345678901234567890L""")

def test_Integer_ascription_on_Float():
    @fp.fn
    def test():
        3.0 [: Int]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Integer_ascription_on_Complex():
    @fp.fn
    def test():
        3.0j [: Int]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Integer_ascription_on_String():
    @fp.fn
    def test():
        "3" [: Int]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestIntegerUnaryOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: Int]
            x_plus = +x
            x_plus [: Int]
            x_minus = -x
            x_minus [: Int]
            x_invert = ~x
            x_invert [: Int]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Int]

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

def test_Integer_no_not():
    @fp.fn
    def test():
        not (3 [: Int])
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestIntegerBinops:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: Int]
            y = 456 [: Int]
            x_plus_y = x + y
            x_plus_y [: Int]
            x_minus_y = x - y
            x_minus_y [: Int]
            x_mult_y = x * y
            x_mult_y [: Int]
            x_mod_y = x % y
            x_mod_y [: Int]
            x_pow_y = x ** y
            x_pow_y [: Int]
            x_lshift_y = x << y
            x_lshift_y [: Int]
            x_rshift_y = x >> y
            x_rshift_y [: Int]
            x_bitor_y = x | y
            x_bitor_y [: Int]
            x_bitxor_y = x ^ y
            x_bitxor_y [: Int]
            x_bitand_y = x & y
            x_bitand_y [: Int]
            x_floordiv_y = x // y
            x_floordiv_y [: Int]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Int]

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

# see TestIntFloatDiv for Integer/Float division
def test_Integer_Int_div():
    @fp.fn
    def test():
        x [: Int] = 3
        x / x
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestIntegerCompareOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: Int]
            x_eq_y = (x == 456 == 789)
            x_eq_y [: Bool]
            x_neq_y = (x != 456 != 789)
            x_neq_y [: Bool]
            x_lt_y = (x < 456 < 789)
            x_lt_y [: Bool]
            x_lte_y = (x <= 456 <= 789)
            x_lte_y [: Bool]
            x_gt_y = (x > 456 > 789)
            x_gt_y [: Bool]
            x_gte_y = (x >= 456 >= 789)
            x_gte_y [: Bool]
            x_is_y = (x is 456 is 789)
            x_is_y [: Bool]
            x_isnot_y = (x is not 456 is not 789)
            x_isnot_y [: Bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

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

def test_Int_In():
    @fp.fn
    def test():
        x [: Int] = 123
        y [: Int] = 456
        x in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Int_NotIn():
    @fp.fn
    def test():
        x [: Int] = 123
        y [: Int] = 456
        x not in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Int_And():
    @fp.fn
    def test():
        x [: Int] = 123
        y [: Int] = 456
        x and y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Int_Or():
    @fp.fn
    def test():
        x [: Int] = 123
        y [: Int] = 456
        x or y
    with pytest.raises(typy.TypeError):
        test.typecheck()

#
# Float
#

from typy.std import Float
from typy.std.numeric import Float_

class TestFloatIntroF:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3.0 [: Float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestFloatIntroI:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: Float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestFloatIntroL:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: Float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 1.2345678901234567e+69""")

class TestIntegerIncIntroF:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3.0 [: Float_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestIntegerIncIntroI:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: Float_]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3.0""")

class TestFloatIntroL:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: Float_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 1.2345678901234567e+69""")

def test_Float_ascription_on_Complex():
    @fp.fn
    def test():
        3.0j [: Float]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Float_ascription_on_String():
    @fp.fn
    def test():
        "3" [: Float]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestFloatUnaryOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: Float]
            x_plus = +x
            x_plus [: Float]
            x_minus = -x
            x_minus [: Float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 123.0
                x_plus = (+ x)
                x_plus
                x_minus = (- x)
                return x_minus""")

def test_Float_no_not():
    @fp.fn
    def test():
        not (3 [: Float])
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Float_no_invert():
    @fp.fn
    def test():
        x [: Float] = 3
        ~x
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestFloatBinops:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: Float]
            y = 456 [: Float]
            x_plus_y = x + y
            x_plus_y [: Float]
            x_minus_y = x - y
            x_minus_y [: Float]
            x_mult_y = x * y
            x_mult_y [: Float]
            x_mod_y = x % y
            x_mod_y [: Float]
            x_pow_y = x ** y
            x_pow_y [: Float]
            x_div_y = x / y
            x_div_y [: Float]
            x_floordiv_y = x // y
            x_floordiv_y [: Float]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

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

def test_Float_no_lshift():
    @fp.fn
    def test():
        x [: Float] = 3
        x << x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Float_no_rshift():
    @fp.fn
    def test():
        x [: Float] = 3
        x >> x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Float_no_bitor():
    @fp.fn
    def test():
        x [: Float] = 3
        x | x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Float_no_bitxor():
    @fp.fn
    def test():
        x [: Float] = 3
        x ^ x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Float_no_bitand():
    @fp.fn
    def test():
        x [: Float] = 3
        x & x
    with pytest.raises(typy.TypeError):
        test.typecheck()
 
class TestFloatCompareOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: Float]
            x_eq_y = (x == 456 == 789)
            x_eq_y [: Bool]
            x_neq_y = (x != 456 != 789)
            x_neq_y [: Bool]
            x_lt_y = (x < 456 < 789)
            x_lt_y [: Bool]
            x_lte_y = (x <= 456 <= 789)
            x_lte_y [: Bool]
            x_gt_y = (x > 456 > 789)
            x_gt_y [: Bool]
            x_gte_y = (x >= 456 >= 789)
            x_gte_y [: Bool]
            x_is_y = (x is 456 is 789)
            x_is_y [: Bool]
            x_isnot_y = (x is not 456 is not 789)
            x_isnot_y [: Bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

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

def test_Float_In():
    @fp.fn
    def test():
        x [: Float] = 123
        y [: Float] = 456
        x in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Float_NotIn():
    @fp.fn
    def test():
        x [: Float] = 123
        y [: Float] = 456
        x not in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Float_And():
    @fp.fn
    def test():
        x [: Float] = 123
        y [: Float] = 456
        x and y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Float_Or():
    @fp.fn
    def test():
        x [: Float] = 123
        y [: Float] = 456
        x or y
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestIntFloatDiv:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: Int] = 3
            x / 2
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 3
                return (x / 2.0)""")

#
# Complex
#

from typy.std import Complex
from typy.std.numeric import Complex_

class TestComplexIntroI:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: Complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestComplexIntroF:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3.0 [: Complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestComplexIntroL:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: Complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (1.2345678901234567e+69+0j)""")

class TestComplexIntroC:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3j [: Complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3j""")

class TestComplexIncIntroI:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3 [: Complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestComplexIncIntroF:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3.0 [: Complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (3+0j)""")

class TestComplexIncIntroL:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            1234567890123456789012345678901234567890123456789012345678901234567890 [: Complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return (1.2345678901234567e+69+0j)""")

class TestComplexIncIntroC:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            3j [: Complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 3j""")

def test_Complex_Intro_tuple_short():
    @fp.fn
    def f():
        (0,) [: Complex]
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_Complex_Intro_tuple_long():
    @fp.fn
    def f():
        (0, 0, 0) [: Complex]
    with pytest.raises(typy.TypeError):
        f.typecheck()

class TestComplexIntroTuple:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            (1, 0) [: Complex] # II
            (1, 0) [: Complex_]
            (2.0, 3) [: Complex] # FI
            (2.0, 3) [: Complex_]
            (3.0, 3.0) [: Complex] # FF
            (3.0, 3.0) [: Complex_]
            (4, 3j) [: Complex] # IC
            (4, 3j) [: Complex_]
            x [: Int] = 1
            (x, 5) [: Complex]
            (x, 6) [: Complex_]
            (7, x) [: Complex]
            (8, x) [: Complex_]
            y [: Float] = 1
            (y, 9) [: Complex]
            (y, 10) [: Complex_]
            (11, y) [: Complex]
            (12, y) [: Complex_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

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

def test_Complex_Intro_tuple_rl_bad():
    @fp.fn
    def f():
        x [: Bool] = True
        (x, 0) [: Complex]
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_Complex_Intro_tuple_im_bad():
    @fp.fn
    def f():
        x [: Bool] = True
        (0, x) [: Complex]
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_Complex_ascription_on_String():
    @fp.fn
    def test():
        "3" [: Complex]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestComplexUnaryOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: Complex]
            x_plus = +x
            x_plus [: Complex]
            x_minus = -x
            x_minus [: Complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = (123+0j)
                x_plus = (+ x)
                x_plus
                x_minus = (- x)
                return x_minus""")

def test_Complex_no_not():
    @fp.fn
    def test():
        not (3 [: Complex])
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_no_invert():
    @fp.fn
    def test():
        x [: Complex] = 3
        ~x
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestFloatBinopsCC:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: Complex]
            y = 456 [: Complex]
            x_plus_y = x + y
            x_plus_y [: Complex]
            x_minus_y = x - y
            x_minus_y [: Complex]
            x_mult_y = x * y
            x_mult_y [: Complex]
            x_pow_y = x ** y
            x_pow_y [: Complex]
            x_div_y = x / y
            x_div_y [: Complex]
            x_floordiv_y = x // y
            x_floordiv_y [: Complex]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

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

def test_Complex_no_mod():
    @fp.fn
    def test():
        x [: Complex] = 3
        x % x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_no_lshift():
    @fp.fn
    def test():
        x [: Complex] = 3
        x << x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_no_rshift():
    @fp.fn
    def test():
        x [: Complex] = 3
        x >> x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_no_bitor():
    @fp.fn
    def test():
        x [: Complex] = 3
        x | x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_no_bitxor():
    @fp.fn
    def test():
        x [: Complex] = 3
        x ^ x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_no_bitand():
    @fp.fn
    def test():
        x [: Complex] = 3
        x & x
    with pytest.raises(typy.TypeError):
        test.typecheck()
 
class TestComplexCompareOps:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = 123 [: Complex]
            x_eq_y = (x == 456 == 789)
            x_eq_y [: Bool]
            x_neq_y = (x != 456 != 789)
            x_neq_y [: Bool]
            x_is_y = (x is 456 is 789)
            x_is_y [: Bool]
            x_isnot_y = (x is not 456 is not 789)
            x_isnot_y [: Bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

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

def test_Complex_Lt():
    @fp.fn
    def test():
        x [: Complex] = 123
        y [: Complex] = 456
        x < y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_LtE():
    @fp.fn
    def test():
        x [: Complex] = 123
        y [: Complex] = 456
        x <= y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_Gt():
    @fp.fn
    def test():
        x [: Complex] = 123
        y [: Complex] = 456
        x > y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_GtE():
    @fp.fn
    def test():
        x [: Complex] = 123
        y [: Complex] = 456
        x >= y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_In():
    @fp.fn
    def test():
        x [: Complex] = 123
        y [: Complex] = 456
        x in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_NotIn():
    @fp.fn
    def test():
        x [: Complex] = 123
        y [: Complex] = 456
        x not in y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_And():
    @fp.fn
    def test():
        x [: Complex] = 123
        y [: Complex] = 456
        x and y
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_Complex_Or():
    @fp.fn
    def test():
        x [: Complex] = 123
        y [: Complex] = 456
        x or y
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestComplexComponents():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: Complex] = 456
            r [: Float] = x.real
            x.imag
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

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
            x [: Complex] = 456
            x.conjugate()
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

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
            x [: Int] = 456
            x.f
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Float]

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
            x [: Int] = 456
            x.c
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

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
            x [: Float] = 456
            x.c
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Complex]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = 456.0
                return __builtin__.complex(x)""")

#
# Str
# 

from typy.std import Str
from typy.std.string import Str_

class TestStringIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            "test" [: Str]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Str]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 'test'""")

class TestStringIncIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            "test" [: Str_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Str]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return 'test'""")

def test_String_num_Intro():
    @fp.fn
    def test(self):
        123 [: Str]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestStringAdd:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            ("test" [: Str]) + "test"
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Str]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return ('test' + 'test')""")

class TestStringCompare:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = "abc" [: Str] == "def" == "ghi"
            x [: Bool]
            x = "abc" [: Str] != "def" != "ghi"
            x [: Bool]
            x = "abc" [: Str] is "def" is "ghi"
            x [: Bool]
            x = "abc" [: Str] is not "def" is not "ghi"
            x [: Bool]
            x = "abc" [: Str] in "def" in "ghi"
            x [: Bool]
            x = "abc" [: Str] not in "def" not in "ghi"
            x [: Bool]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Bool]

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
            x [: Str] = "abcdefg"
            y = x[0]
            y [: Str]
            y = x[0:1]
            y [: Str]
            y = x[0:1:2]
            y [: Str]
            y = x[0:]
            y [: Str]
            # no x[:1] because that's ascription syntax
            # can always use x[0:1] for this
            y = x[0:1:]
            y [: Str]
            y = x[0::1]
            y [: Str]
            y = x[:0:1]
            y [: Str]
            y = x[0::]
            y [: Str]
            y = x[:0:]
            y [: Str]
            y = x[::0]
            y [: Str]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), Str]

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
    assert isinstance(tpl[Int], typy.Type)
    assert tpl[Int].idx == OD(((0, (0, Int)),))

def test_tpl_formation_two_ty():
    assert isinstance(tpl[Int, Int], typy.Type)
    assert tpl[Int, Int].idx == OD((
        (0, (0, Int)),
        (1, (1, Int))
    ))

def test_tpl_formation_single_noty():
    with pytest.raises(typy.TypeFormationError):
        tpl["Int"]

def test_tpl_formation_two_noty():
    with pytest.raises(typy.TypeFormationError):
        tpl[Int, "Int"]

def test_tpl_formation_single_label():
    assert tpl["lbl0" : Int].idx == OD((
        ("lbl0", (0, Int)),
    ))

def test_tpl_formation_two_labels():
    assert tpl["lbl0": Int, "lbl1": Str].idx == OD((
        ("lbl0", (0, Int)),
        ("lbl1", (1, Str))
    ))

def test_tpl_formation_duplicate_labels():
    with pytest.raises(typy.TypeFormationError):
        tpl["lbl0": Int, "lbl0": Str]

def test_tpl_formation_empty_lbl():
    with pytest.raises(typy.TypeFormationError):
        tpl["": Int]

def test_tpl_formation_Int_labels():
    assert tpl[1 : Int, 0 : Int].idx == OD((
        (1, (0, Int)),
        (0, (1, Int))
    ))

def test_tpl_formation_neg_label():
    with pytest.raises(typy.TypeFormationError):
        tpl[-1 : Int]

def test_tpl_formation_non_String_label():
    with pytest.raises(typy.TypeFormationError):
        tpl[None : Int]

def test_tpl_formation_non_type_component():
    with pytest.raises(typy.TypeFormationError):
        tpl["lbl0" : None]

def test_tpl_inc_ty_formation():
    assert isinstance(tpl[...], typy.IncompleteType)

def test_tpl_inc_ty_formation_bad():
    with pytest.raises(typy.TypeFormationError):
        tpl[..., 'lbl0' : Int]

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
            x [: Str] = "test"
            y [: Int] = 0
            z1 [: tpl[Str]] = (x,)
            z2 [: tpl[Str, Int]] = (x, y)
            z3 [: tpl['lbl0': Str]] = (x,)
            z4 [: tpl['lbl0': Str, 'lbl1': Int]] = (x, y)
            z4
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl['lbl0': Str, 'lbl1': Int]]

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

def test_tpl_Tuple_Intro_few():
    @fp.fn
    def test():
        x [: Str] = "test"
        z [: tpl[Str, Int]] = (x,)
        z
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Tuple_Intro_many():
    @fp.fn
    def test():
        x [: Str] = "test"
        z [: tpl[Str, Str, Int]] = (x, x)
        z
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestTplTupleIncIntro():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: Str] = "test"
            y [: Int] = 0
            z1 [: tpl]  = () 
            z2 [: tpl] = (x, y)
            z2
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl[Str, Int]]

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
            z1 [: tpl[Str, Int]] = {0 : "test", 1 : 0}
            z2 [: tpl['lbl0' : Str, 'lbl1' : Int]] = {'lbl0': "test", 'lbl1': 0}
            z3 [: tpl['lbl0' : Str, 'lbl1' : Int]] = {'lbl1': 0, 'lbl0': "test"}
            z3
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl['lbl0' : Str, 'lbl1' : Int]]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                z1 = (lambda x: (x[0], x[1]))(('test', 0))
                z2 = (lambda x: (x[0], x[1]))(('test', 0))
                z3 = (lambda x: (x[1], x[0]))((0, 'test'))
                return z3""")

def test_tpl_Dict_Intro_few():
    @fp.fn
    def test():
        z1 [: tpl[Str, Int]] = {0 : "test"}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Dict_Intro_many():
    @fp.fn 
    def test():
        z1 [: tpl[Str, Int]] = {0 : "test", 1 : 0, 2 : 0}
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestTplDictIncIntro():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: Str] = "test"
            y [: Int] = 0
            z1 [: tpl] = {'lbl0' : x, 'lbl1' : y}
            z1
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), tpl['lbl0' : Str, 'lbl1' : Int]]

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
        x [: Str] = "test"
        z1 [: tpl] = {'' : x}
        z1
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Dict_neg_lbl():
    @fp.fn
    def test():
        x [: Str] = "test"
        z1 [: tpl] = {-1 : x}
        z1
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Dict_bad_lbl():
    @fp.fn 
    def test():
        x [: Str] = "test"
        z1 [: tpl] = {None : x}
        z1
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_tpl_Dict_duplicate_lbl():
    @fp.fn
    def test():
        x [: Str] = "test"
        y [: Int] = 0
        z1 [: tpl] = {"lbl0": x, "lbl0": y}
        z1
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestTplDictAttribute():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f(x):
            {x : tpl['lbl0' : Str]}
            x.lbl0
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[tpl['lbl0' : Str], Str]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return x[0]""")

class TestTplDictAttribute():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f(x):
            {x : tpl[Str, 'lbl1' : Int]}
            (x[0], x['lbl1']) [: tpl]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[tpl[Str, 'lbl1' : Int], tpl[Str, Int]]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return (x[0], x[1])""")
