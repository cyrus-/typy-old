"""py.test based tests for typy.std

To run:
  $ py.test test_std.py
"""
import typy
import typy.std as std

@std.fn
def mk_unit():
    """This is a docstring."""
    {} >> std.unit
    return ()

# TODO: test docstring
# TODO: test type annotation system
# TODO: test unit intro
# TODO: test return
# TODO: test code generation
