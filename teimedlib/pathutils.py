#!/usr/bin/env python3
# coding: utf-8

import pathlib as pth

def path2str(path):
    try:
        if path is None :
            raise(Exception("path2str(path): path is None"))
        s=f"{path}"
        return s
    except Exception as e:
        raise(e)

def str2path(s):
    try:
        if s is None:
            raise(Exception("str2path(str): string is None"))
        path=pth.Path(s)
        return path
    except Exception as e:
        raise(e)

def pathlist2strlist(path_lst):
    path_lst=[] if path_lst is None else path_lst
    lst=[path2str(x) for x in path_lst]
    return lst

def strlist2pathlist(st_lst):
    st_lst=[] if st_lst is None else st_lst
    lst=[str2path(x) for x in st_lst]
    return lst

def rlist_path(path,match):
    lst=[]
    for x in path.rglob(match):  
        lst.append(x)
    return lst

def list_path(path,match):
    lst=[]
    for x in path.glob(match):  
        lst.append(x)
    return lst


# sosttiuisce path.name con path1.name
# se s0,s1 != '' name viene modificato
def subst_path_name(path0,path1,s0='',s1=''):
    try:
        name=path1.name
        if s1!='':
            name=name.replace(s0,s1)
        path=path0.with_nname(name)
        return path
    except Exception as e:
        raise(e)

# ritorna una path con path.name modificato da replace s0=>s1
def update_path_name(path,s0,s1):
    try:
        name=path.name.replace(s0,s1)
        path_trg=path.with_nname(name)
        return path_trg
    except Exception as e:
        raise(e)
