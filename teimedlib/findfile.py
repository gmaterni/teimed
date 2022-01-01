#!/usr/bin/env python3
# coding: utf-8
from pdb import set_trace
import teimedlib.pathutils as ptu



# ritorna una lista di path selezionate da math
# in ancestor_dir
# se ancesor_dir is None lo assume come "."
def find_path_lst(path_abs_p, match):
    try:
        if path_abs_p is None:
            ancestor_p = ptu.str2path(".")
            pw=match.find('*')
            if pw > -1:
                path_s=match[0:pw]
                path_p=ptu.str2path(path_s)
                if path_p.is_absolute():
                    ancestor_p=path_p
                    match=match[pw:]
        elif isinstance(path_abs_p, str):
            ancestor_p = ptu.str2path(path_abs_p)
        path_lst = []
        for x in ancestor_p.glob(match):
            path_lst.append(x)
        return path_lst
    except Exception as e:
        raise(e)


def find_dir_lst(ancestor_dir, match):
    lst = find_path_lst(ancestor_dir, match)
    return[x for x in lst if x.is_dir()]


def find_file_lst(ancestor_dir, match):
    lst = find_path_lst(ancestor_dir, match)
    return[x for x in lst if x.is_file()]


# ritorna una lista di path selezionate da math
# a partire da ancestor_dir in modalità ricorsiva
# se ancesor_dir is None lo assume come "."
def rfind_path_lst(ancestor_dir, match):
    try:
        if ancestor_dir is None:
            ancestor_dir = ptu.str2path(".")
        elif isinstance(ancestor_dir, str):
            ancestor_dir = ptu.str2path(ancestor_dir)
        path_lst = []
        for x in ancestor_dir.rglob(match):
            path_lst.append(x)
        return path_lst
    except Exception as e:
        raise(e)


def rfind_dir_lst(ancestor_dir, match):
    lst = rfind_path_lst(ancestor_dir, match)
    return[x for x in lst if x.is_dir()]


def rfind_file_lst(ancestor_dir, match):
    lst = rfind_path_lst(ancestor_dir, match)
    return[x for x in lst if x.is_file()]
