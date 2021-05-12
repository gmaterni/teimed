#!/usr/bin/env python3
# coding: utf-8
import os
import pathlib as pth

def cwd():
    pwd = pth.Path().cwd()
    return pwd

def home():
    home = pth.Path().home()
    return home

# path (str)file usato per memorizzrae 
# la configurazione temporanea
def path_rc(rc):
    home = pth.Path().home()
    prc= pth.Path().joinpath(home, rc)
    src=path2str(prc)
    return src

def path2str(path):
    try:
        if path is None:
            raise(Exception("path2str() path is None"))
        #s = f"{path}"
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

def exists(path):
    return pth.Path(path).exists()

def remove(path):
    if not pth.Path(path).exists():
        return False
    pth.Path(path).unlink()
    return True
 
def join(path0, path1):
    return pth.Path().joinpath(path0, path1)


def relative(path0, path1):
    if path0 is None:
        return cwd if path1 is None else path1
    elif path1 is None :
        return cwd if path0 is None else path
    else:
        return pth.Path(path0).relative_to(path1)

def pathlist2strlist(path_lst):
    path_lst = [] if path_lst is None else path_lst
    lst = [path2str(x) for x in path_lst]
    return lst

def strlist2pathlist(st_lst):
    st_lst = [] if st_lst is None else st_lst
    lst = [str2path(x) for x in st_lst]
    return lst

def rlist_path(path, match):
    lst=[x for x in path.rglob(match)]
    return lst

def list_path(path, match=None):
    if match is None:
        lst=[x for x in path.iterdir()]
    else:
        lst=[x for x in path.glob(match)]
    return lst

# sosttiuisce path.name con path1.name
# se s0,s1 != '' name viene modificato
def subst_path_name(path0, path1, s0='', s1=''):
    try:
        name = path1.name
        if s1 != '':
            name = name.replace(s0, s1)
        path = path0.with_nname(name)
        return path
    except Exception as e:
        msg = f"ERROR subs_path_name {os.linesep}{e}"
        raise(Exception(msg))

# ritorna una path con path.name modificato da replace s0=>s1
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
