"""py.test based tests for typy.fn

To run:
  $ py.test test_fp.py
"""
import ast

import pytest

from utils import *

import typy
import typy.fp as fp
from typy.std import bool_, bool
unit = fp.unit

# Type Formation
class TestTypeFormation:
    def test_unit_index(self):
        with pytest.raises(typy.TypeFormationError):
            fp.unit_[0]

    def test_bool_index(self):
        with pytest.raises(typy.TypeFormationError):
            bool_[0]

    def test_stdfn_noargs(self):
        fn_ty = fp.fn[(), unit]
        assert isinstance(fn_ty, typy.Type)
        assert fn_ty.idx == ((), unit)

    def test_stdfn_onearg(self):
        fn_ty = fp.fn[unit, unit]
        assert isinstance(fn_ty, typy.Type)
        assert fn_ty.idx == ((unit,), unit)

    def test_stdfn_twoargs(self):
        fn_ty = fp.fn[unit, unit, unit]
        assert isinstance(fn_ty, typy.Type)
        assert fn_ty.idx == ((unit, unit), unit)

    def test_stdfn_tupled_args(self):
        fn_ty = fp.fn[(unit, unit), unit]
        assert isinstance(fn_ty, typy.Type)
        assert fn_ty.idx == ((unit, unit), unit)

    def test_stdfn_badidx_nottuple(self):
        with pytest.raises(typy.TypeFormationError):
            fp.fn[0]

    def test_stdfn_badidx_nottype(self):
        with pytest.raises(typy.TypeFormationError):
            fp.fn[0, unit]

    def test_stdfn_badidx_nottype2(self):
        with pytest.raises(typy.TypeFormationError):
            fp.fn[(unit, 0), unit]

    def test_stdfn_badidx_rtnottype(self):
        with pytest.raises(typy.TypeFormationError):
            fp.fn[unit, 0]

    def test_stdfn_badidx_too_short(self):
        with pytest.raises(typy.TypeFormationError):
            fp.fn[unit]

    def test_stdfn_incty_construction_all_elided(self):
        fn_incty = fp.fn[...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == Ellipsis 

    def test_stdfn_incty_construction_noargs_rty_elided(self):
        fn_incty = fp.fn[(), ...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == ((), Ellipsis)

    def test_stdfn_incty_construction_onearg_rty_elided(self):
        fn_incty = fp.fn[unit, ...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == ((unit,), Ellipsis)

    def test_stdfn_incty_construction_twoargs_rty_elided(self):
        fn_incty = fp.fn[unit, unit, ...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == ((unit, unit), Ellipsis)

    def test_stdfn_incty_construction_tupled_args_rty_elided(self):
        fn_incty = fp.fn[(unit, unit), ...]
        assert isinstance(fn_incty, typy.IncompleteType)
        assert fn_incty.inc_idx == ((unit, unit), Ellipsis)

    def test_stdfn_incty_badidx_arg_elided(self):
        with pytest.raises(typy.TypeFormationError):
            fp.fn[..., unit]

    def test_stdfn_incty_badidx_arg_nottuple(self):
        with pytest.raises(typy.TypeFormationError):
            fp.fn[0, ...]

    def test_stdfn_incty_badidx_arg_nottype(self):
        with pytest.raises(typy.TypeFormationError):
            fp.fn[(unit, 0), ...]

# fn

class TestStdFnDirectDecorator:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            pass
        return f

    def test_is_fn(self, f):
        assert isinstance(f, typy.Fn)

    def test_tree(self, f):
        assert isinstance(f.tree, ast.FunctionDef)

def test_stdfn_docstring():
    fnty = fp.fn[unit, unit]
    @fnty
    def f():
        """This is a docstring."""
    assert f.__doc__ == f.func_doc == """This is a docstring."""

def test_stdfn_incty_docstring():
    @fp.fn
    def f():
        """This is a docstring."""
    assert f.__doc__ == f.func_doc == """This is a docstring."""

class TestStdFnArgCountCorrect:
    @pytest.fixture
    def fn_ty(self):
        return fp.fn[unit, unit]

    @pytest.fixture
    def f(self, fn_ty):
        @fn_ty
        def f(x):
            """This is a docstring."""
        return f

    def test_type(self, f, fn_ty):
        assert f.typecheck() == fn_ty

    def test_translate(self, f):
        translation_eq(f, """
            def f(x):
                pass""")

def test_stdfn_arg_count_incorrect():
    fn_ty = fp.fn[unit, unit]
    @fn_ty
    def test():
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestStdFnArgCountZero:
    @pytest.fixture
    def fn_ty(self): return fp.fn[(), unit]

    @pytest.fixture
    def f(self, fn_ty):
        @fn_ty
        def f():
            """This is a docstring."""
        return f

    def test_type(self, f, fn_ty):
        assert f.typecheck() == fn_ty

    def test_translate(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

def test_stdfn_arg_count_zero_incorrect():
    fn_ty = fp.fn[(), unit]
    @fn_ty
    def f(x):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_stdfn_varargs_unsupported():
    fn_ty = fp.fn[unit, unit]
    @fn_ty 
    def f(*x):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_stdfn_kwargs_unsupported():
    fn_ty = fp.fn[unit, unit]
    @fn_ty 
    def f(**x):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_stdfn_defaults_unsupported():
    fn_ty = fp.fn[unit, unit]
    @fn_ty 
    def f(x=()):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        f.typecheck()

class TestStdFnPass:
    @pytest.fixture
    def fn_ty(self): return fp.fn[(), unit]

    @pytest.fixture
    def f(self, fn_ty):
        @fn_ty
        def f():
            """This is a docstring."""
            pass
        return f

    def test_type(self, fn_ty, f):
        assert f.typecheck() == fn_ty

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

def test_stdfn_Pass_type():
    fn_ty = fp.fn[(), bool]
    @fn_ty
    def f():
        pass
    with pytest.raises(typy.TypeMismatchError):
        f.typecheck()

class TestStdFnIncTyEmpty:
    @pytest.fixture
    def f(self):
        fn_ty = fp.fn[(), ...]
        @fn_ty
        def f():
            """This is a docstring."""
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnIncTyPass:
    @pytest.fixture
    def f(self):
        fn_ty = fp.fn[(), ...]
        @fn_ty
        def f():
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSig:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            """This is a docstring."""
            {}
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSigR():
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            """This is a docstring."""
            {} >> unit
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSigPass:
    @pytest.fixture
    def f(self):    
        @fp.fn
        def f():
            """This is a docstring."""
            {}
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSigRPass:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            """This is a docstring."""
            {} >> unit
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

class TestStdFnSigArgs:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f(x):
            {unit}
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(unit,), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                pass""")

def test_stdfn_sig_args_too_many():
    @fp.fn
    def test(x):
        {unit, unit}
        pass
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_args_too_few():
    @fp.fn
    def test(x, y):
        {unit}
        pass
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestStdFnSigNamedArgs:
    @pytest.fixture 
    def f(self):
        @fp.fn
        def f(x):
            {x : unit}
            pass
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[unit, unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                pass""")

def test_stdfn_sig_named_args_too_many():
    @fp.fn
    def test(x):
        {x : unit, y : unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_named_args_too_few():
    @fp.fn
    def test(x, y):
        {x : unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_named_args_wrong_names():
    @fp.fn
    def test(x):
        {y : unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_named_args_wrong_names2():
    @fp.fn
    def test(x, y):
        {x : unit, z : unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestStdFnSigComplexTypes:
    @pytest.fixture
    def f(self):
        q = [unit, bool]
        @fp.fn
        def f(x, y):
            {x : q[1], y : q[0]} >> q[0]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[bool, unit, unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x, y):
                pass""")

class TestRedundantSigs:
    @pytest.fixture
    def f(self):
        fn_ty = fp.fn[(), ...]
        @fn_ty 
        def f():
            {}
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

class TestRedundantSigs2:
    @pytest.fixture
    def f(self):
        fn_ty = fp.fn[(unit, unit), unit]
        @fn_ty
        def f(x, y):
            {unit, unit} >> unit
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(unit, unit), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x, y):
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

class TestRedundantSigs3:
    @pytest.fixture
    def f(self):
        fn_ty = fp.fn[(), ...]
        @fn_ty
        def f():
            {} >> unit
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                pass""")

    #def test_eval(self, f):
    #    assert f() == None

def test_redundant_sigs_4():
    fn_ty = fp.fn[(unit, unit), unit]
    @fn_ty
    def f(x, y):
        {bool, bool}
    with pytest.raises(typy.TypeError):
        f.typecheck()

class TestRedundantSigs5:
    @pytest.fixture
    def f(self):
        fn_ty = fp.fn[(bool, bool), unit]
        @fn_ty
        def f(x, y):
            {bool, bool}
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(bool, bool), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x, y):
                pass""")

def test_redundant_sigs_6():
    fn_ty = fp.fn[(unit, unit), ...]
    @fn_ty
    def test(x, y):
        {bool, unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

# unit

class TestUnitIntro:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            {} >> unit
            ()
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return None""")

    #def test_eval(self, f):
    #    assert f() == None

class TestUnitAscription:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            () [: unit]
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return None""")

    #def test_eval(self, f):
    #    assert f() == None

class test_unit_ascription_toomany():
    @fp.fn
    def test():
        (1, 2) [: unit]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestUnitIncAscription:
    @pytest.fixture
    def f(self):
        @fp.fn 
        def f():
            () [: fp.unit_[...]]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return None""")

    #def test_eval(self, f):
    #    assert f() == None

def test_unit_inc_ascription_toomany():
    @fp.fn
    def test():
        (1, 2) [: fp.unit_[...]]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestUnitOmittedIncAscription:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            () [: fp.unit_]
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                return None""")

    #def test_eval(self, f):
    #    assert f() == None

def test_unit_bad_ascription():
    @fp.fn
    def test():
        () [: bool]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_unit_bad_inc_ascription():
    @fp.fn
    def test():
        () [: bool_[...]]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_unit_bad_omitted_inc_ascription():
    @fp.fn
    def test():
        () [: bool_]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

class TestUnitCompare:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: unit] = ()
            x_eq_y = (x == () == ())
            x_eq_y [: bool]
            x_neq_y = (x != () != ())
            x_neq_y [: bool]
            x_is_y = (x is () is ())
            x_is_y [: bool]
            x_isnot_y = (x is not () is not ())
            x_isnot_y [: bool]
        return f

    def test_type(self, f): 
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = None
                x_eq_y = (x == None == None)
                x_eq_y
                x_neq_y = (x != None != None)
                x_neq_y
                x_is_y = (x is None is None)
                x_is_y
                x_isnot_y = (x is not None is not None)
                return x_isnot_y""")

def test_unit_Lt():
    @fp.fn
    def f():
        x [: unit] = ()
        x < ()
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_unit_LtE():
    @fp.fn
    def f():
        x [: unit] = ()
        x <= ()
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_unit_Gt():
    @fp.fn
    def f():
        x [: unit] = ()
        x > ()
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_unit_GtE():
    @fp.fn
    def f():
        x [: unit] = ()
        x >= ()
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_unit_In():
    @fp.fn
    def f():
        x [: unit] = ()
        x in ()
    with pytest.raises(typy.TypeError):
        f.typecheck()

def test_unit_NotIn():
    @fp.fn
    def f():
        x [: unit] = ()
        x not in ()
    with pytest.raises(typy.TypeError):
        f.typecheck()

# Variables

class TestVariableLookup:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f(x):
            {x : bool}
            x
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[bool, bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return x""")

class TestVariableLookupAna:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f(x):
            {x : bool} >> bool
            x
        return f 

    def test_type(self, f):
        assert f.typecheck() == fp.fn[bool, bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f(x):
                return x""")

def test_variable_lookup_notfound():
    @fp.fn 
    def test(x):
        {x : bool}
        y
    with pytest.raises(typy.TypeError):
        test.typecheck()
    
class TestAssignSyn:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = () [: unit]
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = None
                return x""")

    #def test_eval(self, f):
    #    assert f() == None

class TestAssignAna:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x = () [: unit]
            x = ()
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), unit]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = None
                x = None
                return x""")

    #def test_eval(self, f):
    #    assert f() == None

def test_assign_bad():
    @fp.fn
    def test(x):
        {unit}
        x = True [: bool]
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestAssignAscription:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: bool] = True
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                return x""")

class TestAssignAscriptionDbl:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: bool] = True
            x [: bool] = True
            x
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = True
                x = True
                return x""")

def test_assign_ascription_dbl_inconsistent():
    @fp.fn
    def test():
        x [: bool] = True 
        x [: unit] = ()
        x
    with pytest.raises(typy.TypeError):
        test.typecheck()

class TestAssignMultiple:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: bool] = y = True
            y
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = y = True
                return y""")

class TestAssignMultipleAscription:
    @pytest.fixture
    def f(self):
        @fp.fn
        def f():
            x [: bool] = y [: bool] = True
            y
        return f

    def test_type(self, f):
        assert f.typecheck() == fp.fn[(), bool]

    def test_translation(self, f):
        translation_eq(f, """
            def f():
                x = y = True
                return y""")

def test_assign_multiple_ascription_bad():
    @fp.fn
    def test():
        x [: bool] = y [: unit] = True
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_assign_multiple_ascription_bad_2():
    @fp.fn
    def test(x):
        {x : bool}
        x [: bool] = y [: unit] = True
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_assign_multiple_ascription_bad_3():
    @fp.fn
    def test(x):
        {x : unit}
        x [: bool] = y [: bool] = True
    with pytest.raises(typy.TypeError):
        test.typecheck()
