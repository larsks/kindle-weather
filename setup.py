#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='kindle-weather',
    version='1',
    description='Server-side of kindle weather project',
    author='Lars Kellogg-Stedman',
    author_email='lars@oddbit.com',
    url='http://github.com/larsks/kindle-weather',
    install_requires=open('requirements.txt').readlines(),
    packages=find_packages(),
    package_data={'weather': ['data/*.svg']},
    entry_points = {
        'console_scripts': [
            'kindle-weather=weather.main:main',
        ],
    },
    zip_safe=False,
)
