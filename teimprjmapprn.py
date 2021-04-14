#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import sys
from teimed.teimprjmap import TeimPrjMap

__date__ = "05-03-2021"
__version__ = "0.1.0"
__author__ = "Marta Materni"


def do_main(prj_name=""):
    tw=TeimPrjMap().main(prj_name)
    tw.prn_cmds()
    tw.prn_txt_cmds()
    tw.prn_dirs()

if __name__ == "__main__":
    prj_name = ""
    le = len(sys.argv)
    if le == 2:
        prj_name = sys.argv[1]
        if prj_name == "-h":
            print("teimfh.py <prj_name>")
            sys.exit(0)
    do_main(prj_name)
