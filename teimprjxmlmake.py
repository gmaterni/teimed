#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import stat
import pathlib as pl
from pdb import set_trace
from teimed import template_xml_prj
import json

__date__ = "32-03-2021"
__version__ = "0.1.6"
__author__ = "Marta Materni"

help = """
prjmgr.py prj/<prj.json>

witness_checkover.json
witness_checktxt.json
witness_rmovelog.json
witness_merge.json
witness_txt.json
witness_xml.json
witness.json
-------------------------------
prjmgr.py witness_prj/<prj.json>

text_checkover.json
text_checktxt.json
text_removelog.json
text_txt.json
text_lineword.json
text_note.json
text_over.json
text.json
"""

TEIM_WORK = "teim_work"
PRJ = "prj"
LOG = "log"
CFG = "cfg"
XML = "xml"

WITNESS = "witness"

WITNESS_PRJ = "witness_prj"
TEXT = "text"
TEXT_LOG = "text_log"


class TeimPrjXmlMake(object):

    def __init__(self,
                 work_name,
                 witness_name,
                 text_name):
        # dir virtuali  template
        self.tmpl_work = TEIM_WORK
        self.tmpl_prj = os.path.join(self.tmpl_work, PRJ)
        self.tmpl_witness_prj = os.path.join(self.tmpl_work, WITNESS_PRJ)
        # nomi work+witness+text
        self.work_name = work_name
        self.dir_work = work_name
        self.witness_name = witness_name
        self.witness_log_name = f"{witness_name}_log"
        self.witness_prj_name = f"{witness_name}_prj"
        self.text_name = text_name
        self.text_log_name = f"{text_name}_log"
        # dir progetto  work work/prj work/cfg work/log work/xml
        self.dir_prj = os.path.join(self.dir_work, PRJ)
        self.dir_cfg = os.path.join(self.dir_work, CFG)
        self.dir_xml = os.path.join(self.dir_work, XML)
        self.dir_log = os.path.join(self.dir_work, LOG)
        # dir witness witness/log (contenitore per singoli witness)
        self.dir_witness_name = os.path.join(self.dir_work, self.witness_name)
        self.dir_witness_log_name = os.path.join(self.dir_witness_name, LOG)
        # dir witness_prj (progetti per i singoli text)
        self.dir_witness_prj_name = os.path.join( self.dir_work, self.witness_prj_name)

    # __prj__
    def write_work_id(self):
        name_id="__prj__"
        text=f"{self.work_name}"
        path_id=os.path.join(self.dir_work,name_id)
        if os.path.exists(path_id):
            return
        with open(path_id,"w") as f:
            f.write(text)
        os.chmod(path_id, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)

    def files_of_dir(self, path, ptrn):
        p = pl.Path(path)
        fs = sorted(list(p.glob(ptrn)))
        return fs

    def make_dir(self, dirname):
        if not os.path.isdir(dirname):
            print(dirname)
            os.mkdir(dirname)
            os.chmod(dirname, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)

    ###############
    # copia dal template dei file per witness + text
    ################
    def format_trxt_prj(self, x):
        x = x.replace(WITNESS, self.witness_name)
        x = x.replace(TEXT_LOG, self.text_log_name)
        x = x.replace(TEXT, self.text_name)
        return x

    def copy_from_witness_text(self):
        for k, v in template_xml_prj.witness_prj.items():
            prj = os.path.join(self.tmpl_witness_prj, k)
            x = prj.replace(TEIM_WORK, self.work_name)
            x = x.replace(WITNESS_PRJ, self.witness_prj_name)
            x = x.replace(TEXT, self.text_name)
            prj_x = f"{x}.json"
            #
            src = json.dumps(v, indent=2)
            src_x = self.format_trxt_prj(src)
            with open(prj_x, "w") as f:
                f.write(src_x)
            os.chmod(prj_x, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)

    #######################
    # copia dal template per witness
    ######################
    def copy_from_witness(self):
        for k, v in template_xml_prj.prj.items():
            prj = os.path.join(self.tmpl_prj, k)
            x = prj.replace(TEIM_WORK, self.work_name)
            x = x.replace(WITNESS, self.witness_name)
            prj_x = f"{x}.json"
            #
            src = json.dumps(v, indent=2)
            src_x = src.replace(WITNESS, self.witness_name)
            with open(prj_x, "w") as f:
                f.write(src_x)
            os.chmod(prj_x, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)

    def print_dir(self):
        print(f">>> {self.dir_witness_name}")
        print(self.dir_work)
        print(self.dir_cfg)
        print(self.dir_prj)
        print(self.dir_xml)
        print(self.dir_log)
        print(self.dir_witness_name)
        print(self.dir_witness_log_name)
        print(self.dir_witness_prj_name)
        print("")

    def make_dirs(self):
        self.make_dir(self.dir_work)
        self.make_dir(self.dir_cfg)
        self.make_dir(self.dir_prj)
        self.make_dir(self.dir_xml)
        self.make_dir(self.dir_log)
        #
        self.make_dir(self.dir_witness_name)
        self.make_dir(self.dir_witness_log_name)
        #
        if self.text_name.strip()!="":
            self.make_dir(self.dir_witness_prj_name)
            self.copy_from_witness_text()
        self.copy_from_witness()
        self.write_work_id()


def do_main(work, witness, text=""):
    mk = TeimPrjXmlMake(work, witness, text)
    mk.make_dirs()
    mk.print_dir()

def do_main_csv(project):
    try:
        with open(project, "r") as f:
            rows = f.readlines()
        for row in rows:
            sp = row.strip().split("|")
            sp.append("")
            if len(sp) < 3:
                return
            work, witness, text = sp[0:3]
            do_main(work, witness, text)
    except Exception as e:
        print("EROROR in <name>_prj.csv")
        s = str(e)
        print(s)
        sys.exit(1)

def do_main_args(work, witness, text=""):
    # TODO
    """
    if not os.path.isdir(work):
        print(f"{work} Not Found.")
        sys.exit(0)
    """
    do_main(work, witness, text)

if __name__ == "__main__":
    le = len(sys.argv)
    if le == 2:
        csv = sys.argv[1]
        do_main_csv(csv)
    elif le == 3:
        work, witness = sys.argv[1:]
        do_main_args(work, witness, "")
    elif le == 4:
        work, witness, text = sys.argv[1:]
        do_main_args(work, witness, text)
    else:
        s="""
es. project.csv
flori_xml|par1|eps
flori_xml|tor1|eps
flori_xml|ven1|eps

Crea le directory SE NON esistno

teimprjxmlmake.py project.csv>
crea :
    flori_xml/
    flori_xml/__prj__
    flori_xml/par1
    flori_xml/par1/eps
    ..
teimprjxmlmake.py <work> <witnes> ")
crea :
    work/
    work/__prj__
    work/witness

teimprjxmlmake.py <work> <witnes> < text>")
crea :
    work/
    work/__prj__
    work/witness
    work/witness/text
        """
        print(s)
        #print(help)
        sys.exit(0)
