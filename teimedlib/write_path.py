#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ast import If
import stat
import os
import pathlib as pth

# crea tutte le dir e scrive il file
def write_path_file(path_str, text, w_a='w'):
    path = pth.Path(path_str)
    ps = path.parent.parts

    if len(ps)>1:
        dir_str = ps[0]
        path_dir = pth.Path(dir_str)
        path_dir.mkdir(exist_ok=True)
        chmod(dir_str)
        for p in ps[1:]:
            dir_str = f"{dir_str}/{p}"
            path_dir = pth.Path(dir_str)
            path_dir.mkdir(exist_ok=True)
            chmod(dir_str)

    open(path_str, w_a).write(text)
    chmod(path_str)


def make_dir_of_file(path):
    dirname = os.path.dirname(path)
    if dirname.strip() == '':
        return
    make_dir(dirname)


def make_dir(dirname):
    try:
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
            os.chmod(dirname, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)
            return True
        else:
            return False
    except Exception as e:
        s = str(e)
        msg = f"ERROR make_dir(){os.linesep}{s}"
        raise Exception(msg)


def chmod(path):
    os.chmod(path, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)
