#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import stat

BIN = "teimed_flori/bin"

def path_bin():
    pwd=os.getcwd()
    sp=pwd.partition("/tei/")
    path_tei=f"{sp[0]}{sp[1]}"
    path_flori=os.path.join(path_tei,BIN)
    return path_flori

def write_cmd(lst):
    name=lst[0]
    cmd = " ".join(lst[1:])
    path = os.path.join(path_bin(), name)
    print(name)
    print(cmd)
    with open(path,"w+") as f: 
        f.write(cmd)
    os.chmod(path, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)


if len(sys.argv)>1:
    write_cmd(sys.argv[1:])