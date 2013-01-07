#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='query-model',
    version='1.0.0',
    url='https://github.com/dmr/query-model',
    license='MIT',
    author='Daniel Rech',
    author_email='danielmrech@gmail.com',
    description='An model and different implementations for a parallel request',
    packages=[
        'query_model',
    ],
    entry_points={
        'console_scripts': [
            'predict_lookup_time = query_model.predict_lookup_time:main',
            'query_urls = query_model.query_urls:main',
        ],
    },
    zip_safe=False,
    platforms='any',
    install_requires=[
        'argparse',
        'pycurl2',
        'human_curl'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ]
)
