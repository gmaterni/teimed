#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages

setup(
    name='teimed',
    version="0.2.4",
    py_modules=['teiminfo',
                'prjmgr',
                'teimprjxml',
                'teimprjtext',
                'teimprjsave'
                ],
    install_requires=['lxml'],
    include_package_data=True,
    packages=find_packages(),
    # packages=['teimcfg','teimedlib'],
    # package_data={'teimed':['teimcfg/*.*']},
    scripts=[
        "teixml2txt.py",
        "checkover.py",
        "checktxt.py",
        "teimprjxml.py",
        "teimprjtext.py",
        "prjmgr.py",
        "teimprjsave.py",
        "teimedit.py",
        "teimnote.py",
        "teimover.py",
        "teimsetid.py",
        "teimxmlformat.py",
        "teimxml.py"
    ],
    author="Marta Materni",
    author_email="marta.materni@gmail.com",
    description="Tools per TEI",
    long_description=open('README.rst').read(),
    url='https://github.com/digiflor/',
    license="new BSD License",
    classifiers=['Development Status :: 1 - Planing',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: Italiano',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python 3.6.',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities'],
    entry_points={
        'console_scripts': [
            'teiminfo = teiminfo:list_modules',
        ],
    },
)
