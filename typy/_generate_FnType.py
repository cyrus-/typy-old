check_methods = []
stmt_forms = (
  'FunctionDef', 
  'ClassDef', 
  'Return', 
  'Delete',
  'Assign',
  'AugAssign',
  'Print',
  'For',
  'While',
  'If',
  'With',
  'Raise',
  'TryExcept',
  'TryFinally',
  'Assert',
  'Import',
  'ImportFrom',
  'Exec',
  'Global',
  'Expr',
  'Pass',
  'Break',
  'Continue')
for stmt_form in stmt_forms:
    check_methods.append('''@classmethod
def check_{0}(cls, ctx, tree):
  raise NotSupportedError(cls, "class method", "check_{0}", tree)
'''.format(stmt_form))

print "################################################################################"
print "# The following stubs are pasted from the result of running _generate_FnType.py."
print "################################################################################"
print ""
print str.join('\n', check_methods)
print "################################################################################"
print "# End autogenerated section"
print "################################################################################"
