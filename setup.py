from distutils.core import setup

import os1

setup(
    name='ouster-os1',
    version=os1.__version__,
    description=os1.__doc__,
    author=os1.__author__,
    url='https://github.com/rsiemens/ouster-python/',
    packages=['os1'],
)
