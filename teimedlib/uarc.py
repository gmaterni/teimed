#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import pathlib as pth
from pdb import set_trace

__date__ = "30-08-2021"
__version__ = "0.1.2"
__author__ = "Marta Materni"


class UaRc(object):
    """
    gestisce il file '.teimeditrc' per teimedit.py
    memorizza posizione delle finestre ad ogni sesseione

    """

    def __init__(self, rc_name=".uarc"):
        home = pth.Path().home()
        self.path_rc_p = pth.Path().joinpath(home, rc_name)
        self.rc = {}

    def is_empty(self):
        if not self.path_rc_p.exists():
            return True
        self.load()
        return (self.rc == {})

    def remove(self):
        if self.path_rc_p.exists():
            self.path_rc_p.unlink()

    def set(self, k, v):
        self.rc[k] = v
        return self

    def get_val(self, k):
        return self.rc.get(k, None)

    def get(self, k, v):
        """
        # x=rc.get('a',v) 
        se 'a' NON esiste 
        setta rc e ritorna v
        altrimenti 
        ritorna val
        """
        val = self.rc.get(k, None)
        if val is None:
            self.rc[k] = v
            return v
        else:
            return val

    def upd(self, k, v, default):
        """
        se val is None
          se v is None
            setta v=default
          setta rc e ritorna v (o defaut)
       altrimenti
             ritorna val
        """
        val = self.rc.get(k, None)
        if val is None:
            if v is None:
                v = default
            self.rc[k] = v
            return v
        else:
            return val

    # def xupd(self,k,v):
    #     """
    #     # x=rc.upd('a',v)
    #     se a NON esiste OR (v!=None AND  v!='' )
    #     setta rc e ritorna v
    #     altrimenti
    #     ritorna val
    #     """
    #     val=self.rc.get(k,None)
    #     if val is None or (v is not None and len(v)> 0):
    #         self.rc[k]=v
    #         return v
    #     else:
    #         return val

    def prn(self, msg=''):
        print("")
        print(msg)
        for k, v in self.rc.items():
            print(f'{k}:{v}')

    def save(self):
        try:
            s = json.dumps(self.rc, indent=2)
            self.path_rc_p.write_text(s)
            self.path_rc_p.chmod(mode=0o666)
        except Exception as e:
            raise(Exception(f"ERROR save_rc() {os.linesep}{e}"))

    def load(self):
        try:
            if not self.path_rc_p.exists():
                self.save()
            s = self.path_rc_p.read_text()
            self.rc = json.loads(s)
        except Exception as e:
            raise(Exception(f"ERROR load_rc() {os.linesep}{e}"))
