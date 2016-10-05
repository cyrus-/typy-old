"""Standard library tests.

To run:
  $ py.test test_std.py
"""
import pytest
import ast

import typy
from typy.std import component, unit, record, string, py, fn, finsum, tpl

def test_unit_intro():
    @component
    def c():
        x [: unit] = ()

    assert isinstance(c, typy.Component)

    # parsing
    assert isinstance(c._members, tuple)
    assert len(c._members) == 1
    assert isinstance(c._members[0], typy.ValueMember)
    assert c._members[0].id == "x"
    assert isinstance(c._members[0].uty, typy.UName)
    assert isinstance(c._members[0].uty.name_ast, ast.Name)
    assert c._members[0].uty.id == "unit"
    assert isinstance(c._members[0].tree, ast.Assign)
    
    # checking 
    assert isinstance(c._members[0].ty, typy.CanonicalTy)
    assert c._members[0].ty.fragment == unit
    assert c._members[0].ty.idx == ()

    # evaluation
    assert c._module.x == ()

def test_component_args():
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c(x):
            pass
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c(*x):
            pass
    with pytest.raises(typy.ComponentFormationError):
        @component
        def c(**x):
            pass

