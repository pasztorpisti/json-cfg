# -*- coding: utf-8 -*-

from distutils.core import setup
import os
import re
import codecs

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
#with open('DESCRIPTION.rst', encoding='utf-8') as f:
#    long_description = f.read()

setup(
    name='jsonconfig',
    version=find_version('jsonconfig', '__init__.py'),
    description='JSON config file parser',
    #long_description=long_description,

    url='https://github.com/pasztorpisti/jsonconfig',

    author='István Pásztor',
    author_email='pasztorpisti@gmail.com',

    license='MIT',

    classifiers=[
        'License :: OSI Approved :: MIT License',

        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='json configuration jsonconfiguration json-configuration comment',
    packages=['jsonconfig', 'tests'],
)
