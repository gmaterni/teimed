#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import teimedlib.pathutils as pthu
import json
import os


class UaRc(object):

    def __init__(self,name_rc=".uarc"):
        self.path_rc = pthu.path_rc(name_rc)
        self.rc={}

    def remove(self):
        pthu.remove(self.path_rc)

    def set(self,k,v):
        self.rc[k]=v
        return self

    # x=get('a',v) 
    # se a NON esiste 
    #    setta rc e ritorna v
    # altrimenti 
    #   ritorna val
    def get(self,k,v):
        val=self.rc.get(k,None)
        if val is None:
            self.rc[k]=v
            return v
        else:
            return val

    # se a NON esiste OR (v!=None AND  v!=''()
    #    setta rc e ritorna v
    # altrimenti 
    #   ritorna val
    def upd(self,k,v):
        val=self.rc.get(k,None)
        if val is None or (v is not None and len(v)> 0):
            self.rc[k]=v
            return v
        else:
            return val


    def prn(self,msg=''):
        print("")
        print(msg)
        for k,v in self.rc.items():
            print(f'{k}:{v}')

    def save(self):
        try:
            s = json.dumps(self.rc, indent=2)
            with open(self.path_rc, "w+")as f:
                f.write(s)
            os.chmod(self.path_rc, 0o666)
        except Exception as e:
            raise(Exception(f"ERROR write_rc() {os.linesep}{e}"))

    def load(self):
        if not pthu.exists(self.path_rc):
            self.save()
        try:
            with open(self.path_rc, "r") as f:
                txt = f.read()
            self.rc = json.loads(txt)
        except Exception as e:
            raise(Exception(f"ERROR read_rc() {os.linesep}{e}"))

