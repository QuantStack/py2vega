#!/usr/bin/env python

from setuptools import setup, find_packages

__AUTHOR__ = 'QuantStack dev team'

setup(
    name='py2vega',
    version='0.6.1',
    description='A Python to Vega-expression transpiler.',
    author=__AUTHOR__,
    maintainer=__AUTHOR__,
    url='https://github.com/QuantStack/py2vega',
    license='BSD 3-Clause',
    keywords='python vega vega-expression',
    packages=find_packages(exclude=['test']),
    python_requires='>=3.10',
    install_requires=[
        'gast>=0.7.0,<0.8'
    ],
    extras_require={
        'testing': ['pytest', 'flake8'],
    },
    platforms=['any'],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
