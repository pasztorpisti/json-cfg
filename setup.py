# -*- coding: utf-8 -*-

import os
import re
import codecs
try:
    from setuptools import setup
    have_setuptools = True
except ImportError:
    from distutils.core import setup
    have_setuptools = False


script_dir = os.path.abspath(os.path.dirname(__file__))


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


# Get the long description from the relevant file
# with open('DESCRIPTION.rst', encoding='utf-8') as f:
#     long_description = f.read()


extra_setup_params = {}
if have_setuptools:
    extra_setup_params['test_suite'] = 'tests'
    extra_setup_params['tests_require'] = ['mock']


setup(
    name='json-cfg',
    version=find_version('jsoncfg', '__init__.py'),
    description='JSON config file parser with extended syntax (e.g.: comments), '
                'line/column numbers and other extras.',
    # long_description=long_description,

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
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords='json configuration jsonconfiguration json-configuration comment',
    packages=['jsoncfg', 'tests'],

    **extra_setup_params
)
