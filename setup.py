#!/usr/bin/env python

from setuptools import setup, find_packages

__AUTHOR__ = 'QuantStack dev team'

setup(
    name='py2vega',
    version='0.4.0',
    description='A Python to Vega-expression transpiler.',
    author=__AUTHOR__,
    maintainer=__AUTHOR__,
    url='https://github.com/QuantStack/py2vega',
    license='BSD 3-Clause',
    keywords='python vega vega-expression',
    packages=find_packages(exclude=['test']),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[],
    extras_require={
        'testing': ['pytest', 'flake8'],
    },
    platforms=['any'],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
