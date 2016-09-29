"""Core tests.

To run:
  $ py.test test_core.py
"""
import pytest
import ast

import typy
from typy.std import component, unit, record, string, py

def test_unit_intro():
    @component
    def c():
        x [: unit] = ()

    assert isinstance(c, typy.Component)

    # parsing
    assert isinstance(c._members, tuple)
    assert len(c._members) == 1
    assert isinstance(c._members[0], typy.ValueMember)
    assert c._members[0].name.id == "x"
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

def test_gpce_paper_example_1():
    # simplified to use string rather than string_in for now
    @component
    def Listing1():
        Account [: type] = record[
            name        : string,
            account_num : string,
            memo        : py
        ]

        test_acct [: Account] = {
            name: "Harry Q. Bovik",
            account_num: "00-12345678",
            memo: { }
        }

    c = Listing1
    assert isinstance(c, typy.Component)

    # parsing
    assert isinstance(c._members, tuple)
    assert len(c._members) == 2
    
    assert isinstance(c._members[0], typy.TypeMember)
    assert c._members[0].name.id == "Account"
    assert isinstance(c._members[0].ucon, typy.UCanonicalTy)
    assert isinstance(c._members[0].ucon.fragment_ast, ast.Name)
    assert isinstance(c._members[0].ucon.idx_ast, ast.ExtSlice)

    assert isinstance(c._members[1], typy.ValueMember)
    assert c._members[1].name.id == "test_acct"
    assert isinstance(c._members[1].uty, typy.UName)
    assert c._members[1].uty.id == "Account"
    assert isinstance(c._members[1].expr, ast.Dict)

    # checking
    assert isinstance(c._members[0].ty, typy.CanonicalTy)
    assert c._members[0].ty.fragment == record
    assert isinstance(c._members[0].ty.idx, dict)
    assert c._members[0].ty.idx["name"].fragment == string
    assert c._members[0].ty.idx["account_num"].fragment == string
    assert c._members[0].ty.idx["memo"].fragment == py
    
    assert isinstance(c._members[1].ty, typy.ConVar)
    assert c._members[1].ty.name_ast.id == "Account"

    # translation and evaluation
    assert c._members[1].value == ("00-12345678", { }, "Harry Q. Bovik")

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

