#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from pdb import set_trace
import sys
import os
import pathlib as pth

__date__ = "09-08-2021"
__version__ = "0.1.1"
__author__ = "Marta Materni"


class FindPrj(object):
    """
    Programma di utility
    Cerca il primo file __prj__ contenuto in un progetto
    a partire dalla dir dalla quale è lanciato.
    Il nome del progetto è passato per psoizione.

    es.
    teimprjfind.py flori_xml

    flori_xml
    /u/teim/TEST/flori_xml/__prj__
    
    """    
    
    def __init__(self):
        self._run_dir = pth.Path().cwd()
        self._prj_names=[]
        self._prj_dirs=[]
        self.prj_name=''

    @property
    def prj_names(self):
        return self._prj_names

    @property
    def prj_dirs(self):
        return self._prj_dirs

    def read_prj_name(self, prj_path):
        with open(prj_path, "r") as f:
            prj_name = f.read().strip()
        return prj_name
    
    def find_prj(self,name=''):
        self.prj_name=name
        lst = self._run_dir.rglob("__prj__")
        prj_paths = [pid for pid in lst]
        if prj_paths == []:
            return [], []
        self._prj_names = []
        self._prj_dirs=[]
        for path in prj_paths:
            prj_name = self.read_prj_name(path)
            if name=='' or name==prj_name:
                self._prj_names.append(prj_name)
                self._prj_dirs.append(path)
        return self
        
    def prn(self):
        s=f"run dir:{self._run_dir}"
        print(s)
        if len(self._prj_names)==0:
            print("")
            print(f"prj {self.prj_name} Not Found.")
            return
        for i,name in enumerate(self._prj_names):
            print("")
            dir=self._prj_dirs[i]
            print(f"{name}")
            print(f"{dir}")

if __name__ == "__main__":
    prj_name = ""
    le = len(sys.argv)
    if le == 2:
        prj_name = sys.argv[1]
    fp=FindPrj()
    fp.find_prj(prj_name)
    fp.prn()
    