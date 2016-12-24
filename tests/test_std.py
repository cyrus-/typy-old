"""Standard library tests.

To run:
  $ py.test test_std.py
"""
import pytest
import ast

import typy
from typy.std import component, unit, record, string, py, fn, finsum, tpl

# 
# unit
# 

def test_unit_intro():
    @component
    def c():
        x [: typy.std.unit] = ()

    assert isinstance(c, typy.Component)

    # checking 
    assert isinstance(c._members[0].ty, typy._ty_exprs.CanonicalTy)
    assert c._members[0].ty.fragment == unit
    assert c._members[0].ty.idx == ()

    # translation
    assert c

    # evaluation
    assert c._module.x == ()

