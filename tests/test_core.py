"""Core tests.

To run:
  $ py.test test_core.py
"""
import pytest
import ast

import typy
from typy.std import component, unit

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

def test_unit_intro():
    @component
    def c():
        x [: unit] = ()

    assert isinstance(c, typy.Component)
    assert isinstance(c._members, tuple)
    assert len(c._members) == 1
    assert isinstance(c._members[0], typy.ValueMember)
    assert c._members[0].name == "x"
    assert isinstance(c._members[0].ty_ann, typy.NameTyExpr)
    assert isinstance(c._members[0].ty_ann.name_ast, ast.Name)
    assert c._members[0].ty_ann.id == "unit"
    assert isinstance(c._members[0].expr, ast.Tuple)

