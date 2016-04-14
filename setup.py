# -*- coding: utf-8 -*-

import os
import re
import codecs
from setuptools import setup, find_packages


script_dir = os.path.dirname(os.path.abspath(__file__))


def find_version(*path):
    with codecs.open(os.path.join(script_dir, *path), 'r', 'latin1') as f:
        contents = f.read()

    # The version line must have the form
    # version_info = (X, Y, Z)
    m = re.search(
        r'^version_info\s*=\s*\(\s*(?P<v0>\d+)\s*,\s*(?P<v1>\d+)\s*,\s*(?P<v2>\d+)\s*\)\s*$',
        contents,
        re.MULTILINE,
    )
    if m:
        return '%s.%s.%s' % (m.group('v0'), m.group('v1'), m.group('v2'))
    raise RuntimeError('Unable to determine package version.')


with codecs.open(os.path.join(script_dir, 'README.rst'), 'r', 'utf8') as f:
    long_description = f.read()


setup(
    name='json-cfg',
    version=find_version('src', 'jsoncfg', '__init__.py'),
    description='JSON config file parser with extended syntax (e.g.: comments), '
                'line/column numbers in error messages, etc...',
    keywords='json config file parser configuration comment',
    long_description=long_description,

    url='https://github.com/pasztorpisti/json-cfg',

    author='István Pásztor',
    author_email='pasztorpisti@gmail.com',

    license='MIT',

    classifiers=[
        'License :: OSI Approved :: MIT License',

        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=['kwonly-args>=1.0.7'],
    packages=find_packages('src'),
    package_dir={'': 'src'},

    test_suite='tests',
    tests_require=['mock'],
)
