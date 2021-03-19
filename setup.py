#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages
import teimlib.__init__

setup(
    name='teimed',
    version=teimlib.__init__.__version__,
    py_modules=['teiminfo','ualog'],
    packages=find_packages(),
    #packages=['teimed'],
    scripts=[
        "checkover.py",
        "checktxt.py",
        "maketeimxmlprj.py",
        "maketeimtextprj.py",
        "prjmgr.py",
        "savetext.py",
        "teimedit.py",
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
