#!/usr/bin/env python3
# coding: utf-8

import os

__date__ = "13-07-2021"
__version__ = "0.5.3"
__author__ = "Marta Materni"


class Log(object):
    """
        Log("w")            modalità wrie
        Log("a")            modlaità append

        self.out_liv > 0    print attivato globalmente
        self.out_liv  <1    disattivato
        
        prn()/prn(1)          attivato localmente anche  
                            se distattivato globalmente

        prn(0)               disattivato localmente
                            ma resta valido il settaggio globale
    """

    def __init__(self, append_write='w'):
        self.path_log = ""
        self.dirname = ""
        self.append_write = append_write
        self.out_liv = 0
        self.used = False
        self.msg = ''

    def set_liv(self, liv):
        self.out_liv = liv
        return self

    # setta path e liv, NON apre fisicamente il file
    def open(self, path_log, liv):
        self.path_log = path_log
        self.dirname = os.path.dirname(path_log).strip()
        self.out_liv = int(liv)
        # rimuove path_log se in modalità 'w' esiste
        if self.append_write=='w':
            if os.path.exists(self.path_log):
                os.remove(self.path_log)
        return self

    # apre fisicamente il file e crea la dir se non esiste
    def open_file(self):
        if self.dirname != "":
            if not os.path.exists(self.path_log):
                if not os.path.isdir(self.dirname):
                    os.mkdir(self.dirname)
                    os.chmod(self.dirname, 0o777)
        f = open(self.path_log, self.append_write)
        f.close()
        os.chmod(self.path_log, 0o777)
        self.used = True

    def prn(self, liv=1):
        if self.out_liv == 0 and liv > 0:
            print(self.msg)
        return self

    def log(self, *args):
        if self.out_liv < 0:
            return self
        if not self.used:
            self.open_file()
        ls = ["None" if x is None else str(x) for x in args]
        s = f"{os.linesep}".join(ls)
        f = open(self.path_log, "a")
        f.write(s)
        f.write(os.linesep)
        f.close()
        self.msg = s
        if self.out_liv > 0:
            print(s)
        return self
