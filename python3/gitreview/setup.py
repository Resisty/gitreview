#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='gitreview',
    version='0.24',
    entry_points={
        'console_scripts': [
            'gitreview=gitreview.command_line:main'
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
