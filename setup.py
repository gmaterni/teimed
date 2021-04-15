#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages
import teimedlib.__init__

setup(
    name='teimed',
    version=teimedlib.__init__.__version__,
    py_modules=['teiminfo',
                'prjmgr'
                'teimprjxmlmake',
                'teimprjtextmake',
                'teimprjsave'
                ],
    packages=find_packages(),
    # packages=['teimedlib'],
    scripts=[
        "checkover.py",
        "checktxt.py",
        "teimprjxmlmake.py",
        "teimprjtextmake.py",
        "prjmgr.py",
        "teimprjsave.py",
        "teimedlibit.py",
        "teimnote.py",
        "teimover.py",
        "teimsetid.py",
        "teimxmlformat.py",
        "teimxmllint.py",
        "teimxml.py"
    ],
    author="Marta Materni",
    author_email="marta.materni@gmail.com",
    description="Tools per TEI",
    long_description=open('README.rst').read(),
    include_package_data=True,
    url='https://github.com/digiflor/',
    license="new BSD License",
    install_requires=['lxml'],
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
