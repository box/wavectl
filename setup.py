#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
from setuptools import setup, find_packages
import os

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.6',
    'Operating System :: OS Independent',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

install_requires = [
    "argcomplete",
    "future",
    "GitPython",
    "python-dateutil",
    "six",
    "termcolor",
    "wavefront-api-client>=2.3.1"]

test_require = [
    "mock",
    "recommonmark",
    "Sphinx",
    "sphinxcontrib-programoutput",
]

base_dir = os.path.dirname(__file__)

setup(
    name="wavectl",
    version="0.3.0",
    description="Command Line Client For Wavefront",
    long_description=open(os.path.join(base_dir, 'README.md'),).read(),
    long_description_content_type='text/markdown',
    url="https://github.com/box/wavectl",
    author="Box",
    author_email="oss@box.com",
    keywords=["Wavefront", "Wavefront Public API", "wavectl", "cli"],
    packages=find_packages(),
    install_requires=install_requires,
    test_require=test_require,
    entry_points={
        'console_scripts': [
            'wavectl = wavectl.main:main',
        ]
    },
    classifiers=CLASSIFIERS,
    license='Apache Software License, Version 2.0, http://www.apache.org/licenses/LICENSE-2.0',
)
