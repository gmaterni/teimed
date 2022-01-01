#!/usr/bin/env python3
# coding: utf-8

from pdb import set_trace
#import atexit
import os
import pathlib as pth
import pprint
import sys

import tkinter as tk
# import tkinter.filedialog as fdialog
import tkinter.messagebox as mbox

from teimedlib.edit_constants import *
from teimedlib.teim_constants import *

from teimedlib.listbox import open_listbox
from teimedlib.textpad import TextPad

from prjmgr import PrjMgr
from teimprjtext import do_main as do_main_prj_text
from teimedlib.teimprjmap import TeimPrjMap
from teimprjsave import save_text

from teimedlib.ualog import Log
import teimedlib.pathutils as ptu

__date__ = "01-01-2022"
__version__ = "0.3.0"
__author__ = "Marta Materni"


root_w = 1000
root_h = 600
root_x = 100
root_y = 100

log_w = 1000
log_h = 600
log_x = 200
log_y = 200


def pp(data, w=60):
    return pprint.pformat(data, width=w)


tfhlogerr = Log("w")

W_IDS = ['wmerge',
         'wcheckover',
         'wchecktxt',
         'wtxt',
         'wsetid',
         'wover',
         'wnote',
         'wformat',
         'wall',
         'wremovelog'
         ]

T_IDS = ['tcheckover',
         'tchecktxt',
         'ttxt',
         'tsetid',
         'tover',
         'tnote',
         'tformat',
         'tall',
         'tremovelog']

TEIMFH_LOG_ERR = "log/teimxmlh.ERR.log"


class TeimXmlFh(object):
    """
    Gestisce in modalità grafica un progetto
    """

    def __init__(self, prj_name=None):
        # atexit.register(self.all_done)
        self.prj_name = prj_name
        #######################
        # si posiziona nella di prj_dir
        self.tprmap = TeimPrjMap()
        run_pos=self.tprmap.check_prj_dir(prj_name)
        if run_pos == 0:
            print(f"Project {self.prj_name} Not Found.")
            sys.exit(0)
            return
        prj_dir = self.tprmap.prj_dir
        if run_pos == 2:
            os.chdir(prj_dir)
        print(self.tprmap.prj_dir)
        #######################
        self.tprmap.main(prj_name)
        #######################
        path_err = pth.Path().joinpath(prj_dir, TEIMFH_LOG_ERR)
        tfhlogerr.open(ptu.path2str(path_err), 1)
        self.pwd = ptu.cwd()
        ##################
        self.root = None
        self.txt_root = None
        self.wlog = None
        self.txt_log = None
        ###################
        # menu dinamici
        self.mv_witness = {}
        self.mv_text = None
        self.mv_prj_text = None
        self.mv_prj_witness = None
        #################
        self.witness_name = ""
        self.text_name = ""
        self.witness_cmds = []
        self.text_cmds = []

        self.lbl_prj_var = {}
        self.lbl_witness_var = {}
        self.lbl_text_var = None

    # def all_done(self):
    #     print("aaa")

    # nome del prj selezionato
    def set_prj(self):
        self.prj_name = self.tprmap.prj_name
        self.add_menu_witness()
        lbl = f"prj:  {self.prj_name}"
        self.lbl_prj_var.set(lbl)

    # XXX menu per la selezione del witness
    def add_menu_witness(self):
        names = self.tprmap.witness_name_lst
        self.mv_witness.delete(1, 10)
        for name in names:
            self.mv_witness.add_command(
                label=name,
                command=lambda x=name: self.set_witness(x))
        self.mv_witness.add_separator()

    # setta i comandi relativi al witness selezionato
    def set_witness(self, witness_name):
        self.witness_name = witness_name
        lbl = f"witness:  {witness_name}"
        self.lbl_witness_var.set(lbl)
        self.add_menu_prj_witness()
        self.add_menu_text()
        self.text_name = None

    # menu per la selezione del text di un witness
    def add_menu_text(self):
        wt_names = self.tprmap.witness_text_name_lst
        names = []
        for wt in wt_names:
            w, t = wt
            if w == self.witness_name:
                names.append(t)
        self.mv_text.delete(1, 10)
        for name in names:
            self.mv_text.add_command(
                label=name,
                command=lambda x=name: self.set_text(x))
        self.mv_text.add_separator()

    # setta i comandi relativi al witness e text selezionato
    def set_text(self, text_name):
        #print(f"set_text {text_name}")
        self.text_name = text_name
        lbl = f"text:  {text_name}"
        self.lbl_text_var.set(lbl)
        self.add_menu_prj_text(text_name)

    # XXX setta il menu witness command
    def add_menu_prj_witness(self):
        lst = self.tprmap.cmd_lst[self.witness_name]
        rows = []
        for wid in W_IDS:
            s = f"{self.witness_name}_{wid[1:]}"
            for tc in lst:
                text, cmd = tc
                text = text.replace('.json', '')
                if s == text:
                    rows.append([wid, text, cmd])
                    break
                if wid == 'wall' and text == self.witness_name:
                    rows.append([wid, text, cmd])
        self.witness_cmds = rows

        self.mv_prj_witness.delete(1, 10)
        for row in self.witness_cmds:
            id, lbl, cmd = row
            self.mv_prj_witness.add_command(
                label=lbl,
                command=lambda x=id: self.exe_prj_witness(x))
        self.mv_prj_witness.add_separator()

    # XXX setta il menu text command
    def add_menu_prj_text(self, text_name):
        if self.witness_name is None:
            return
        wtn_name = self.witness_name
        lst = self.tprmap.txt_cmd_lst[wtn_name][text_name]
        # print(f'wtn_name:{wtn_name}  text_name:{text_name}')
        # print(f'txt_cmds:{pp(self.tpr.txt_cmds,40)}')
        # print(f'txt_cmds[wtn_name]:{pp(self.tpr.txt_cmds[wtn_name],40)}')
        # print(f'txt_cmds[wtn_name]:{lst.txt_cmds[wtn_name]}')
        rows = []
        for tid in T_IDS:
            s = f"{text_name}_{tid[1:]}"
            for tc in lst:
                text, cmd = tc
                text = text.replace('.json', '')
                # print(s,text)
                if s == text:
                    rows.append([tid, text, cmd])
                    break
                if tid == 'tall' and text == text_name:
                    rows.append([tid, text, cmd])
        self.text_cmds = rows
        self.mv_prj_text.delete(1, 10)
        for row in self.text_cmds:
            id, lbl, cmd = row
            self.mv_prj_text.add_command(label=lbl,
                                         command=lambda x=id: self.exe_prj_text(x))
        self.mv_prj_text.add_separator()

    # XXX esegue il comando con prjmgr
    def exe_prj_witness(self, idx):
        if self.witness_name is None:
            return
        for x in self.witness_cmds:
            id, text, json_path = x
            if id == idx:
                print(f'A {text}')
                pm = PrjMgr()
                pm.parse_file(json_path)
                break

    # XXX esegue comando text
    def exe_prj_text(self, idx):
        if self.witness_name is None:
            self.mbox.showinfo("Select witness")
            return
        if not self.text_name:
            return
        for x in self.text_cmds:
            id, text, json_path = x
            if id == idx:
                print(f'A {text}')
                pm = PrjMgr()
                pm.parse_file(json_path)
                break

    # backup dei testi
    def backup_text(self):
        prj_name = self.prj_name
        if prj_name is None:
            return
        path = self.tprmap.prj_dir
        # print(path)
        os.chdir(path)
        save_text()
        os.chdir(self.pwd)

    # XXX aggiorna il progetto all'aggiunta di un testo
    def make_prj_text(self):
        if not self.prj_name:
            return
        for wtn_name in self.tprmap.witness_name_lst:
            do_main_prj_text(self.prj_name, wtn_name)
        self.tprmap.main(self.prj_name)
        if self.witness_name:
            self.add_menu_text()

    def file_prj_list(self):
        path_s = self.tprmap.prj_dir
        path_p = ptu.str2path(path_s)
        wtn_lst = self.tprmap.witness_name_lst
        path_p_lst = []
        name_s_lst = []
        for wtn in wtn_lst:
            path_wtn = ptu.join(path_p, wtn)
            rlst = ptu.rlist_path(path_wtn, "*.*")
            for x in rlst:
                path_file = pth.Path(x).relative_to(path_p)
                path_p_lst.append(path_file)
                s = ptu.path2str(path_file)
                name_s_lst.append(s)

        def load_file(n):
            if n < 0:
                return
            path = path_p_lst[n]
            try:
                with path.open('r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                msg = f'load_file() {path} Not Found'
                tfhlogerr.log(msg)
                return
            self.txt_root.delete("1.0", tk.END)
            self.txt_root.insert("1.0", text)
        open_listbox(name_s_lst, load_file)

    def file_witness_list(self):
        wtn = self.witness_name
        if len(wtn) < 1:
            mbox.showinfo("", "Select WItness")
            return
        path_s = self.tprmap.prj_dir
        path_p = ptu.str2path(path_s)
        path_wtn = ptu.join(path_s, wtn)
        path_p_lst = []
        name_s_lst = []
        rlst = ptu.rlist_path(path_wtn, "*.*")
        for x in rlst:
            path_file = pth.Path(x).relative_to(path_p)
            path_p_lst.append(path_file)
            s = ptu.path2str(path_file)
            name_s_lst.append(s)

        def load_file(n):
            if n < 0:
                return
            path = path_p_lst[n]
            try:
                with path.open('r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                msg = f'load_file() {path} Not Found'
                tfhlogerr.log(msg)
                return
            self.txt_root.delete("1.0", tk.END)
            self.txt_root.insert("1.0", text)
        open_listbox(name_s_lst, load_file)

    def cmd(self):
        pass

    def add_bottom_bar(self):

        def new_label(str_var, col):
            lbl = tk.Label(bottom_bar,
                           pady=5,
                           textvariable=str_var,
                           fg=FG_BOTTOM_LBL,
                           bg=BG_BOTTOM,
                           font=FONT_BOTTOM)
            lbl.grid(row=0,
                     column=col,
                     sticky='sw',
                     padx=10,
                     pady=5)
            return lbl

        bottom_bar = tk.Frame(self.root)
        bottom_bar.config(height=30,
                          bg=BG_BOTTOM,
                          bd=0)
        bottom_bar.grid(row=1,
                        column=0,
                        sticky='swe',
                        padx=0,
                        pady=0)
        self.lbl_prj_var = tk.StringVar()
        self.lbl_prj_var.set("prj:")
        new_label(self.lbl_prj_var, 0)

        self.lbl_witness_var = tk.StringVar()
        self.lbl_witness_var.set("witness:")
        new_label(self.lbl_witness_var, 2)

        self.lbl_text_var = tk.StringVar()
        self.lbl_text_var.set("text:")
        new_label(self.lbl_text_var, 4)

    def open_root(self):

        def new_mv(mb):
            mv = tk.Menu(menu_bar, tearoff=0)
            mv.config(font=FONT_MENU,
                      bg=BG_MENU,
                      fg=FG_MENU,
                      activebackground=BG2_MENU,
                      activeforeground=FG2_MENU,
                      relief=tk.SOLID)
            mv.add_separator()
            return mv

        self.root = tk.Tk()
        self.root.title("TeimXmlFh")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.geometry('%dx%d+%d+%d' % (root_w, root_h, root_x, root_y))
        self.root.config(background=BG_WIN, pady=2)
        self.root.protocol("WM_DELETE_WINDOW", lambda: False)

        self.txt_root = TextPad(self.root)
        self.txt_root.focus_set()
        self.txt_root.grid(row=0, column=0, sticky="nwes")

        self.add_bottom_bar()

        menu_bar = tk.Menu(self.root, tearoff=0)
        menu_bar.config(font=FONT_MENU,
                        bg=BG_MENU,
                        fg=FG_MENU,
                        activebackground=BG2_MENU,
                        activeforeground=FG2_MENU,
                        bd=2,
                        relief=tk.SOLID)
        self.root.config(menu=menu_bar)
        self.root.bind("<Control-q>", self.app_quit)

        self.mv_witness = new_mv(menu_bar)
        self.mv_text = new_mv(menu_bar)
        self.mv_prj_text = new_mv(menu_bar)
        self.mv_prj_witness = new_mv(menu_bar)
        mv_utils = new_mv(menu_bar)
        mv_utils.add_command(label='Add Text', command=self.make_prj_text)
        mv_utils.add_command(label='Backup Text', command=self.backup_text)
        mv_utils.add_command(label='Prn ids', command=self.cmd)
        mv_utils.add_command(label='Popup', command=self.cmd)
        mv_utils.add_command(label='Cmd', command=self.cmd)

        mv_list = new_mv(menu_bar)
        mv_list.add_command(label='Prj Files', command=self.file_prj_list)
        mv_list.add_command(label='Witness Files',
                            command=self.file_witness_list)

        # orizontale
        menu_bar.add_cascade(label='Witness', menu=self.mv_witness)
        menu_bar.add_cascade(label='Text', menu=self.mv_text)
        menu_bar.add_cascade(label='Prj Text', menu=self.mv_prj_text)
        menu_bar.add_cascade(label='Prj Witness', menu=self.mv_prj_witness)
        menu_bar.add_cascade(label='List Files', menu=mv_list)
        menu_bar.add_cascade(label='Utils', menu=mv_utils)
        menu_bar.add_command(label='              ')
        menu_bar.add_command(label='Quit',
                             command=self.app_quit,
                             underline=0,
                             background=BG_MENU_LBL,
                             foreground=FG_MENU_LBL,
                             activebackground=BG2_MENU_LBL,
                             activeforeground=FG2_MENU_LBL)
        # self.show_wlog("")
        ######################
        self.set_prj()
        #####################
        tk.mainloop()

    # UA gestione log
    # def top_wroot(self):
    #     self.top_not()
    #     self.root.attributes("-topmost", True)

    def top_wlog(self):
        # self.wlog.lift()
        self.top_not()
        self.wlog.attributes("-topmost", True)

    def top_not(self):
        self.root.attributes("-topmost", False)
        self.wlog.attributes("-topmost", False)

    def top_order(self):
        self.top_not()
        self.root.lift()

    def iconify(self):
        self.root.iconify()
        self.wlog.iconify()

    def open_wlog(self):
        if self.wlog is not None:
            return
        self.wlog = tk.Tk()
        self.wlog.protocol("WM_DELETE_WINDOW", lambda: False)
        self.wlog.title('LOG')
        self.wlog.rowconfigure(0, weight=1)
        self.wlog.columnconfigure(0, weight=1)
        self.wlog.geometry('%dx%d+%d+%d' % (log_w, log_h, log_x, log_y))
        self.txt_log = TextPad(self.wlog)
        self.txt_log.grid(sticky='nsew')
        self.txt_log.configure(font=FONT_LOG, bg=BG_LOG, fg=FG_LOG)

    def quit_lgo(self):
        self.wlog.destroy()
        #self.wlog = None

    def show_wlog(self, s):
        s = '' if s is None else s
        self.open_wlog()
        self.txt_log.delete('1.0', tk.END)
        self.txt_log.insert('1.0', s)

    def app_quit(self, *args):
        self.root.quit()
        if self.wlog is not None:
            self.wlog.quit()

def do_main(prj_name=''):
    tme = TeimXmlFh(prj_name)
    tme.open_root()

if __name__ == '__main__':
    arg = sys.argv[1:]
    if len(arg) < 1:
        do_main("")
    else:
        do_main(arg[0])
