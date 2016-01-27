"""Test utilities."""
import textwrap

import astunparse

def translation_eq(f, truth):
    """helper function for test_translate functions

    compares an AST to the string truth, which should contain Python code.
    truth is first dedented.
    """
    f.compile()
    translation = f.translation
    translation_s = astunparse.unparse(translation)
    truth_s = "\n" + textwrap.dedent(truth) + "\n"
    assert translation_s == truth_s
