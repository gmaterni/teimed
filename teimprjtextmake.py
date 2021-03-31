#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pdb import set_trace
from prjmgr import PrjMgr
import pprint
import json
import os


def pp(data):
    return pprint.pformat(data, indent=2, width=40)


class TeimPrjTextMake(object):

    def __init__(self):
        self.pwd = os.getcwd()

    def prj_exec(self, js, work, witness):
        pm = PrjMgr()
        s = json.dumps(js, indent=2, sort_keys=False)
        s = s.replace("work", work)
        s = s.replace("witness", witness)
        js = json.loads(s)
        # print(pp(js))
        pm.parse_json(js)

    def make(self, work, witness):
        remove_witness_log = {
            "remove_dir": [
                {
                    "dir": "work/witness",
                    "pattern": "witness.*"
                },
                {
                    "dir": "work/witness",
                    "pattern": "witness_format.*"
                },
                {
                    "dir": "work/witness",
                    "pattern": "*.log"
                },
                {
                    "dir": "work/witness/log",
                    "pattern": "*.*"
                }
            ]
        }
        self.prj_exec(remove_witness_log, work, witness)
        ###############
        remove_witness_prj = {
            "remove_dir": [
                {
                    "dir": "work/witness_prj",
                    "pattern": "*.json"
                }
            ]
        }
        self.prj_exec(remove_witness_prj, work, witness)
        #############
        execute_make_prj = {
            "log":"1",
            "exe_dir": {
                "dir": "work/witness",
                "pattern": "*.txt",
                "par_subst": ".txt|",
                "par_name": "$F",
                "exe_file": [
                    [
                        "teimprjxmlmake.py work witness $F"
                    ]
                ]
            }
        }
        self.prj_exec(execute_make_prj, work, witness)

    def make_work_witness(self, work, witness):
        basename = os.path.basename(self.pwd)
        # pwd == work NON interno alla dir
        if basename == work:
            if not os.path.isdir(witness):
                print(f"{witness} Not Found.")
                return
            dirname = os.path.dirname(self.pwd)
            os.chdir(dirname)
            self.make(work, witness)
            os.chdir(self.pwd)
            return
        # dir work non trovata
        if not os.path.isdir(work):
            print(f"{work} Not Found")
            return

        # nela dir parent di work
        path = os.path.join(work, witness)
        if not os.path.isdir(path):
            print(f"{witness} Not Found.")
            return
        self.make(work, witness)

    def make_witness(self, witness):
        if not os.path.isdir(witness):
            print(f"{witness} Not Found.")
            return
        work = os.path.basename(self.pwd)
        dirname = os.path.dirname(self.pwd)
        os.chdir(dirname)
        self.make(work, witness)
        os.chdir(self.pwd)

# [work,witness]
# [witness]

def do_main(work,witness):
    mk = TeimPrjTextMake()
    mk.make_work_witness(work, witness)

def do_main_witness(witness):
    mk = TeimPrjTextMake()
    mk.make_witness(witness)

if __name__ == "__main__":
    le = len(sys.argv)
    if le == 2:
        witness = sys.argv[1]
        do_main_witness(witness)
    elif le == 3:
        work, witness = sys.argv[1:]
        do_main(work, witness)
    else:
        s="""
Crea le direttory per i text che sono stati aggiunti
al witness indicato

teimprjtextmake.py <work> <witness>

Se si esegue lo script  nella dir di work:
teimprjtextmake.py <witness>
        """
        print(s)
        sys.exit(0)
