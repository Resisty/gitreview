#!/usr/bin/env python
''' Module for setting up gitreview CLI tool(s)
'''
#pylint: disable=unused-import
from setuptools import setup, find_packages

setup(
    name='gitreview',
    version='0.36',
    entry_points={
        'console_scripts': [
            'gitreview=gitreview.command_line:main',
            'gitreview-provide-format=gitreview.command_line:provide_format'
        ],
    },
    packages=[
        'gitreview',
        'gitreview.lib'
    ],
    install_requires=[
        'pyyaml',
        'requests'
    ]
)
