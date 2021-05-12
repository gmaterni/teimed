#!/usr/bin/env python3
# coding: utf-8

from pdb import set_trace
import argparse
import os
import pprint
import sys
from lxml import etree

import tkinter as tk
import tkinter.filedialog as fdialog
import tkinter.messagebox as mbox

from teimedlib.uarc import UaRc
from teimedlib.ualog import Log
from teimedlib.readovertags import read_over_tags
import teimedlib.pathutils as ptu

from teimedlib.edit_constants import *
from teimedlib.teim_constants import *
from teimedlib.listbox import open_listbox
from teimedlib.textedit import TextEdit
from teimedlib.textpad import TextPad
from teimedlib.findfile import find_dir_lst, find_file_lst
from teimedlib.clean_text import clean_text

import teimedlib.check_teimed as chk
from checkover import do_main as do_main_checkover
from checktxt import do_main as do_main_checktxt
from teimnote import do_main as do_main_note
from teimover import do_main as do_main_over
from teimsetid import do_main as do_main_setid
from teimxml import do_main as do_main_xml
from teixml2txt import do_main as do_main_xml2txt

__date__ = "08-05-2021"
__version__ = "0.21.1"
__author__ = "Marta Materni"


def HELP_RUN_OPS():
    s = """
teimedit.py -c florimont -d paris -t eps*.txt -s K -e

-c florimont (facoltativo)
cerca a partire dalla directory "florimont" la directory "teimcfg"
se ne trova più di uno, mostra una lista per selezionare
se ne trova uno, lo seleziona e procede
se non ne trova nessuno, esce dall'applicazione

-d paris (facoltativo)
cerca a partire dalla directory "paris" tutti i testi 
che corrispondono al nome o alla wilcard dell'opzione -t
se ne trova più di uno. mostra una lista per selezionare
se ne trova uno, lo seleziona e procede
se non ne trova nessuno, mostra un messaggio e procede

-t eps*.txt 
nome del file o wilcard dei files di testo da elaborare
se si utilizza solo la wilcard, porla tra apici o virgolette "*".txt o '*'.txt
i files sono cercati a partire dalla directory dell'opzione -d
se non è stata selezionata, la ricerca parte dalla directory corrente

-s K
sigla del manoscritto

- e <facoltativo>
cancella la storia delle precedenti sessioni
        """
    return s


g_win0 = '1000x600+50+50'
g_win1 = '1000x600+150+150'
g_win2 = '1000x600+250+250'
g_win3 = '1000x600+350+350'


def pp(data, w=60):
    return pprint.pformat(data, width=w)


rc = UaRc('.teimeditrc')

editerr = Log("w")


class TeimEdit(object):

    def __init__(self,
                 parent_teimcfg=None,
                 search_text_dir=None,
                 text_regex=None,
                 text_sign="",):
        """
        Args:
            parent_teimcfg (str, optional): dir parent di teimcfg "".
            search_text_dir (str, optional): dir parent del/dei file di testo.
            text_regex (str, optional): wilcard file/i di testo.
            text_sign (str, optional): sigla del manoscritto.
        """
        self.path_edit_err = ptu.str2path("log/teimedit.lo")
        editerr.open(ptu.path2str(self.path_edit_err), 1)
        # ARGS
        x = rc.upd("parent_teimcfg", parent_teimcfg)
        self.parent_teimcfg = ptu.str2path(x)

        x = rc.upd("search_text_dir", search_text_dir)
        self.search_text_dir = ptu.str2path(x)

        self.text_regex = rc.upd("text_regex", text_regex)
        self.text_sign = rc.upd("text_sign", text_sign)
        ###################################
        self.path_text = None
        self.path_teimcfg = ""
        self.text_dir = None
        self.log_dir = None

        self.pwd = ptu.cwd()
        self.path_entity_csv = None
        self.path_over_csv = None
        self.path_teimnote = None

        self.path_xml = None
        self.path_xml_format = None

        self.path_entity_txt = None
        self.path_entity_log = None
        self.path_entity_err = None

        self.path_setid_xml = None
        self.path_setid_log = None
        self.path_setid_err = None

        self.path_over_xml = None
        self.path_over_log = None
        self.path_over_err = None

        self.path_note_err = None
        #self.path_xml_err = None

        self.path_check_txt = None
        self.path_check_over = None

        self.path_text_txt = None
        self.path_text_err = None

        self.path_tmp = None
        # var per il controllo del check
        self.tag_num_debug = 0
        # dopo la lettutr cfg
        self.tag_over_lst = None
        self.win0 = None
        self.text_edit = None
        self.win1 = None
        self.txt1 = None
        self.win2 = None
        self.txt2 = None
        self.win3 = None
        self.txt3 = None
        # rc.get
        self.geometry_win0 = rc.get('win0', g_win0)
        self.geometry_win1 = rc.get('win1', g_win1)
        self.geometry_win2 = rc.get('win2', g_win2)
        self.geometry_win3 = rc.get('win3', g_win3)
        #####################################

    def write_file(self, path, text):
        path.write_text(text)
        self.chmod(path)

    def read_file(self, path):
        if not path.exists():
            s = ptu.path2str(path)
            self.show_log_lift(f"{s} Not Found.", True)
            return None
        with path.open('r', encoding='utf-8') as f:
            s = f.read()
        return s

    def chmod(self, path):
        try:
            ptu.chmod(path)
        except Exception as e:
            editerr.log(f"ERROR in chmod {path} .{os.linesep}{e}")
            self.top_order()
            mbox.showerror("", f"ERROR {path}")

    def find_teimtag(self):
        """
        cerca in modalità ricorsiva la dir teimgcfg a partire dal
        parametro parent_teimcfg se settato, altrimenti dalla
        dir corrente.
        Se esiste legge i file teimedcsv ed overflow.csv 
        """
        try:
            dir_lst = find_dir_lst(self.parent_teimcfg, TEIMCFG)
            name_lst = ptu.pathlist2strlist(dir_lst)
            le = len(dir_lst)
            if le == 0:
                self.iconify()
                mbox.showerror("", f"{TEIMCFG}  Not Foud")
                sys.exit()
            elif le == 1:
                self.path_teimcfg = dir_lst[0]
                self.set_teimcfg_paths()
                # path_text è il parametro iniziale
                self.find_file_text(self.text_regex)
                self.win0.after(20, self.show_info())
            else:
                def on_select(n):
                    if n < 0:
                        return
                    self.path_teimcfg = dir_lst[n]
                    self.set_teimcfg_paths()
                    self.find_file_text(self.text_regex)
                    self.win0.after(20, self.show_info())

                open_listbox(name_lst, on_select, "find teimcfg")
        except Exception as e:
            editerr.log("ERROR in find_teimeg() {os.linesep}{e}" )
            self.iconify()
            mbox.showerror("", f"{TEIMCFG}  Not Foud")
            sys.exit()
    
    def find_file_text(self, text_regex):
        try:
            file_lst = find_file_lst(self.search_text_dir, text_regex)
            name_lst = ptu.pathlist2strlist(file_lst)
            le = len(file_lst)
            if le == 0:
                self.top_order()
                mbox.showinfo("", f"{text_regex}  Not Foud",parent=self.win0)
            elif le == 1:
                path_text_str = file_lst[0]
                self.set_path_files(path_text_str)
                self.read_text_file()
                self.show_info()
                self.text_edit.focus_set()
            else:
                def load_file(n):
                    if n < 0:
                        return
                    path_text_str = file_lst[n]
                    self.set_path_files(path_text_str)
                    self.read_text_file()
                    self.show_info()
                    self.text_edit.focus_set()
                open_listbox(name_lst, load_file, "find text")
        except Exception as e:
            editerr.log("ERROR {text_regex}.{os.linesep}{e}")
            self.show_log_top("ERROR {text_regex}.{os.linesep}{e}")

    def set_teimcfg_paths(self):
        try:
            self.path_entity_csv = ptu.join(self.path_teimcfg, TEIMTAGS_CSV)
            self.path_over_csv = ptu.join(self.path_teimcfg, TEIMOVERFLOW_CSV)

            if not self.path_over_csv.exists():
                self.iconify()
                mbox.showerror("", f"{self.path_over_csv}  Not Foud")
                sys.exit()

            if not self.path_entity_csv.exists():
                self.iconify()
                mbox.showerror("", f"{self.path_entity_csv}  Not Foud")
                sys.exit()
            
            # legge la tabbella per overflow
            lst=read_over_tags(self.path_over_csv)
            # prepara la tabella per la gestione del menu
            self.tag_over_lst=chk.fill_tag_over_lst(lst)
        except Exception as e:
            editerr.log(f"ERROR set_teimcfg_paths. {e}")
            self.iconify()
            mbox.showerror("", f"ERROR set_teimcfg_paths ")
            sys.exit()

    def set_path_files(self, path_text_str):
        try:
            self.path_text = ptu.str2path(path_text_str)
            self.text_dir = self.path_text.parent
            self.log_dir = ptu.join(self.text_dir, "log")
            ptu.make_dir(self.log_dir)
            self.path_teimnote = ptu.join(self.text_dir, TEIMNOTE_CSV)

            # teim/teim.xml
            self.path_xml = ptu.update_path_name(
                self.path_text, ".txt", ".xml")

            # teim/teim_format.xml
            self.path_xml_format = ptu.update_path_name(
                self.path_text, ".txt", "_format.xml")

            # temporaneo  per la gestione dei lfiles mella dir og
            t_name = self.path_text.name
            path_log = ptu.join(self.log_dir, t_name)

            # teim/log/teim_MED.txt
            # teim/log/teim_MED.log
            # teim/log/teim_MED.ERR.log
            self.path_entity_txt = ptu.update_path_name(
                path_log, ".txt", "_MED.txt")
            self.path_entity_log = ptu.update_path_name(
                path_log, ".txt", "_MED.log")
            self.path_entity_err = ptu.update_path_name(
                path_log, ".txt", "_MED.ERR.log")

            # teim/log/teim_WID.xml
            # teim/log/teim_WID.log
            # teim/log/teim_WID.ERR.log
            self.path_setid_xml = ptu.update_path_name(
                path_log, ".txt", "_WID.xml")
            self.path_setid_log = ptu.update_path_name(
                path_log, ".txt", "_WID.log")
            self.path_setid_err = ptu.update_path_name(
                path_log, ".txt", "_WID.ERR.log")

            # teim/log/teim_OVER.xml
            # teim/log/teim_OVER.log
            # teim/log/teim_OVER.ERR.log
            self.path_over_xml = ptu.update_path_name(
                path_log, ".txt", "_OVER.xml")
            self.path_over_log = ptu.update_path_name(
                path_log, ".txt", "_OVER.log")
            self.path_over_err = ptu.update_path_name(
                path_log, ".txt", "_OVER.ERR.log")

            # teim/log/teim_note.ERR.log
            self.path_note_err = ptu.update_path_name(
                path_log, ".txt", "_note.ERR.log")

            # teim/log/teimCHECK_TXT.txt
            self.path_check_txt = ptu.update_path_name(
                path_log, ".txt", "_CHECK_TXT.log")

            # teim/log/teimCHECK_OVER.txt
            self.path_check_over = ptu.update_path_name(
                path_log, ".txt", "_CHECK_OVER.log")

            # teim/teim_text.txt
            # teim/log/teim_text.ERR.log
            self.path_text_txt = ptu.update_path_name(
                self.path_text, ".txt", "_text.txt")
            self.path_text_err = ptu.update_path_name(
                path_log, ".txt", "_text.ERR..log")

            self.path_tmp = ptu.join(self.log_dir, 'tmp')
        except Exception as e:
            editerr.log(f"ERROR set_path_fies.{os.linesep}{e}")
            self.iconify()
            mbox.showerror("", f"ERROR set_path_fies ")
            sys.exit()

    ########################
    # manu_bar
    ########################

    def top_w0(self):
        self.top_not()
        self.win0.attributes("-topmost", True)

    def top_w1(self):
        self.top_not()
        self.win1.attributes("-topmost", True)

    def top_w2(self):
        self.top_not()
        self.win2.attributes("-topmost", True)

    def top_w3(self):
        # self.win3.lift()
        self.top_not()
        self.win3.attributes("-topmost", True)

    def top_not(self):
        self.win0.attributes("-topmost", False)
        self.win1.attributes("-topmost", False)
        self.win2.attributes("-topmost", False)
        self.win3.attributes("-topmost", False)

    def top_order(self):
        self.top_not()
        self.win0.lift()

    def iconify(self):
        self.win0.iconify()
        self.win1.iconify()
        self.win2.iconify()
        self.win3.iconify()

    ########################
    # mv_file
    ########################

    # def reload_text(self):
    #     self.read_text_file()

    def open_text(self, *args):
        self.top_order()
        path_str = fdialog.askopenfilename(
            title='file',
            initialdir=self.text_dir,
            filetypes=[("text", "*.txt"),
                       ("*.*", "*.*")])
        if len(path_str) < 1:
            return
        if not ptu.exists(path_str):
            return
        self.set_path_files(path_str)
        self.read_text_file()

    def open_recenti(self):
        try:
            name_lst = self.rc_get_recenti()
            if len(name_lst) < 1:
                return
            self.top_order()
            file_lst = ptu.strlist2pathlist(name_lst)

            def load_file(n):
                if n < 0:
                    return
                path_text_str = file_lst[n]
                self.set_path_files(path_text_str)
                self.read_text_file()
                self.show_info()
                self.win0.lift()
            open_listbox(name_lst, load_file, "find text")
        except Exception as e:
            editerr.log(f" Not Found.{os.linesep}{e}")
            self.top_order()
            mbox.showerror("", f"ERROR set_path_fies ")


    def save_text(self, *args):
        s = self.get_text()
        self.write_file(self.path_text, s)
        self.rc_update_recenti(ptu.path2str(self.path_text))

    def save_text_as(self, *args):
        self.top_order()
        init_dir = ptu.path2str(self.text_dir)
        path_str = fdialog.asksaveasfilename(title='Save as Name',
                                             initialdir=init_dir)
        if path_str is None or len(path_str) < 1:
            return ""
        text = self.get_text()
        self.set_path_files(path_str)
        self.write_file(self.path_text, text)
        self.rc_update_recenti(path_str)
        title = f"TEXT: {path_str} "
        self.win0.title(title)

    ##########################
    # mv_edit su edit
    ##########################

    #################
    # mv_check
    ################
    def elab_checktxt(self):
        s = self.get_text()
        self.write_file(self.path_tmp, s)
        # def do_main(path_src, path_out):
        do_main_checktxt(ptu.path2str(self.path_tmp),
                         ptu.path2str(self.path_check_txt))
        self.chmod(self.path_check_txt)
        s = self.read_file(self.path_check_txt)
        self.show_log_top(s, True)

    def elab_checkover(self):
        s = self.get_text()
        self.write_file(self.path_tmp, s)
        # def do_main(path_src, path_csv, path_out):
        do_main_checkover(ptu.path2str(self.path_tmp),
                          ptu.path2str(self.path_over_csv),
                          ptu.path2str(self.path_check_over))
        self.chmod(self.path_check_over)
        s = self.read_file(self.path_check_over)
        self.show_log_top(s, True)

    ##########################################
    # chek edit funizoni di controllo su teimed
    ###########################################

    def del_tags(self):
        self.text_edit.tag_delete(FIND_TAGS[0])
        self.text_edit.tag_delete(FIND_TAGS[1])

    def config_tags(self):
        self.text_edit.tag_config(FIND_TAGS[0],
                                  background=BG_TAG,
                                  foreground=FG_TAG)
        self.text_edit.tag_config(FIND_TAGS[1],
                                  background=BG2_TAG,
                                  foreground=FG2_TAG)

    def next_idx(self, idx, n):
        r, c = idx.split('.')
        return f"{r}.{int(c)+n}"

    def add_tags(self, m_lst):
        self.nuum_debug = 0
        self.del_tags()
        idx = '1.0'
        for mtch in m_lst:
            # str tags
            s = mtch['s']
            # type match
            t = mtch['t']
            idx = self.text_edit.search(s,
                                        idx,
                                        regexp=False,
                                        stopindex=tk.END)
            if idx == '':
                break
            idx_end = self.next_idx(idx, len(s))
            self.text_edit.tag_add(FIND_TAGS[t], idx, idx_end)
            idx = idx_end
            self.tag_num_debug += 1
        self.config_tags()
        # usa la prima rag per spostrae il teso alla sua posiziione
        tag_lst = self.text_edit.tag_ranges(FIND_TAGS[0])
        t0 = tag_lst[0] if len(tag_lst) > 0 else "1.0"
        self.text_edit.see(t0)

    def add_tags_from_to(self, m_lst):
        self.del_tags()
        idxo = '1.0'
        self.tag_num_debug = 0
        # print("=========")
        for mtch in m_lst:
            # str tags open
            so = mtch['so']
            # str tags close
            sc = mtch['sc']
            # type match
            t = mtch['t']
            # print("")
            # print(f"A0 {idxo} {so}   {sc} * ")
            idxo = self.text_edit.search(so,
                                         idxo,
                                         regexp=False,
                                         stopindex=tk.END)
            # print(f"A1 {idxo}  {so}   {sc}  *")
            if idxo == '':
                break
            self.tag_num_debug += 1
            idx_end = self.next_idx(idxo, len(so))
            # print(f"A2 {idxo} {idx_end}  {so}   {sc}  *")
            # esiste tag di chiusura
            if sc != "":
                idxc = self.text_edit.search(sc,
                                             idxo,
                                             regexp=False,
                                             stopindex=tk.END)
                # print(f"A3 {idxo} {idx_end} {idxc  }{so}   {sc}  *")
                # trovato tag di cgiusura
                if idxc != '':
                    idx_end = self.next_idx(idxc, len(sc))
            # print(f"A4 {idxo} {idx_end} {so}   {sc}  *")
            self.text_edit.tag_add(FIND_TAGS[t], idxo, idx_end)
            idxo = idx_end
            #print(f"A5 {idxo}  {idx_end} {t}  {so}  {sc}")
        self.config_tags()
        # usa la prima rag per spostrae il teso alla sua posiziione
        tag_lst = self.text_edit.tag_ranges(FIND_TAGS[0])
        t0 = tag_lst[0] if len(tag_lst) > 0 else "1.0"
        self.text_edit.see(t0)
        ###############
        # TODO controllo tags
        #print(f"tag a:{t0}  {len(tag_lst)}")
        n = len(m_lst)
        if self.tag_num_debug != n:
            editerr.log("Error")
            for x in m_lst:
                editerr.log(f"{x['t']} {x['s']}")
                self.show_log_top(f"{x['t']} {x['s']}")
            editerr.log(self.tag_num_debug)
            self.show_log_top(self.tag_num_debug)

    def fin_entity_comma(self):
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = clean_text(text)
        m_lst = chk.check_entitys(txt_wrk)
        self.add_tags(m_lst)

    def find_entity_brackets(self):
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = clean_text(text)
        m_lst = chk.check_entity_brackets(txt_wrk)
        self.add_tags(m_lst)

    def read_tag_set(self):
        """ Lettura tags da csv
        tipo|name|tag_txt
        abbr|mlt|<expan corresp="#ab-ctr-mlt">m<ex>u</ex>lt</expan>
        abbr|Mlt|<expan corresp="#ab-ctr-mlt">M<ex>u</ex>lt</expan>
        """
        DELIMITER='|'
        lst = []
        rows=self.path_entity_csv.open().readlines()
        for row in rows:
            if row.strip() == '':
                continue
            cols = row.split(DELIMITER)
            tag_name = cols[1].strip()
            lst.append(tag_name)
        tag_set=set(lst)
        return tag_set


    def find_entity_undefined(self):
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = clean_text(text)
        m_lst = chk.check_entitys(txt_wrk)
        tag_set=self.read_tag_set()
        err_lst=[]
        for item in m_lst:
            tag=item.get('s','').replace('&','').replace(';','').strip()
            if tag in tag_set:
                continue
            item['t']=1
            err_lst.append(item)
        self.add_tags(err_lst)

    def find_over(self, po, pc, *args):
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = clean_text(text)
        m_lst = chk.check_overflow(txt_wrk, po, pc)
        #
        self.add_tags(m_lst)

    def find_form_to(self, po, pc):
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = clean_text(text)
        m_lst = chk.check_overflow(txt_wrk, po, pc)
        #
        self.add_tags_from_to(m_lst)

    #############
    # mv_elab
    #############
    def elab_teimxml(self):
        msg = self.get_text()
        self.write_file(self.path_text, msg)
        try:
            do_main_xml(ptu.path2str(self.path_text),
                        ptu.path2str(self.path_entity_csv),
                        ptu.path2str(self.path_entity_txt))
        except SystemExit as e:
            msg = f"ERROR Elab entity {os.linesep}{e}"
            editerr.log(msg)
            self.show_log_top(msg, True)
            return
        self.chmod(self.path_entity_txt)
        msg = self.read_file(self.path_entity_txt)
        self.show_win1(msg)
        ls = ["    Elab. entity",
              f"{self.path_text}",
              f"{self.path_entity_csv}",
              f"{self.path_entity_txt}"]
        self.show_log_lift(os.linesep.join(ls), True)

    def elab_teimsetid(self):
        if not self.path_entity_txt.exists():
            self.top_order()
            mbox.showinfo("", f"To do Elab. Entity",parent=self.win0)
            return
        # path_txt_1 => path_xml_1
        try:
           # def do_main(path_src, path_out, sigla_scrp, ids_start=""):
            do_main_setid(ptu.path2str(self.path_entity_txt),
                          ptu.path2str(self.path_setid_xml),
                          self.text_sign)
        except SystemExit as e:
            s = f"Errro in set id{os.linesep} {e}"
            editerr.log(s)
            self.show_log_top(s, True)
            return
        self.chmod(self.path_setid_xml)
        ls = ["    Elab. Set id",
              f"{self.path_entity_txt}",
              f"{self.path_setid_xml}",
              f"{self.text_sign}"]
        self.show_log_lift(os.linesep.join(ls), True)

    def elab_teimover(self):
        if not self.path_setid_xml.exists():
            self.top_order()
            mbox.showinfo("", f"To do Elab. Set id",parent=self.win0)
            return
        # path_xml_1 => path_xml_2
        try:
            # def do_main(src_path, out_path, csv_path):
            do_main_over(ptu.path2str(self.path_setid_xml),
                         ptu.path2str(self.path_over_xml),
                         ptu.path2str(self.path_over_csv))
        except SystemExit as e:
            msg = f"Elaborare overflow {os.linesep} {e}"
            editerr.log(msg)
            self.show_log_top(msg, True)
            return
        self.chmod(self.path_over_xml)
        ls = ["    Eelab. overflow",
              f"{self.path_setid_xml}",
              f"{self.path_over_xml}",
              f"{self.path_over_csv}"]
        self.show_log_lift(os.linesep.join(ls), True)

    def elab_teimnote(self):
        if not self.path_over_xml.exists():
            self.top_order()
            mbox.showinfo("", f"To do Elab. Over",parent=self.win0)
            return
        # path_xml_2 => path_xml
        try:
            # def do_main(src_path, out_path, note_path):
            do_main_note(ptu.path2str(self.path_over_xml),
                         ptu.path2str(self.path_xml),
                         ptu.path2str(self.path_teimnote))
        except SystemExit as e:
            msg = f"Elab. note {os.linesep} {e}"
            editerr.log(msg)
            self.show_log_top(msg, True)
            return
        self.chmod(self.path_xml)
        ls = ["    Elab. Note",
              f"{self.path_over_xml}",
              f"{self.path_xml}",
              f"{self.path_teimnote}"]
        self.show_log_lift(os.linesep.join(ls), True)
        self.format_xml()

    def elab_xml2txt(self):
        if not self.path_xml.exists():
            self.top_order()
            mbox.showinfo("", f"To do Elab. Note",parent=self.win0)
            return
        # path_xml => path_text_txt
        try:
            do_main_xml2txt(ptu.path2str(self.path_xml_format),
                            ptu.path2str(self.path_text_txt))
        except SystemExit as e:
            msg = f"ERROR Elab. note {os.linesep}{e} "
            editerr.log(msg)
            self.show_log_top(msg, True)
            return
        self.chmod(self.path_xml)
        ls = ["    XML => text",
              f"{self.path_xml}",
              f"{self.path_text_txt}"]
        self.show_log_lift(os.linesep.join(ls), True)

    def format_xml(self):
        s = self.read_file(self.path_xml)
        # TODO
        s = str(s)
        xml = '<div>'+s+'</div>'
        self.write_file(self.path_tmp, xml)
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            path = ptu.path2str(self.path_tmp)
            root = etree.parse(path, parser)
            src = etree.tostring(root,
                                 method='xml',
                                 xml_declaration=None,
                                 encoding='unicode',
                                 with_tail=True,
                                 pretty_print=True)
            """
                            standalone=None,
                            doctype=None,
                            exclusive=False,
                            inclusive_ns_prefixes=None,
                            strip_text=False)
            """
            self.show_win2(src)
            self.write_file(self.path_xml_format, src)
        except etree.Error as e:
            s = f"ERROR  XML {os.linesep}{e}"
            self.show_log_top(s, True)

    def reload_xml(self):
        txt = self.read_file(self.path_entity_txt)
        self.show_win1(txt)
        xml = self.read_file(self.path_xml_format)
        self.show_win2(xml)
        self.top_order()
        self.win2.lift()

    ##############
    # mv_del
    ##############
    def delete_txt_all(self):
        self.delete_txt1()
        self.delete_txt2()
        self.delete_txt3()

    def delete_txt1(self):
        if self.txt1 is not None:
            self.txt1.delete('1.0', tk.END)

    def delete_txt2(self):
        if self.txt2 is not None:
            self.txt2.delete('1.0', tk.END)

    def delete_txt3(self):
        if self.txt3 is not None:
            self.txt3.delete('1.0', tk.END)

    def remove_log(self):
        path_lst = ptu.list_path(self.log_dir)
        for p in path_lst:
            p.unlink()

    ##############
    # mv_log
    ##############

    # teim/log/teimCHECK_TXT.txt
    def show_check_txt(self):
        self.read_log_file(self.path_check_txt)

    # teim/log/teimCHECK_OVER.txt
    def show_check_over(self):
        self.read_log_file(self.path_check_over)

    # teim/log/teim_MED.log
    def show_entity_log(self):
        self.read_log_file(self.path_entity_log)

    # teim/log/teim_MED.ERR.log
    def show_entity_err(self):
        self.read_log_file(self.path_entity_err)

    # teim/log/teim_WID.log
    def show_setwid_log(self):
        self.read_log_file(self.path_setid_log)

    # teim/log/teim_WID.ERR.log
    def show_setwid_err(self):
        self.read_log_file(self.path_setid_err)

    # TODO      teim/log/teim_OVER.xml
    # teim/log/teim_OVER.log
    def show_over_log(self):
        self.read_log_file(self.path_over_log)

    # teim/log/teim_OVER.ERR.log
    def show_over_err(self):
        self.read_log_file(self.path_over_err)

    # teim/log/teim_OVER.ERR.log
    def show_note_err(self):
        self.read_log_file(self.path_note_err)

    # teim/log/teim_text.txt
    def show_text_txt(self):
        self.read_log_file(self.path_text_txt)

    # TODO teim/log/teim_text.ERR.log
    def show_text_txt_err(self):
        self.read_log_file(self.path_text_err)

    # log/teimedit.log
    def show_edit_err(self):
        self.read_log_file(self.path_edit_err)

    def open_log(self):
        self.top_order()
        path = fdialog.askopenfilename(
            parent=self.win0,
            title='log',
            initialdir=self.log_dir,
            filetypes=[("all", "*.*"),
                       ("log", "*.log"),
                       ("text", "*.txt"),
                       ("xml", "*.xml")])
        if len(path) < 1:
            return
        path = ptu.str2path(path)
        if path.exists():
            s = self.read_file(path)
            self.show_log_top(s)
        else:
            self.top_order()
            mbox.showinfo("", f"Not Foud",parent=self.win0)
    
    #############
    # menu_bar
    ############
    def show_info(self, top=False):
        #abs_teimcfg = os.path.abspath(str(self.teimcfg_dir))
        #abs_text = os.path.abspath(str(self.text_dir))
        wrk_dir = self.pwd
        info = [
            "---------------------------",
            f"work dir       : {wrk_dir}  ",
            f"parent teimcfg : {self.parent_teimcfg}",
            f"search text dir: {self.search_text_dir}",
            f"text RegEx     : {self.text_regex}",
            f"sigla          : {self.text_sign}",
            "---------------------------",
            f"teimed tags    : {self.path_entity_csv}",
            f"overflow tags  : {self.path_over_csv}",
            f"text dir       : {self.text_dir}",
            f"text name      : {self.path_text}",
            f"note           : {self.path_teimnote}",
            "---------------------------",
            f"chek  txt      : {self.path_check_txt}",
            f"check over     : {self.path_check_over}",
            "",
            f"elab  entity   : {self.path_entity_txt}",
            f"log   entity   : {self.path_entity_log}",
            f"ERR   entity   : {self.path_entity_err}",
            "",
            f"elab  set id   : {self.path_setid_xml}",
            f"log   set id   : {self.path_setid_log}",
            f"err   set id   : {self.path_setid_err}",
            "",
            f"elab  over     : {self.path_over_xml}",
            f"log   over     : {self.path_over_log}",
            f"err   over     : {self.path_over_err}",
            "",
            f"elab  note     : {self.path_xml}",
            f"err   note     : {self.path_note_err}",
            "",
            f"elab  text     : {self.path_text_txt}",
            f"err   text     : {self.path_text_err}",
            "---------------------------",
        ]
        s = os.linesep.join(info)
        if top:
            self.show_log_top(s)
        else:
            self.show_log_lift(s)

    def show_options(self):
        s = HELP_RUN_OPS()
        self.show_log_top(s)

    def get_text(self):
        s = self.text_edit.get('1.0', 'end')
        return s.strip()

    def read_text_file(self):
        if self.path_text.exists():
            s = self.read_file(self.path_text)
            self.rc_update_recenti(ptu.path2str(self.path_text))
        else:
            self.write_file(self.path_text, "Empty")
            r = ["", f"File  {self.path_text} Not Found.",
                 "", f"Crated {self.path_text} empyt."]
            s = os.linesep.join(r)
        self.text_edit.insert_text(s)
        file_name = f"{self.path_text}"
        self.win0.title(file_name)
        # self.lbl_path_var.set(file_name)

    def read_log_file(self, path):
        if path.exists():
            s = self.read_file(path)
            self.show_log_top(s)
        else:
            self.top_order()
            mbox.showinfo("", f"{path} Not Foud",parent=self.win0)

    def show_log_top(self, msg, append=False):
        self.show_log(msg, append)
        self.top_w3()

    def show_log_lift(self, msg, append=False):
        self.show_log(msg, append)
        self.win3.lift()

    def show_log(self, msg, append=False):
        msg = "" if msg is None else msg
        if append:
            r = os.linesep.join(["", "", msg])
            self.txt3.insert(tk.END, r)
            self.txt3.see(tk.END)
        else:
            r = os.linesep.join(["", msg])
            self.txt3.delete('1.0', tk.END)
            self.txt3.insert('1.0', r)

    #############################
    # open window
    #############################

# tag_list = [
#     ['damage_high', '{3%', '%3}', 'ODAMH', 'CDAMH'],
#     ['damage_medium', '{2%', '%2}', 'ODAMM', 'CDAMM'],
#     ['damage_low', '{1%', '%1}', 'ODAML', 'CDAML'],
#     ['damage', '{0%', '%0}', 'ODAM', 'CDAM'],
#     ['monologue', '{_', '_}', 'OMON', 'CMON'],
#     ['directspeech', '{', '}', 'ODRD', 'CDRD'],
#     ['agglutination_uncert', '[_', '_]', 'OAGLU', 'CAGLU'],
#     ['agglutination', '[', ']', 'OAGLS', 'CAGLS'],
# ]

    def open_win0(self):

        def add_mv_check():
            # lst.append([func_type,name,so,sc,po,pc])
            lst = self.tag_over_lst
            for item in lst:
                t, name, so, sc, po, pc = item
                lbl = f'{name}:  {so}   {sc}'
                if t == 0:
                    mv_check.add_command(
                        label=lbl,
                        command=lambda x=po, y=pc, : self.find_form_to(x, y))
                else:
                    mv_check.add_command(
                        label=lbl,
                        command=lambda x=po, y=pc: self.find_over(x, y))
            mv_check.add_separator()

        def new_mv():
            mv = tk.Menu(menu_bar, tearoff=0)
            mv.config(
                font=FONT_MENU,
                bg=BG_MENU,
                fg=FG_MENU,
                activebackground=BG2_MENU,
                activeforeground=FG2_MENU,
                relief=tk.SOLID)
            return mv

        self.win0 = tk.Tk()
        #self.win0.withdraw()
        self.win0.title("TeimEdit")
        self.win0.geometry(self.geometry_win0)
        self.win0.config(background=BG_WIN, pady=2)
        self.win0.protocol("WM_DELETE_WINDOW", lambda: False)
        # self.lbl_path_var = tk.StringVar()
        # self.lbl_path_var.set("")
        self.text_edit = TextEdit(self.win0)
        self.text_edit.focus_set()
        self.text_edit.config(spacing1=2, spacing3=2)
        self.text_edit.pack(fill=tk.BOTH, expand=True)

        menu_bar = tk.Menu(self.win0, tearoff=0)
        menu_bar.config(
            font=FONT_MENU,
            bg=BG_MENU,
            fg=FG_MENU,
            activebackground=BG2_MENU,
            activeforeground=FG2_MENU,
            bd=2,
            relief=tk.SOLID)
        self.win0.config(menu=menu_bar)

        mv_file = new_mv()
        mv_file.add_command(
            label='Reload', command=self.read_text_file, underline=0)
        mv_file.add_command(label='Recent Files',
                            command=self.open_recenti, underline=0)
        mv_file.add_separator()
        mv_file.add_command(label='Open  Ctrl-O', command=self.open_text)
        mv_file.add_separator()
        mv_file.add_command(label='Save  Ctrl-S', command=self.save_text)
        mv_file.add_command(label='Save As... Ctrl-Shift-S',
                            command=self.save_text_as)
        mv_file.add_separator()
        mv_file.add_command(label='Quit', command=self.app_quit,
                            underline=0,
                            background=BG_MENU_LBL,
                            foreground=FG_MENU_LBL,
                            activebackground=BG2_MENU_LBL,
                            activeforeground=FG2_MENU_LBL)
        mv_file.add_separator()
        self.text_edit.bind("<Control-o>", self.open_text)
        self.text_edit.bind("<Control-s>", self.save_text)
        self.text_edit.bind("<Control-Shift-S>", self.save_text_as)
        # TODO
        self.text_edit.bind("<Control-q>", self.app_quit)

        mv_edit = new_mv()
        mv_edit.add_command(label="Undo     Ctrl-Z")
        mv_edit.add_command(label="Redo     Ctrl-Shift-Z",
                            command=self.text_edit.on_redo)
        mv_edit.add_separator()
        mv_edit.add_command(label="Cut      Ctrl-X")
        mv_edit.add_command(label="Copy     Ctrl-C")
        mv_edit.add_command(label="Paste    Ctrl-V")

        mv_check = new_mv()
        mv_check.add_command(label='Check Entity Log',
                             command=self.elab_checktxt)
        mv_check.add_command(label='Check Overflow Log',
                             command=self.elab_checkover)
        mv_check.add_separator()
        mv_check.add_command(label='Clean', command=self.del_tags)
        mv_check.add_separator()
        mv_check.add_command(label='Entity Comma',
                             command=self.fin_entity_comma)
        mv_check.add_command(label='Entity Brackets',
                             command=self.find_entity_brackets)
        mv_check.add_command(label='Entity Undefined',
                             command=self.find_entity_undefined)
        mv_check.add_separator()
        #add_mv_check()

        mv_elab = new_mv()
        mv_elab.add_command(label='Elab. Entity', command=self.elab_teimxml)
        mv_elab.add_command(label='Elab. Set ID', command=self.elab_teimsetid)
        mv_elab.add_command(label='Elab. Overflow', command=self.elab_teimover)
        mv_elab.add_command(label='Elab. Note', command=self.elab_teimnote)
        mv_elab.add_separator()
        mv_elab.add_command(label='.XML => .txt', command=self.elab_xml2txt)
        mv_elab.add_separator()
        mv_elab.add_command(label='Reload XML', command=self.reload_xml)

        mv_log = new_mv()
        mv_log.add_command(label='Check Text Err.',
                           command=self.show_check_txt)
        mv_log.add_command(label='Check Over Err.',
                           command=self.show_check_over)
        mv_log.add_separator()
        mv_log.add_command(label='Entity Log.', command=self.show_entity_log)
        mv_log.add_command(label='Entity Err.', command=self.show_entity_err)
        mv_log.add_separator()
        mv_log.add_command(label='Set ID Log.', command=self.show_setwid_log)
        mv_log.add_command(label='Set ID Err.', command=self.show_setwid_err)
        mv_log.add_separator()
        mv_log.add_command(label='Overflow Log.', command=self.show_over_log)
        mv_log.add_command(label='Overflow Err.', command=self.show_over_err)
        mv_log.add_separator()
        mv_log.add_command(label='Note Err.', command=self.show_note_err)
        mv_log.add_separator()
        mv_log.add_command(label='*_text_.txt', command=self.show_text_txt)
        mv_log.add_command(label='.XML => .txt Err.',
                           command=self.show_text_txt_err)
        mv_log.add_separator()
        mv_log.add_command(label='TeimEdit Err.', command=self.show_edit_err)
        mv_log.add_separator()
        mv_log.add_command(label='Read Log', command=self.open_log)

        mv_del = new_mv()
        mv_del.add_command(label='Entity', command=self.delete_txt1)
        mv_del.add_command(label='XML', command=self.delete_txt2)
        mv_del.add_command(label='Log', command=self.delete_txt3)
        mv_del.add_command(label='All', command=self.delete_txt_all)
        mv_del.add_separator()
        mv_del.add_command(label='Remove log files', command=self.remove_log)

        mv_help = new_mv()
        mv_help.add_command(label='Files & Directory', command=self.show_info)
        mv_help.add_command(label='run options', command=self.show_options)

        # orizontale
        menu_bar.add_cascade(label='File', menu=mv_file, underline=0)
        menu_bar.add_cascade(label='Edit', menu=mv_edit, underline=0)
        menu_bar.add_cascade(label='Check', menu=mv_check, underline=0)
        menu_bar.add_cascade(label='Elab.', menu=mv_elab, underline=1)
        menu_bar.add_cascade(label='Log', menu=mv_log, underline=0)
        menu_bar.add_cascade(label='Del.', menu=mv_del, underline=0)
        menu_bar.add_command(label='    1-2-3-4 ', command=self.top_order)
        menu_bar.add_command(label=' 1 ', command=self.top_w0)
        menu_bar.add_command(label=' 2 ', command=self.top_w1)
        menu_bar.add_command(label=' 3 ', command=self.top_w2)
        menu_bar.add_command(label=' 4 ', command=self.top_w3)
        s = f"                               "
        menu_bar.add_command(
            label=s, activeforeground=FG_MENU, activebackground=BG_MENU),
        menu_bar.add_cascade(label='Help', menu=mv_help)

        self.open_win1()
        self.open_win2()
        self.open_win3()

        self.show_win1("")
        self.show_win2("")
        self.show_win3("")
        ############
        # cerca la dir teimcfg_dir partendo 
        # -c teimcfg_dir
        # se non la trova exit
        # invoca
        # set_file_path
        # read_over_tags
        # read_text_file
        # self.find_file_text(self.path_text)
        self.find_teimtag()
        ############
        add_mv_check()
        tk.mainloop()
        ##############

    def open_win1(self):
        self.win1 = tk.Tk()
        #self.win1=tk.Toplevel(self.win0)
        self.win1.title('ENTITY')
        self.win1.protocol("WM_DELETE_WINDOW", lambda: False)
        self.win1.rowconfigure(0, weight=1)
        self.win1.columnconfigure(0, weight=1)
        self.win1.geometry(self.geometry_win1)
        self.txt1 = TextPad(self.win1)
        self.txt1.config(spacing1=2, spacing3=2)
        self.txt1.grid(sticky='nsew')

    def open_win2(self):
        self.win2 = tk.Tk()
        self.win2.title('XML')
        self.win2.protocol("WM_DELETE_WINDOW", lambda: False)
        self.win2.rowconfigure(0, weight=1)
        self.win2.columnconfigure(0, weight=1)
        self.win2.geometry(self.geometry_win2)
        self.txt2 = TextPad(self.win2)
        self.txt2.config(spacing1=2, spacing3=2)
        self.txt2.grid(sticky='nsew')

    def open_win3(self):
        self.win3 = tk.Tk()
        self.win3.protocol("WM_DELETE_WINDOW", lambda: False)
        self.win3.title('LOG')
        self.win3.rowconfigure(0, weight=1)
        self.win3.columnconfigure(0, weight=1)
        self.win3.geometry(self.geometry_win3)
        self.txt3 = TextPad(self.win3)
        self.txt3.config(spacing1=1, spacing3=1)
        self.txt3.grid(sticky='nsew')
        self.txt3.configure(font=FONT_LOG, bg=BG_LOG, fg=FG_LOG)

    def show_win1(self, s):
        s = '' if s is None else s
        self.txt1.delete('1.0', tk.END)
        self.txt1.insert('1.0', s)

    def show_win2(self, s):
        s = '' if s is None else s
        self.txt2.delete('1.0', tk.END)
        self.txt2.insert('1.0', s)

    def show_win3(self, s):
        s = '' if s is None else s
        self.txt3.delete('1.0', tk.END)
        self.txt3.insert('1.0', s)

    def app_quit(self, *args):
        # yn = mbox.askyesno("", "Quit ?", parent=self.win0)
        # if not yn:
        #     return
        #self.win0.deiconify()
        self.rc_save()
        sys.exit(0)
        # self.win3.quit()
        # self.win2.quit()
        # self.win1.quit()
        # self.win0.quit()

    def rc_get_recenti(self):
        lst = rc.get('recenti', [])
        return lst

    def rc_update_recenti(self, path):
        lst = rc.get("recenti", [])
        lst.append(path)
        lst = list(set(lst))
        rc.set('recenti', lst)

    def rc_save(self):
        rc.set('win0', self.win0.winfo_geometry())
        rc.set('win1', self.win1.winfo_geometry())
        rc.set('win2', self.win2.winfo_geometry())
        rc.set('win3', self.win3.winfo_geometry())
        rc.save()
        #rc.prn("save_rc")

def do_main(parent_teimcfg,
            search_text_dir,
            path_text,
            sign):
    rc.load()
    #rc.prn("rc.load")
    tme = TeimEdit(parent_teimcfg,
                   search_text_dir,
                   path_text,
                   sign)
    tme.open_win0()


def prn_help():
    print(HELP_RUN_OPS())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    le = len(sys.argv)
    if le == 1:
        print(f"author: {__author__}")
        print(f"release: {__version__} { __date__}")
        parser.print_help()
        sys.exit()
    parser.add_argument('-c',
                        dest="parentcfg",
                        required=False,
                        default=None,
                        metavar="dir of teimcfg",
                        help="[-c <teimcfg_dir>]")
    parser.add_argument('-d',
                        dest="parenttext",
                        required=False,
                        default=None,
                        metavar="dir of text",
                        help="[-d <text_dir>]")
    parser.add_argument('-t',
                        dest="txt",
                        required=False,
                        default="",
                        type=str,
                        metavar="text name",
                        help="[-t <file>.txt]")
    parser.add_argument('-s',
                        dest="sign",
                        required=False,
                        default="K",
                        metavar="text sign",
                        help="[-s <sign>]")
    parser.add_argument('-x',
                        action="store_true",
                        required=False,
                        help="[-x  print examples]")
    parser.add_argument('-e',
                        action="store_true",
                        required=False,
                        help="[-e delete history]")
    args = parser.parse_args()
    if args.x:
        prn_help()
        sys.exit()
    if args.e:
        rc.remove()
        if args.txt == '':
            sys.exit()
    do_main(args.parentcfg,
            args.parenttext,
            args.txt,
            args.sign)
