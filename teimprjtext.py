#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pdb import set_trace
from prjmgr import PrjMgr
import pprint
import json
import os


__date__ = "27-07-2021"
__version__ = "1.2.1"
__author__ = "Marta Materni"


def pp(data, wd=60):
    return pprint.pformat(data, indent=2, width=wd)


class TeimPrjText(object):
    """
    Crea le direttory per i file di testo che sono stati aggiunti
    al witness indicato
    teimprjtext.py <project_name> <witness>
    Se si esegue lo script  nella dir del progetto
    teimprjtext.py <witness>
    gli argomenti soo passati per psoizione,
    es.
    teimprjtext.py <project_name> <witness>

    teimprjtext.py <witness>

    """

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
        remove_prj_witness = {
            "remove_dir": [
                {
                    "dir": "work/prj_witness",
                    "pattern": "*.json"
                }
            ]
        }
        self.prj_exec(remove_prj_witness, work, witness)
        #############
        execute_make_prj = {
            "log": "1",
            "exe_dir": {
                "dir": "work/witness",
                "pattern": "*.txt",
                "par_subst": ".txt|",
                "par_name": "$F",
                "exe_file": [
                    [
                        "teimprjxml.py work witness $F"
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
                print(f"witness: {witness} Not Found.")
                return
            dirname = os.path.dirname(self.pwd)
            os.chdir(dirname)
            self.make(work, witness)
            os.chdir(self.pwd)
            return
        # dir work non trovata
        if not os.path.isdir(work):
            print(f"work: {work} Not Found")
            return

        # nela dir parent di work
        path = os.path.join(work, witness)
        if not os.path.isdir(path):
            print(f"witness: {witness} Not Found.")
            return
        self.make(work, witness)

    def make_witness(self, witness):
        if not os.path.isdir(witness):
            print(f"witness:{witness} Not Found.")
            return
        work = os.path.basename(self.pwd)
        dirname = os.path.dirname(self.pwd)
        os.chdir(dirname)
        self.make(work, witness)
        os.chdir(self.pwd)

# [work,witness]
# [witness]


def do_main(work, witness):
    mk = TeimPrjText()
    mk.make_work_witness(work, witness)


def do_main_witness(witness):
    mk = TeimPrjText()
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
        s = """
Crea le direttory per i text che sono stati aggiunti
al witness indicato

teimprjtext.py <project_name> <witness>

Se si esegue lo script  nella dir del progetto:
teimprjtext.py <witness>
        """
        print(s)
        sys.exit(0)
