from distutils.core import setup

setup(
	name='typy',
	version='0.1.0',
	author='Cyrus Omar',
	author_email='cyrus.omar@gmail.com',
	packages=('typy', 'typy.fp', 'typy.util'),
	py_modules=('typy', 'typy.fp', 'typy.util'),
	url='http://www.github.com/cyrus-/typy',
	license='MIT',
	description='A programmable static type system as a Python library.',
	long_description='',
	install_requires=('astunparse',)
)
