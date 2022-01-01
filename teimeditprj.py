#!/usr/bin/env python3
# coding: utf-8
import sys
import pathlib as pth
import shutil
import os

"""
copia /u/teimm/teimed/teimcfg in una dir passata come args
"""
def cp_r(dir_dst=None):
    if not dir_dst:
        return
    teimcfg = 'teimcfg'
    pwd=os.getcwd()
    teimcfg_src=os.path.join(pwd,teimcfg)
    if not os.path.exists(teimcfg_src):
        print(f'{teimcfg_src} Not Found')
        return
    if os.path.exists(dir_dst):
        print(f'{dir_dst} exists')
        return
    teimcfg_dst=os.path.join(dir_dst,teimcfg)
    shutil.copytree(teimcfg_src,teimcfg_dst)
    pth.Path(dir_dst).chmod(0o777)
    for f in pth.Path(dir_dst).rglob("*.*"):
        f.chmod(0o777)

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("dir project")
        sys.exit()
    path = sys.argv[1]  
    cp_r(path)
