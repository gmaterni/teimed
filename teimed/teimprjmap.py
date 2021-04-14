#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace

import sys
import os
from teimed.ualog import Log
import pathlib as pth
import pprint

__date__ = "20-03-2021"
__version__ = "0.1.3"
__author__ = "Marta Materni"

WITNESS_NAME_RIF = "_xml.json"
TEXT_NAME_RIF = "_txt.json"


class TeimPrjMap(object):
    """controlla l'esistenza del progetto
    se run_dir e un parente di prj_dir si sposta su prj_dir
    setta le dir del progetto
    setta i comandi per witness_names (cmds)
    setta i domandi per witnes_text (txt_cmds)
    i dati sono accessibili mediante property

    il nome del progetto (work) + senza estensione
    """

    def __init__(self):
        self._prj_name = ""
        self._run_dir = pth.Path().cwd()
        self._run_dir_pos = 0
        self._prj_dir = ""
        #####################################
        self._witness_names = []
        self._witness_text_names = []
        self._cmds = {}
        self._txt_cmds = {}

    def pp(self, data, w=80):
        if data is None:
            return ""
        return pprint.pformat(data, indent=2, width=w)

    @property
    def prj_name(self):
        return str(self._prj_name)

    @property
    def run_dir(self):
        return self._run_dir

    @property
    def run_dir_pos(self):
        return self._run_dir_pos

    @property
    def prj_dir(self):
        return self._prj_dir

    @property
    def witness_names(self):
        return self._witness_names

    @property
    def witness_text_names(self):
        return self._witness_text_names

    @property
    def cmds(self):
        return self._cmds

    @property
    def txt_cmds(self):
        return self._txt_cmds

    ################################################
    # controllo run_dir ef eventula chdir su prj_dir
    #################################################

    def read_prj_name(self, prj_path):
        with open(prj_path, "r") as f:
            prj_name = f.read().strip()
        return prj_name

    def find_prj_in_dir(self):
        lst = self._run_dir.glob("__prj__")
        prj_paths = [pid for pid in lst]
        if prj_paths == []:
            return ""
        pid_path = prj_paths[0]
        prj_name = self.read_prj_name(pid_path)
        return prj_name

    def find_prj_in_desc_dir(self):
        # TODO cerca a partire dalla run_dir
        lst = self._run_dir.rglob("__prj__")
        prj_paths = [pid for pid in lst]
        if prj_paths == []:
            return [], []
        prj_names = []
        for path in prj_paths:
            prj_name = self.read_prj_name(path)
            prj_names.append(prj_name)
            # print(path)
        return prj_paths, prj_names

    def check_prj_dir_of_name(self):
        """controlla se run_dir==prj_dir
        e se self.prj_name!==project_name della dir
        setta run_dir_pos=1
        se run_dir è parent di cd_prj_dir
        controllo che self.prj_name== prj_name della dur
        e setta run_dir_pos=2
        """
        prj_name = self.find_prj_in_dir()
        if prj_name == self._run_dir.name and prj_name == self._prj_name:
            self._prj_dir = self._run_dir
            self._run_dir_pos = 1
            return
        prj_paths, prj_names = self.find_prj_in_desc_dir()
        if prj_names == []:
            return
        for path in prj_paths:
            # print(f"path: {path}")
            prj_name = self.read_prj_name(path)
            # print(f"prj_name: {prj_name}{os.linesep}")
            if prj_name == self._prj_name:
                self._prj_dir = path.parent
                self._run_dir_pos = 2
                # TODO assegna run_dir
                # self._run_dir=self._prj_dir

    def check_prj_dir(self):
        """controlla si run_dir==prj_dir con self.prj_name=='
        viene settato quello di prj_dir
        setta run_dir_pos=1
        """
        prj_name = self.find_prj_in_dir()
        if prj_name == self._run_dir.name:
            self._prj_name = prj_name
            self._prj_dir = self._run_dir
            self._run_dir_pos = 1

    def set_prj_dir(self, prj_name=""):
        self._prj_name = prj_name
        if self._prj_name == "":
            self.check_prj_dir()
        else:
            self.check_prj_dir_of_name()
        if self._run_dir_pos == 2:
            # TODO cambia posizione
            # os.chdir(self._prj_dir)
            pass

    ######################################
    def set_witness_cmds(self):
        self._witness_names = []
        self._cmds = {}
        lst = []
        prj_json_dir = pth.Path().joinpath(self._prj_dir, "prj")
        for x in prj_json_dir.iterdir():
            lst.append(x)
            # TODO riferimento per individura witness
            # p = x.name.find("_xml.json")
            p = x.name.find(WITNESS_NAME_RIF)
            if p < 0:
                continue
            wtn_name = x.name[:p]
            self._cmds[wtn_name] = []
            self._witness_names.append(wtn_name)

        for x in sorted(lst):
            json_name = x.name
            v = x.absolute()
            v = v.relative_to(self._prj_dir)
            json_cmd = f"{v}"
            for wtn_name in self._witness_names:
                if json_name.find(wtn_name) == 0:
                    self._cmds[wtn_name].append([json_name, json_cmd])

    # ven1_prj/eps01_txt.jsons
    def set_witness_text_cmds(self):
        self._txt_cmds = {}
        lst = []
        self._witness_text_names = []
        try:
            # print(f"**** self._prj_dir: {self._prj_dir}")
            for wtn in self._witness_names:
                wtn_prj = f"{wtn}_prj"
                #path_wtn_prj = pth.Path().joinpath(wtn_prj)
                #print(f"** path_wtn_prj: {path_wtn_prj} ")
                path_wtn_prj = pth.Path().joinpath(self._prj_dir, wtn_prj)
                # print(f"** path_wtn_prj: {path_wtn_prj} ")
                if path_wtn_prj.exists():
                    for txt_cmd in path_wtn_prj.iterdir():
                        # print(f"txt_cmd: {txt_cmd}")
                        lst.append(txt_cmd)
        except Exception as e:
            print(str(e))
            # sys.exit(0)
        for x in sorted(lst):
            # riferimento per individurare text
            # p = x.name.find("_txt.json")
            p = x.name.find(TEXT_NAME_RIF)
            if p < 0:
                continue
            wtn_name = x.parent.name.replace("_prj", "")
            txt_name = x.name[0:p]
            self._witness_text_names.append([wtn_name, txt_name])
            if wtn_name not in self._txt_cmds.keys():
                self._txt_cmds[wtn_name] = {}
            self._txt_cmds[wtn_name][txt_name] = []
        #
        for x in sorted(lst):
            wtn_prj = x.parent.name
            txt_cmd = x.name
            json_cmd = x.absolute()
            json_cmd = json_cmd.relative_to(self._prj_dir)
            json_cmd = f"{json_cmd}"
            for w_k, w_v in self._txt_cmds.items():
                for t_k in w_v:
                    if wtn_prj.find(w_k) == 0:
                        if txt_cmd.find(t_k) == 0:
                            self._txt_cmds[w_k][t_k].append([x.name, json_cmd])

    def prn_dirs(self):
        print(f"prj_name     :{self.prj_name}")
        print(f"run_dir      :{self.run_dir}")
        print(f"run_dir_pos  :{self.run_dir_pos}")
        print(f"prj_dir      :{self.prj_dir}")
        print(f"witness_names:{self.pp(self.witness_names,80)}")
        print(f"witness_text_names:{self.pp(self.witness_text_names,80)}")
        return self

    def prn_cmds(self):
        print(f"cmds         :{self.pp(self.cmds,60)}")
        return self

    def prn_txt_cmds(self):
        print(f"txt_cmds     :{self.pp(self.txt_cmds,60)}")
        return self

    def main(self, prj_name=None):
        self.set_prj_dir(prj_name)
        if self._run_dir_pos == 0:
            print("Project Not Found")
            sys.exit(0)
        self.set_witness_cmds()
        self.set_witness_text_cmds()
        return self

    # work="nome projetto"
    # TeimPrjMgr().main(work)
