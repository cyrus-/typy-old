"""py.test based tests for typy.std

To run:
  $ py.test test_std.py
"""
import ast

import pytest
import typy
import typy.std as std

unit = std.unit
def test_unit_index():
    with pytest.raises(typy.TypeFormationError):
        std.unit_[0]

boolean = std.boolean
def test_boolean_index():
    with pytest.raises(typy.TypeFormationError):
        std.boolean_[0]

def test_stdfn_noargs():
    fn_ty = std.fn[(), unit]
    assert isinstance(fn_ty, typy.Type)
    assert fn_ty.idx == ((), unit)

def test_stdfn_onearg():
    fn_ty = std.fn[unit, unit]
    assert isinstance(fn_ty, typy.Type)
    assert fn_ty.idx == ((unit,), unit)

def test_stdfn_twoargs():
    fn_ty = std.fn[unit, unit, unit]
    assert isinstance(fn_ty, typy.Type)
    assert fn_ty.idx == ((unit, unit), unit)

def test_stdfn_tupled_args():
    fn_ty = std.fn[(unit, unit), unit]
    assert isinstance(fn_ty, typy.Type)
    assert fn_ty.idx == ((unit, unit), unit)

def test_stdfn_badidx_nottuple():
    with pytest.raises(typy.TypeFormationError):
        std.fn[0]

def test_stdfn_badidx_nottype():
    with pytest.raises(typy.TypeFormationError):
        std.fn[0, unit]

def test_stdfn_badidx_nottype2():
    with pytest.raises(typy.TypeFormationError):
        std.fn[(unit, 0), unit]

def test_stdfn_badidx_rtnottype():
    with pytest.raises(typy.TypeFormationError):
        std.fn[unit, 0]

def test_stdfn_badidx_too_short():
    with pytest.raises(typy.TypeFormationError):
        std.fn[unit]

def test_stdfn_incty_construction_all_elided():
    fn_incty = std.fn[...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == Ellipsis 

def test_stdfn_incty_construction_noargs_rty_elided():
    fn_incty = std.fn[(), ...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == ((), Ellipsis)

def test_stdfn_incty_construction_onearg_rty_elided():
    fn_incty = std.fn[unit, ...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == ((unit,), Ellipsis)

def test_stdfn_incty_construction_twoargs_rty_elided():
    fn_incty = std.fn[unit, unit, ...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == ((unit, unit), Ellipsis)

def test_stdfn_incty_construction_tupled_args_rty_elided():
    fn_incty = std.fn[(unit, unit), ...]
    assert isinstance(fn_incty, typy.IncompleteType)
    assert fn_incty.inc_idx == ((unit, unit), Ellipsis)

def test_stdfn_incty_badidx_arg_elided():
    with pytest.raises(typy.TypeFormationError):
        std.fn[..., unit]

def test_stdfn_incty_badidx_arg_nottuple():
    with pytest.raises(typy.TypeFormationError):
        std.fn[0, ...]

def test_stdfn_incty_badidx_arg_nottype():
    with pytest.raises(typy.TypeFormationError):
        std.fn[(unit, 0), ...]

def test_stdfn_direct_decorator():
    @std.fn
    def test():
        pass
    assert isinstance(test, typy.Fn)
    assert isinstance(test.tree, ast.FunctionDef)

def test_stdfn_docstring():
    fnty = std.fn[unit, unit]
    @fnty
    def test():
        """This is a docstring."""
    assert test.__doc__ == test.func_doc == """This is a docstring."""

def test_stdfn_incty_docstring():
    @std.fn
    def test():
        """This is a docstring."""
    assert test.__doc__ == test.func_doc == """This is a docstring."""

def test_stdfn_arg_count_correct():
    fn_ty = std.fn[unit, unit]
    @fn_ty
    def test(x):
        """This is a docstring."""
    assert test.typecheck() == fn_ty

def test_stdfn_arg_count_incorrect():
    fn_ty = std.fn[unit, unit]
    @fn_ty
    def test():
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_arg_count_zero():
    fn_ty = std.fn[(), unit]
    @fn_ty
    def test():
        """This is a docstring."""
    assert test.typecheck() == fn_ty

def test_stdfn_arg_count_zero_incorrect():
    fn_ty = std.fn[(), unit]
    @fn_ty
    def test(x):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_varargs_unsupported():
    fn_ty = std.fn[unit, unit]
    @fn_ty 
    def test(*x):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_kwargs_unsupported():
    fn_ty = std.fn[unit, unit]
    @fn_ty 
    def test(**x):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_defaults_unsupported():
    fn_ty = std.fn[unit, unit]
    @fn_ty 
    def test(x=()):
        """This is a docstring."""
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_Pass():
    fn_ty = std.fn[(), unit]
    @fn_ty
    def test():
        """This is a docstring."""
        pass
    assert test.typecheck() == fn_ty

def test_stdfn_Pass_type():
    fn_ty = std.fn[(), boolean]
    @fn_ty
    def test():
        pass
    with pytest.raises(typy.TypeMismatchError):
        test.typecheck()

def test_stdfn_incty_empty():
    fn_ty = std.fn[(), ...]
    @fn_ty
    def test():
        """This is a docstring."""
    assert test.typecheck() == std.fn[(), unit]

def test_stdfn_incty_Pass():
    fn_ty = std.fn[(), ...]
    @fn_ty
    def test():
        pass
    assert test.typecheck() == std.fn[(), unit]

def test_stdfn_sig():
    @std.fn
    def test():
        """This is a docstring."""
        {}
    assert test.typecheck() == std.fn[(), unit]

def test_stdfn_sig_r():
    @std.fn
    def test():
        """This is a docstring."""
        {} >> unit
    assert test.typecheck() == std.fn[(), unit]

def test_stdfn_sig_Pass():
    @std.fn
    def test():
        """This is a docstring."""
        {}
        pass
    assert test.typecheck() == std.fn[(), unit]

def test_stdfn_sig_r_Pass():
    @std.fn
    def test():
        """This is a docstring."""
        {} >> unit
        pass
    assert test.typecheck() == std.fn[(), unit]

def test_stdfn_sig_args():
    @std.fn
    def test(x):
        {unit}
        pass
    assert test.typecheck() == std.fn[(unit,), unit]

def test_stdfn_sig_args_too_many():
    @std.fn
    def test(x):
        {unit, unit}
        pass
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_args_too_few():
    @std.fn
    def test(x, y):
        {unit}
        pass
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_named_args():
    @std.fn
    def test(x):
        {x : unit}
        pass
    assert test.typecheck() == std.fn[unit, unit]

def test_stdfn_sig_named_args_too_many():
    @std.fn
    def test(x):
        {x : unit, y : unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_named_args_too_few():
    @std.fn
    def test(x, y):
        {x : unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_named_args_wrong_names():
    @std.fn
    def test(x):
        {y : unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_named_args_wrong_names2():
    @std.fn
    def test(x, y):
        {x : unit, z : unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_stdfn_sig_complex_types():
    q = [unit, boolean]
    @std.fn
    def test(x, y):
        {x : q[1], y : q[0]} >> q[0]
    assert test.typecheck() == std.fn[boolean, unit, unit]

def test_redundant_sigs():
    fn_ty = std.fn[(), ...]
    @fn_ty 
    def test():
        {}
    assert test.typecheck() == std.fn[(), unit]

def test_redundant_sigs_2():
    fn_ty = std.fn[(unit, unit), unit]
    @fn_ty
    def test(x, y):
        {unit, unit} >> unit
    assert test.typecheck() == std.fn[(unit, unit), unit]

def test_redundant_sigs_3():
    fn_ty = std.fn[(), ...]
    @fn_ty
    def test():
        {} >> unit
    assert test.typecheck() == std.fn[(), unit]

def test_redundant_sigs_4():
    fn_ty = std.fn[(unit, unit), unit]
    @fn_ty
    def test(x, y):
        {boolean, boolean}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_redundant_sigs_5():
    fn_ty = std.fn[(boolean, boolean), unit]
    @fn_ty
    def test(x, y):
        {boolean, boolean}
    assert test.typecheck() == std.fn[(boolean, boolean), unit]

def test_redundant_sigs_6():
    fn_ty = std.fn[(unit, unit), ...]
    @fn_ty
    def test(x, y):
        {boolean, unit}
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_unit_intro():
    @std.fn
    def test():
        {} >> unit
        ()
    assert test.typecheck() == std.fn[(), unit]

def test_unit_ascription():
    @std.fn
    def test():
        () [: unit]
    assert test.typecheck() == std.fn[(), unit]

def test_unit_ascription_toomany():
    @std.fn
    def test():
        (1, 2) [: unit]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_unit_inc_ascription():
    @std.fn 
    def test():
        () [: std.unit_[...]]
    assert test.typecheck() == std.fn[(), unit]

def test_unit_inc_ascription_toomany():
    @std.fn
    def test():
        (1, 2) [: std.unit_[...]]
    with pytest.raises(typy.TypeError):
        test.typecheck()

def test_unit_omitted_inc_ascription():
    @std.fn
    def test():
        () [: std.unit_]
    assert test.typecheck() == std.fn[(), unit]

def test_unit_bad_ascription():
    @std.fn
    def test():
        () [: boolean]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_unit_bad_inc_ascription():
    @std.fn
    def test():
        () [: std.boolean_[...]]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_unit_bad_omitted_inc_ascription():
    @std.fn
    def test():
        () [: std.boolean_]
    with pytest.raises(typy.NotSupportedError):
        test.typecheck()

def test_boolean_ascription_True():
    @std.fn
    def test():
        True [: boolean]
    assert test.typecheck() == std.fn[(), boolean]

def test_boolean_ascription_False():
    @std.fn
    def test():
        False [: boolean]
    assert test.typecheck() == std.fn[(), boolean]

def test_boolean_ascription_bad():
    @std.fn
    def test():
        Bad [: boolean]
    with pytest.raises(typy.TypeError):
        test.typecheck()

# @std.fn
# def mk_unit():
#     """This is a docstring."""
#     {} >> std.unit
#     return ()

# TODO: test unit intro
# TODO: test return
# TODO: test code generation
