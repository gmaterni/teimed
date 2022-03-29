#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import teimedlib.pathutils as ptu

"""
scrittura comandi

uash.py dir1/dir2/cmd.py ls .
scrive in cmd.py ls .

"""
def write_cmd(lst):
    name = lst[0]
    cmd = " ".join(lst[1:])
    # path = os.path.join(path_bin(), name)
    print(name)
    print(cmd)
    ptu.make_dir_of_file(name)
    with open(name,"w") as f:
        f.write(cmd)


if len(sys.argv) > 1:
    write_cmd(sys.argv[1:])
