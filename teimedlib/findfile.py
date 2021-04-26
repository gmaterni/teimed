#!/usr/bin/env python3
# coding: utf-8

import teimedlib.pathutils as pthu

#ritorna una lista di path selezionate da math 
# a partire da initialdir
def find_match_files(initialdir, match):
    try:
        if initialdir is None:
            initialdir = pthu.str2path(".")
        elif isinstance(initialdir,str):
            initialdir = pthu.str2path(initialdir)
        path_lst = []
        for x in initialdir.rglob(match):
            path_lst.append(x)
        return path_lst
    except Exception as e:
        raise(e)
