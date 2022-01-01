#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import sys
# import os
# from teimedlib.ualog import Log
import pathlib as pth
import teimedlib.pathutils as ptu
import pprint

__date__ = "01-01-2022"
__version__ = "0.3.0"
__author__ = "Marta Materni"

# XXX riferimentoiper l'elencop witness e text
WITNESS_NAME_RIF = "_setid.json"
TEXT_NAME_RIF = "_setid.json"


class TeimPrjMap(object):
    """
    controlla l'esistenza del progetto
    se run_dir e un parente di prj_dir si sposta su prj_dir
    setta le dir del progetto
    setta i comandi per witness_names (cmds)
    setta i domandi per witnes_text (txt_cmds)
    i dati sono accessibili mediante property

    il nome del progetto (work) + senza estensione
    """

    def __init__(self):
        self._prj_name = ""
        self._run_dir_p = pth.Path().cwd()
        self._run_dir_pos = 0
        self._prj_dir_p = None
        #####################################
        self._witness_names = []
        self._witness_text_names = []
        self._cmds = {}
        self._txt_cmds = {}

    def pp(self, data, w=80):
        return pprint.pformat(data, indent=2, width=w)

    @property
    def prj_name(self):
        return str(self._prj_name)

    @property
    def run_dir(self):
        s = ptu.path2str(self._run_dir_p)
        return s

    @property
    def run_dir_pos(self):
        return self._run_dir_pos

    @property
    def prj_dir(self):
        s = ptu.path2str(self._prj_dir_p)
        return s

    @property
    def witness_name_lst(self):
        return sorted(self._witness_names)

    @property
    def witness_text_name_lst(self):
        return sorted(self._witness_text_names)

    @property
    def cmd_lst(self):
        return self._cmds

    @property
    def txt_cmd_lst(self):
        return self._txt_cmds

    ################################################
    # controllo run_dir ef eventuale chdir su prj_dir
    #################################################

    def read_prj_name(self, prj_path):
        with open(prj_path, "r") as f:
            prj_name = f.read().strip()
        return prj_name

    def find_prj_in_dir(self):
        """
        ritorna il nome di prj se lo trovata
        altrimenti ritornn ''
        """
        lst = self._run_dir_p.rglob("__prj__")
        prj_paths = [pid for pid in lst]
        if prj_paths == []:
            return ""
        pid_path = prj_paths[0]
        prj_name = self.read_prj_name(pid_path)
        return prj_name

    def find_prj_in_desc_dir(self):
        """
        cerca a partire dalla run_dir
        """
        lst = self._run_dir_p.rglob("__prj__")
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
        """
        controlla se run_dir==prj_dir
        e se self.prj_name!==project_name della dir
        setta run_dir_pos=1
        se run_dir è parent di cd_prj_dir
        controllo che self.prj_name== prj_name della dur
        e setta run_dir_pos=2
        """
        prj_name = self.find_prj_in_dir()
        if prj_name == '':
            input("ERROR_A")
            return
        if prj_name == self._run_dir_p.name and prj_name == self._prj_name:
            self._prj_dir_p = self._run_dir_p
            # run_dir = prj_dir
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
                self._prj_dir_p = path.parent
                self._run_dir_pos = 2

    def check_prj_dir_of_none(self):
        """
        controlla si run_dir==prj_dir con self.prj_name=='
        viene settato quello di prj_dir
        setta run_dir_pos=1
        """
        prj_name = self.find_prj_in_dir()
        if prj_name == '':
            self._run_dir_pos = 0
            return
        if prj_name == self._run_dir_p.name:
            self._prj_name = prj_name
            self._prj_dir_p = self._run_dir_p
            # pwd è la dir  prj_dir
            self._run_dir_pos = 1
        elif prj_name =='':
            self._run_dir_pos = 0
        else:
            self._prj_name = prj_name
            prj_paths, prj_names = self.find_prj_in_desc_dir()
            for path in prj_paths:
                p_name = self.read_prj_name(path)
                if p_name == self._prj_name:
                    self._prj_dir_p = path.parent
            self._run_dir_pos = 2

    def check_prj_dir(self, prj_name=None):
        """"
        ritorna
         1) run_dir == prj_dir
         2) run_dir = parent di prj_dir
        """
        self._prj_name = prj_name
        if not self._prj_name:
            self.check_prj_dir_of_none()
        else:
            self.check_prj_dir_of_name()
        return self._run_dir_pos

    ######################################

    def set_witness_cmds(self):
        self._witness_names = []
        self._cmds = {}
        lst = []
        prj_json_dir = pth.Path().joinpath(self._prj_dir_p, "prj")
        for x in prj_json_dir.iterdir():
            lst.append(x)
            # riferimento per individura witness
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
            v = v.relative_to(self._prj_dir_p)
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
                prj_wtn = f"prj_{wtn}"
                # print(f"** prj_wtn: {prj_wtn} ")
                path_prj_wtn = pth.Path().joinpath(self._prj_dir_p, prj_wtn)
                # print(f"*  path_prj_wtn: {path_prj_wtn} ")
                if path_prj_wtn.exists():
                    for txt_cmd in path_prj_wtn.iterdir():
                        # print(f"**  txt_cmd: {txt_cmd} ")
                        #print(f"txt_cmd: {txt_cmd}")
                        lst.append(txt_cmd)
                # else:
                #     print(f"!! NOT FOUND   path_prj_wtn: {path_prj_wtn} ")

        except Exception as e:
            msg = f"set_witness_text_cmds()\n {e}"
            raise Exception(msg)
            # sys.exit(0)

        for x in sorted(lst):
            # riferimento per individurare text
            # p = x.name.find("_txt.json")
            p = x.name.find(TEXT_NAME_RIF)
            if p < 0:
                continue
            # wtn_name = x.parent.name.replace("_prj", "")
            wtn_name = x.parent.name.replace("prj_", "")
            txt_name = x.name[0:p]
            # print(f'x:{x}')
            # print(f'x.parent.name:{x.parent.name}')
            # print(f'wtn_name:{wtn_name}')
            # print(f'txt_name:{txt_name}')
            self._witness_text_names.append([wtn_name, txt_name])
            if wtn_name not in self._txt_cmds.keys():
                self._txt_cmds[wtn_name] = {}
                # print(f'NOT in wtn_name:{wtn_name}')
                # print(f'{pp(self._txt_cmds)}')
            self._txt_cmds[wtn_name][txt_name] = []
        #
        for x in sorted(lst):
            prj_wtn = x.parent.name
            txt_cmd = x.name
            json_cmd = x.absolute()
            json_cmd = json_cmd.relative_to(self._prj_dir_p)
            json_cmd = f"{json_cmd}"
            # print(f'\n* x:{x}')
            # print(f'* json_cmd:{json_cmd}')
            for w_k, w_v in self._txt_cmds.items():
                # print(f"* w_k:{w_k}  w_v:{w_v} ")
                for t_k in w_v:
                    s = prj_wtn.replace('prj_', '')
                    # print(f"** prj_wtn:{prj_wtn}    wk:{w_k}    s:{s}")
                    # print(f"** txt_cmd:{txt_cmd} tk: {t_k}")
                    # TODO if prj_wtn.find(w_k) == 0: inversione prj_
                    if s.find(w_k) == 0:
                        if txt_cmd.find(t_k) == 0:
                            self._txt_cmds[w_k][t_k].append([x.name, json_cmd])

    def prn_dirs(self):
        print(f"prj_name     :{self.prj_name}")
        print(f"run_dir      :{self.run_dir}")
        print(f"run_dir_pos  :{self.run_dir_pos}")
        print(f"prj_dir      :{self.prj_dir}")
        print(f"witness_names:{self.pp(self.witness_name_lst,80)}")
        print(f"witness_text_names:{self.pp(self.witness_text_name_lst,80)}")
        return self

    def prn_cmds(self):
        print(f"cmds         :{self.pp(self.cmd_lst,60)}")
        return self

    def prn_txt_cmds(self):
        print(f"txt_cmds     :{self.pp(self.txt_cmd_lst,60)}")
        return self

    def main(self, prj_name=None):
        #self.check_prj_dir(prj_name)
        if self._run_dir_pos == 0:
            msg = "Project Not Found"
            sys.exit(msg)
        self.set_witness_cmds()
        self.set_witness_text_cmds()
        # s=pp(self._cmds)
        # print(s)
        # s=pp(self._txt_cmds)
        # print(s)
        # self.prn_dirs()
        # self.prn_cmds()
        # self.prn_txt_cmds()
        # sys.exit()
        return self

# work="nome projetto"
# TeimPrjMgr().main(work)
