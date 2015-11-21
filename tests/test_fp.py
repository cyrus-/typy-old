"""py.test based tests for typy.fn

To run:
  $ py.test test_fp.py
"""
import ast

import pytest
import typy
import typy.fp as fp

unit = fp.unit
def test_unit_index():
    with pytest.raises(typy.TypeFormationError):
        fp.unit_[0]

boolean = fp.boolean
def test_boolean_index():
    with pytest.raises(typy.TypeFormationError):
        fp.boolean_[0]

def test_stdfn_noargs():
    fn_ty = fp.fn[(), unit]
    assert isinstance(fn_ty, typy.Type)
    assert fn_ty.idx == ((), unit)

def test_stdfn_onearg():
    fn_ty = fp.fn[unit, unit]
    assert isinstance(fn_ty, typy.Type)
    assert fn_ty.idx == ((unit,), unit)

def test_stdfn_twoargs():
    fn_ty = fp.fn[unit, unit, unit]
    assert isinstance(fn_ty, typy.Type)
    assert fn_ty.idx == ((unit, unit), unit)

def test_stdfn_tupled_args():
    fn_ty = fp.fn[(unit, unit), unit]
    assert isinstance(fn_ty, typy.Type)
    assert fn_ty.idx == ((unit, unit), unit)

def test_stdfn_badidx_nottuple():
    with pytest.raises(typy.TypeFormationError):
        fp.fn[0]

def test_stdfn_badidx_nottype():
    with pytest.raises(typy.TypeFormationError):
        fp.fn[0, unit]

def test_stdfn_badidx_nottype2():
    with pytest.raises(typy.TypeFormationError):
        fp.fn[(unit, 0), unit]

def test_stdfn_badidx_rtnottype():
    with pytest.raises(typy.TypeFormationError):
        fp.fn[unit, 0]

def test_stdfn_badidx_too_short():
    with pytest.raises(typy.TypeFormationError):
        fp.fn[unit]

def test_stdfn_incty_construction_all_elided():
    fn_incty = fp.fn[...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == Ellipsis 

def test_stdfn_incty_construction_noargs_rty_elided():
    fn_incty = fp.fn[(), ...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == ((), Ellipsis)

def test_stdfn_incty_construction_onearg_rty_elided():
    fn_incty = fp.fn[unit, ...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == ((unit,), Ellipsis)

def test_stdfn_incty_construction_twoargs_rty_elided():
    fn_incty = fp.fn[unit, unit, ...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == ((unit, unit), Ellipsis)

def test_stdfn_incty_construction_tupled_args_rty_elided():
    fn_incty = fp.fn[(unit, unit), ...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == ((unit, unit), Ellipsis)

def test_stdfn_incty_badidx_arg_elided():
    with pytest.raises(typy.TypeFormationError):
        fp.fn[..., unit]

def test_stdfn_incty_badidx_arg_nottuple():
    with pytest.raises(typy.TypeFormationError):
        fp.fn[0, ...]

def test_stdfn_incty_badidx_arg_nottype():
    with pytest.raises(typy.TypeFormationError):
        fp.fn[(unit, 0), ...]

def test_stdfn_direct_decorator():
    @fp.fn
    def test():
        pass
    assert isinstance(test, typy.Fn)
    assert isinstance(test.tree, ast.FunctionDef)

def test_stdfn_docstring():
    fnty = fp.fn[unit, unit]
    @fnty
    def test():
        """This is a docstring."""
    assert test.__doc__ == test.func_doc == """This is a docstring."""

def test_stdfn_incty_docstring():
    @fp.fn
    def test():
        """This is a docstring."""
    assert test.__doc__ == test.func_doc == """This is a docstring."""

def test_stdfn_arg_count_correct():
    fn_ty = fp.fn[unit, unit]
    @fn_ty
    def test(x):
        """This is a docstring."""
    assert test.typecheck() == fn_ty

def test_stdfn_arg_count_incorrect():
    fn_ty = fp.fn[unit, unit]
    @fn_ty
    def test():
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_arg_count_zero():
    fn_ty = fp.fn[(), unit]
    @fn_ty
    def test():
        """This is a docstring."""
    assert test.typecheck() == fn_ty

def test_stdfn_arg_count_zero_incorrect():
    fn_ty = fp.fn[(), unit]
    @fn_ty
    def test(x):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_varargs_unsupported():
    fn_ty = fp.fn[unit, unit]
    @fn_ty 
    def test(*x):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_kwargs_unsupported():
    fn_ty = fp.fn[unit, unit]
    @fn_ty 
    def test(**x):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_defaults_unsupported():
    fn_ty = fp.fn[unit, unit]
    @fn_ty 
    def test(x=()):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_Pass():
    fn_ty = fp.fn[(), unit]
    @fn_ty
    def test():
        """This is a docstring."""
        pass
    assert test.typecheck() == fn_ty

def test_stdfn_Pass_type():
    fn_ty = fp.fn[(), boolean]
    @fn_ty
    def test():
        pass
    with pytest.raises(typy.TypeMismatchError):
        test.typecheck()

def test_stdfn_incty_empty():
    fn_ty = fp.fn[(), ...]
    @fn_ty
    def test():
        """This is a docstring."""
    assert test.typecheck() == fp.fn[(), unit]

def test_stdfn_incty_Pass():
    fn_ty = fp.fn[(), ...]
    @fn_ty
    def test():
        pass
    assert test.typecheck() == fp.fn[(), unit]

def test_stdfn_sig():
    @fp.fn
    def test():
        """This is a docstring."""
        {}
    assert test.typecheck() == fp.fn[(), unit]

def test_stdfn_sig_r():
    @fp.fn
    def test():
        """This is a docstring."""
        {} >> unit
    assert test.typecheck() == fp.fn[(), unit]

def test_stdfn_sig_Pass():
    @fp.fn
    def test():
        """This is a docstring."""
        {}
        pass
    assert test.typecheck() == fp.fn[(), unit]

def test_stdfn_sig_r_Pass():
    @fp.fn
    def test():
        """This is a docstring."""
        {} >> unit
        pass
    assert test.typecheck() == fp.fn[(), unit]

def test_stdfn_sig_args():
    @fp.fn
    def test(x):
        {unit}
        pass
    assert test.typecheck() == fp.fn[(unit,), unit]

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

def test_stdfn_sig_named_args():
    @fp.fn
    def test(x):
        {x : unit}
        pass
    assert test.typecheck() == fp.fn[unit, unit]

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

def test_stdfn_sig_complex_types():
    q = [unit, boolean]
    @fp.fn
    def test(x, y):
        {x : q[1], y : q[0]} >> q[0]
    assert test.typecheck() == fp.fn[boolean, unit, unit]

def test_redundant_sigs():
    fn_ty = fp.fn[(), ...]
    @fn_ty 
    def test():
        {}
    assert test.typecheck() == fp.fn[(), unit]

def test_redundant_sigs_2():
    fn_ty = fp.fn[(unit, unit), unit]
    @fn_ty
    def test(x, y):
        {unit, unit} >> unit
    assert test.typecheck() == fp.fn[(unit, unit), unit]

def test_redundant_sigs_3():
    fn_ty = fp.fn[(), ...]
    @fn_ty
    def test():
        {} >> unit
    assert test.typecheck() == fp.fn[(), unit]

def test_redundant_sigs_4():
    fn_ty = fp.fn[(unit, unit), unit]
    @fn_ty
    def test(x, y):
        {boolean, boolean}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_redundant_sigs_5():
    fn_ty = fp.fn[(boolean, boolean), unit]
    @fn_ty
    def test(x, y):
        {boolean, boolean}
    assert test.typecheck() == fp.fn[(boolean, boolean), unit]

def test_redundant_sigs_6():
    fn_ty = fp.fn[(unit, unit), ...]
    @fn_ty
    def test(x, y):
        {boolean, unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_unit_intro():
    @fp.fn
    def test():
        {} >> unit
        ()
    assert test.typecheck() == fp.fn[(), unit]

def test_unit_ascription():
    @fp.fn
    def test():
        () [: unit]
    assert test.typecheck() == fp.fn[(), unit]

def test_unit_ascription_toomany():
    @fp.fn
    def test():
        (1, 2) [: unit]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_unit_inc_ascription():
    @fp.fn 
    def test():
        () [: fp.unit_[...]]
    assert test.typecheck() == fp.fn[(), unit]

def test_unit_inc_ascription_toomany():
    @fp.fn
    def test():
        (1, 2) [: fp.unit_[...]]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_unit_omitted_inc_ascription():
    @fp.fn
    def test():
        () [: fp.unit_]
    assert test.typecheck() == fp.fn[(), unit]

def test_unit_bad_ascription():
    @fp.fn
    def test():
        () [: boolean]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_unit_bad_inc_ascription():
    @fp.fn
    def test():
        () [: fp.boolean_[...]]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_unit_bad_omitted_inc_ascription():
    @fp.fn
    def test():
        () [: fp.boolean_]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_boolean_ascription_True():
    @fp.fn
    def test():
        True [: boolean]
    assert test.typecheck() == fp.fn[(), boolean]

def test_boolean_ascription_False():
    @fp.fn
    def test():
        False [: boolean]
    assert test.typecheck() == fp.fn[(), boolean]

def test_boolean_ascription_bad():
    @fp.fn
    def test():
        Bad [: boolean]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_variable_lookup():
    @fp.fn
    def test(x):
        {x : boolean}
        x
    assert test.typecheck() == fp.fn[boolean, boolean]

def test_variable_lookup_ana():
    @fp.fn
    def test(x):
        {x : boolean} >> boolean
        x
    assert test.typecheck() == fp.fn[boolean, boolean]

def test_variable_lookup_notfound():
    @fp.fn 
    def test(x):
        {x : boolean}
        y
    with pytest.raises(typy.TypeError):
        test.typecheck()
    
def test_assign_syn():
    @fp.fn
    def test():
        x = () [: unit]
        x
    assert test.typecheck() == fp.fn[(), unit]

def test_assign_ana():
    @fp.fn
    def test():
        x = () [: unit]
        x = ()
        x
    assert test.typecheck() == fp.fn[(), unit]

def test_assign_bad():
    @fp.fn
    def test(x):
        {unit}
        x = True [: boolean]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_assign_ascription():
    @fp.fn
    def test():
        x [: boolean] = True
        x
    assert test.typecheck() == fp.fn[(), boolean]

def test_assign_ascription_dbl():
    @fp.fn
    def test():
        x [: boolean] = True
        x [: boolean] = True
        x
    assert test.typecheck() == fp.fn[(), boolean]

def test_assign_ascription_dbl_inconsistent():
    @fp.fn
    def test():
        x [: boolean] = True 
        x [: unit] = ()
        x
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_assign_multiple():
    @fp.fn
    def test():
        x [: boolean] = y = True
        y
    assert test.typecheck() == fp.fn[(), boolean]

def test_assign_multiple_ascription():
    @fp.fn
    def test():
        x [: boolean] = y [: boolean] = True
        y
    assert test.typecheck() == fp.fn[(), boolean]

def test_assign_multiple_ascription_bad():
    @fp.fn
    def test():
        x [: boolean] = y [: unit] = True
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_assign_multiple_ascription_bad_2():
    @fp.fn
    def test(x):
        {x : boolean}
        x [: boolean] = y [: unit] = True
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_assign_multiple_ascription_bad_3():
    @fp.fn
    def test(x):
        {x : unit}
        x [: boolean] = y [: boolean] = True
    with pytest.raises(typy.TypeError):
        test.typecheck()

