#!/usr/bin/env python3
# coding: utf-8
from pdb import set_trace
import os
import pathlib as pth

def cwd():
    pwd = pth.Path().cwd()
    return pwd

def home():
    home = pth.Path().home()
    return home

def path2str(path):
    try:
        if path is None:
            raise(Exception("path2str() path is None"))
        # s = f"{path}"
        s=path.as_posix()
        return s.strip()
    except Exception as e:
        raise(Exception(f"ERROR path2str() {os.linesep}{e}"))

def str2path(path_str):
    try:
        path_str="" if path_str is None else path_str
        if isinstance(path_str, str):
            path = pth.Path(path_str)
            return path
        else:
            return path_str
    except Exception as e:
        raise(Exception(f"ERROR str2path() {os.linesep}{e}"))

def exists(path_s):
    return pth.Path(path_s).exists()

def remove(path_s):    
    if not pth.Path(path_s).exists():
        return False
    pth.Path(path_s).unlink()
    return True

def join(path0, path1):
    return pth.Path().joinpath(path0, path1)

def relative(path0, path1):
    print("relative obsolete")
    input("ERROR pathutils.py ")
    input("!!")
    # if path0 is None:
    #     return cwd if path1 is None else path1
    # elif path1 is None :
    #     return cwd if path0 is None else path0
    # else:
    #     return pth.Path(path0).relative_to(path1)
    return None

def relative_to(path,to_path):
    """
    dir di path relativa a to_path
    restituise una str
    """    
    if isinstance(path, str):
        path = pth.Path(path)
    if isinstance(to_path, str):
        to_path = pth.Path(to_path)
    p0=path2str(path.resolve())
    p1=path2str(to_path.resolve())
    pr=p0.replace(f'{p1}/','')
    return pr


def pathlist2strlist(path_lst):
    path_lst = [] if path_lst is None else path_lst
    lst = [path2str(x) for x in path_lst]
    return lst

def strlist2pathlist(path_s_lst):
    path_s_lst = [] if path_s_lst is None else path_s_lst
    lst = [str2path(x) for x in path_s_lst]
    return lst

# lista ricorsiva
def rlist_path(path, match):
    lst=[x for x in path.rglob(match)]
    return lst

def list_path(path, match=None):
    if match is None:
        lst=[x for x in path.iterdir()]
    else:
        lst=[x for x in path.glob(match)]
    return lst

# ritorna una path con path.name modificato 
# da replace s0=>s1
def update_path_name(path, s0, s1):
    try:
        name = path.name.replace(s0, s1)
        path_trg = path.with_name(name)
        return path_trg
    except Exception as e:
        msg = f"ERROR update_path_name {os.linesep}{e}"
        raise(Exception(msg))

def make_dir(path_dir, mode=0o777):
    if path2str(path_dir) == '':
        return
    if not path_dir.exists():
        path_dir.mkdir(mode=mode)

def chmod(path, mode=0o777):
    if not path.exists():
        raise(Exception(f"{path} Not Exists"))
    try:
        #os.chmod(path, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)
        path.chmod(mode=mode)
    except Exception as e:
        msg = f"ERROR chmod() {os.linesep}{e}"
        raise(Exception(msg))
