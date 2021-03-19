#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import stat
import pathlib as pt

class  RmLog(object):

    def __init__(self):
        self.pwd=pt.Path.cwd()
        
    def list_file_log(self):
        lst=self.pwd.rglob("*.log")
        f_lst=[]
        for f in lst:
            f_lst.append(f)
        return f_lst    

    def list_dir_log(self):
        p_lst=self.pwd.rglob("log/")
        return p_lst
            
    def list_file_of_dir_log(self):
        d_lst=self.list_dir_log()
        f_lst=[]
        for d in d_lst:
            d_f_lst=d.rglob("*.*")
            for f in d_f_lst:
                f_lst.append(f)
        return f_lst

    def list_log(self):
        f_lst=self.list_file_log()
        d_f_lst=self.list_file_of_dir_log()
        log_lst=[]
        for x in f_lst:
            log_lst.append(x)
        for x in d_f_lst:
            log_lst.append(x)
        lst=list(set(log_lst))
        lst=sorted(lst)
        return lst

    def remove_log(self):
        log_lst=self.list_log()
        print(len(log_lst))
        for f in log_lst:
            print(f)
            f.unlink()
            

rml=RmLog()
rml.remove_log()
