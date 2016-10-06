"typy errors"

#
# Errors
#

class TypyError(Exception):
    """Base class for typy errors."""
    pass

class InternalError(TypyError):
    """Raised when an internal invariant has been violated."""
    def __init__(self, message):
        TypyError.__init__(self, message)

class UsageError(TypyError):
    """Raised by typy to indicate incorrect usage of the typy API."""
    def __init__(self, message):
        TypyError.__init__(self, message)

class TypeFormationError(TypyError):
    """Raised by typy to indicate that a type expression is malformed."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

class TyError(TypyError):
    """Raised by fragments to indicate a type error."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

class TyMismatchError(TyError):
    """Raised when the synthesized type is inconsistent with the 
    type provided for analysis."""
    def __init__(self, expected, got, tree):
        TyError.__init__(self, 
            "Type mistatch.\n"
            "Expected: " + str(expected) + "\n"
            "Got: " + str(got) + "\n", tree)
        self.expected = expected
        self.got = got

class KindError(TypyError):
    """Raised by typy or fragments to indicate a kind error."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

class TypeValidationError(KindError):
    """Raised by fragments to indicate that a type index value
    cannot be computed."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

class ComponentFormationError(TypyError):
    """Raised to indicate that a component is malformed."""
    def __init__(self, message, tree):
        TypyError.__init__(self, message)
        self.tree = tree

class FragmentError(TypyError):
    """Raised to indicate a problem with a fragment definition."""
    def __init__(self, message, fragment):
        TypyError.__init__(self, message)
        self.fragment = fragment

__all__ = ('InternalError', 'UsageError', 'TypeFormationError', 
           'TyError', 'TyMismatchError', 'KindError', 
           'TypeValidationError', 'ComponentFormationError', 
           'FragmentError')

