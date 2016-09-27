"""Core tests.

To run:
  $ py.test test_core.py
"""
import pytest
import ast

import typy
from typy.std import component, unit

def test_unit_intro():
    @component
    def c():
        x [: unit] = ()

    assert isinstance(c, typy.Component)

    # parsing
    assert isinstance(c._members, tuple)
    assert len(c._members) == 1
    assert isinstance(c._members[0], typy.ValueMember)
    assert c._members[0].name == "x"
    assert isinstance(c._members[0].uty, typy.UName)
    assert isinstance(c._members[0].uty.name_ast, ast.Name)
    assert c._members[0].uty.id == "unit"
    assert isinstance(c._members[0].expr, ast.Tuple)
    assert len(c._exports) == 1
    assert c._exports['x'] == c._members[0]
    
    # checking 
    assert isinstance(c._members[0].ty, typy.CanonicalTy)
    assert c._members[0].ty.fragment == unit
    assert c._members[0].ty.idx == ()

    # translation
    assert isinstance(c._members[0].expr.translation, ast.Tuple)
    assert len(c._members[0].expr.translation.elts) == 0

    # evaluation
    assert c._members[0].value == ()

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

