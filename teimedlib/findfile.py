#!/usr/bin/env python3
# coding: utf-8

import teimedlib.pathutils as ptu

#ritorna una lista di path selezionate da math 
# a partire da initialdir
def find_path_lst(initialdir, match):
    try:
        if initialdir is None:
            initialdir = ptu.str2path(".")
        elif isinstance(initialdir,str):
            initialdir = ptu.str2path(initialdir)
        path_lst = []
        for x in initialdir.rglob(match):
            path_lst.append(x)
        return path_lst
    except Exception as e:
        raise(e)

def find_dir_lst(initialdir, match):
    lst=find_path_lst(initialdir,match)
    return[x for x in lst if x.is_dir()]

def find_file_lst(initialdir, match):
    lst=find_path_lst(initialdir,match)
    return[x for x in lst if x.is_file()]




