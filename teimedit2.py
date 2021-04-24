#!/usr/bin/env python3
# coding: utf-8


from teimedlib.ualog import Log

from teimeditlib.textlinenumbers import TextLineNumbers
from teimeditlib.textpad import TextPad
from teimeditlib.listbox import open_listbox
from teimeditlib.constants import *

from teimxml import do_main as do_main_xml
from teimsetid import do_main as do_main_setid
from teimover import do_main as do_main_over
from teimnote import do_main as do_main_note
from checktxt import do_main as do_main_checktxt
from checkover import do_main as do_main_checkover
from teixml2txt import do_main as do_main_xml2txt

import tkinter as tk
#from tkinter.font import Font
import tkinter.filedialog as fdialog
import tkinter.messagebox as mbox

import pathlib as pth
import argparse
from lxml import etree
import stat
import sys
import os
import pprint
from pdb import set_trace

__date__ = "25-04-2021"
__version__ = "0.20.0"
__author__ = "Marta Materni"


def HELP_OPS():
    s = """
Crreazione Nuovo Progetto Default:
teimedit.py -p florimont       
=> florimont/teim.json
    florimont/cfg
    florimont/teim/log
    florimont/teim/teim.txt

Crreazione Progetto :
teimedit.py -p florimont -c paris.json -d paris -t eps01.txt -s J
=>  florimont/par1s.json
    florimont/cfg
    florimont/paris/log
    florimont/paris/eps01.txt

N.B, lanciare teimedit. nella dir del progetto
Aggiunta testo con creazione del file json:
teimedit.py -c tor.json -d tor -t eps01.txt -
=>  florimont/tor.json
    florimont/tor/log
    florimont/tor/eps01.txt

Lettura testo definito nel file json;
teimedit.py -r tor.json

Lettura di un testp NON definito nel file json
teimedit.py -r tor.json -t eps02.txt
        """
    return s


# TEXT_DIR='text_dir'
# TEXT_NAME='text_name'
# TEXT_SIGN='text_sign'
# LOG_DIR='log_dir'
# CFG_DIR='cfg_dir'

NOTE_CSV = 'note_csv'
TEIMED_CSV = 'teimed.csv'
OVERFLOW_CSV = 'overflow.csv'

dx = 100
dy = 100
w_w = 1000
w_h = 630

w0_w = w_w
w0_h = 600
w0_x = 100
w0_y = 100

w1_w = w_w
w1_h = w_h
w1_x = w0_x+dx
w1_y = w0_y+dy+30

w2_w = w_w
w2_h = w_h
w2_x = w1_x+dx
w2_y = w1_y+dy

w3_w = w_w
w3_h = w_h
w3_x = w2_x+dx
w3_y = w2_y+dy


def pp(data, w=60):
    return pprint.pformat(data, width=w)


logediterr = Log("w")


class TeimEdit(object):

    def __init__(self,
                 cfg_dir=None,
                 dir_search=None,
                 path_text=None,
                 text_sign="",):
        logediterr.open("log/teimedit.log", 1)
        self.cfg_dir = cfg_dir
        self.dir_search = dir_search
        self.path_text = path_text
        self.text_sign = text_sign

        self.text_dir = None
        self.log_dir = None

        self.pwd = pth.Path().cwd()
        self.path_entity_csv = None
        self.path_over_csv = None
        self.path_note_csv = None

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

        self.path_check_txt = None
        self.path_check_over = None

        self.path_text_txt = None
        self.path_text_err = None

        self.path_tmp = None
        #
        self.win0 = None
        self.text_edit = None
        self.win1 = None
        self.txt1 = None
        self.win2 = None
        self.txt2 = None
        self.win3 = None
        self.txt3 = None

#     mbox.showerror("Error", "Could not open file")
#     mbox.showwarning("Warning", "Deprecated function call")
#     mbox.askquestion("Question", "Are you sure to quit?")
#     mbox.showinfo("Information", "Download completed")
#     mbox.askyesno("Information", "Confirm?")

    def find_path_text(self, path):
        try:
            if self.dir_search is None:
                # self.dir_search=self.pwd
                self.dir_search = pth.Path("./")
            else:
                self.dir_search = pth.Path(self.dir_search)
            t_name = f"{path}"
            path_lst = []
            name_lst = []
            for x in self.dir_search.rglob(t_name):
                path_lst.append(x)
                # p=x.relative_to(self.pwd)
                name_lst.append(self.path2str(x))
            le = len(path_lst)
            if le == 0:
                mbox.showinfo("", f"{t_name}  Not Foud")
            elif le == 1:
                self.path_text = path_lst[0]
                self.set_path_files(self.path_text)
                self.read_text_file()
            else:
                def on_select(n):
                    self.path_text = path_lst[n]
                    self.set_path_files(self.path_text)
                    self.read_text_file()

                open_listbox(self.win0, name_lst, on_select)
            return
        except Exception as e:
            print(str(e))
            sys.exit()

    def set_path_files(self, path_text):
        try:
            if isinstance(path_text, str):
                self.path_text = pth.Path(path_text)
            self.text_dir = self.path_text.parent

            if self.cfg_dir is None:
                self.cfg_dir = pth.Path().joinpath(self.pwd, "cfg")
            else:
                if isinstance(self.cfg_dir, str):
                    self.cfg_dir = pth.Path(self.cfg_dir)

            self.log_dir = pth.Path().joinpath(self.text_dir, "log")
            # self.make_dir(self.text_dir)
            # self.make_dir(self.cfg_dir)
            self.make_dir(self.log_dir)

            self.path_entity_csv = pth.Path().joinpath(self.cfg_dir, TEIMED_CSV)
            self.path_over_csv = pth.Path().joinpath(self.cfg_dir, OVERFLOW_CSV)
            self.path_note_csv = pth.Path().joinpath(self.text_dir, NOTE_CSV)

            tnm = self.path_text.name

            # teim/teim.xml
            self.path_xml = self.path_text.with_name(
                tnm.replace(".txt", ".xml"))

            # teim/teim_F.xml
            self.path_xml_format = self.path_text.with_name(
                tnm.replace(".txt", "_F.xml"))

            # per la gestione dei log
            path_log = pth.Path().joinpath(self.log_dir, tnm)

            # teim/log/teim_MED.txt
            # teim/log/teim_MED.log
            # teim/log/teim_MED.ERR.log
            self.path_entity_txt = path_log.with_name(
                tnm.replace(".txt", "_MED.txt"))
            self.path_entity_log = path_log.with_name(
                tnm.replace(".txt", "_MED.log"))
            self.path_entity_err = path_log.with_name(
                tnm.replace(".txt", "_MED.ERR.log"))

            # teim/log/teim_WID.xml
            # teim/log/teim_WID.log
            # teim/log/teim_WID.ERR.log
            self.path_setid_xml = path_log.with_name(
                tnm.replace(".txt", "_WID.xml"))
            self.path_setid_log = path_log.with_name(
                tnm.replace(".txt", "_WID.log"))
            self.path_setid_err = path_log.with_name(
                tnm.replace(".txt", "_WID.ERR.log"))

            # teim/log/teim_OVER.xml
            # teim/log/teim_OVER.log
            # teim/log/teim_OVER.ERR.log
            self.path_over_xml = path_log.with_name(
                tnm.replace(".txt", "_OVER.xml"))
            self.path_over_log = path_log.with_name(
                tnm.replace(".txt", "_OVER.log"))
            self.path_over_err = path_log.with_name(
                tnm.replace(".txt", "_OVER.ERR.log"))

            # teim/log/teimCHECK_TXT.txt
            self.path_check_txt = path_log.with_name(
                tnm.replace(".txt", "_CHECK_TXT.txt"))

            # teim/log/teimCHECK_OVER.txt
            self.path_check_over = path_log.with_name(
                tnm.replace(".txt", "_CHECK_OVER.txt"))

            # teim/teim_text.txt
            # teim/log/teim_text.ERR.log
            self.path_text_txt = self.path_text.with_name(
                tnm.replace(".txt", "_text.txt"))
            self.path_text_err = path_log.with_name(
                tnm.replace(".txt", "_text.ERR.log"))

            self.path_tmp = pth.Path().joinpath(self.log_dir, 'tmp')

        except Exception as e:
            s = str(e)
            logediterr.log(f"ERROR set_path_fies")
            logediterr.log(s)
            sys.exit(1)

    def path2str(self, path):
        s = f"{path}"
        return s

    def make_dir(self, path_dir):
        if len(f"{path_dir}".strip()) == 0:
            return
        if not path_dir.exists():
            # def mkdir(self, mode=0o777, parents=False, exist_ok=False):
            path_dir.mkdir(mode=0o777)

    def chmod(self, path):
        if not path.exists():
            self.show_log(f"File {path} Not Exists")
            return
        try:
            #os.chmod(path, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)
            path.chmod(mode=0o777)
        except Exception as e:
            logediterr.log(f"ERROR File Not Found.")
            logediterr.log(str(e))
            self.show_log(f"File {path} Not Found.")
            self.top_w3()

    def write_file(self, path, text):
        # with open(path, 'w') as f:
        #     f.write(text)
        # self.chmod(path)
        # path.write_bytes(text.encode('utf-8')
        path.write_text(text)
        self.chmod(path)

    def read_file(self, path):
        # print(type(path))
        # set_trace()
        #s = open(path, 'rt').read()
        #s = path.read_text(path)
        with path.open('r', encoding='utf-8') as f:
            s = f.read()
        return s

    def open_win0(self):
        self.win0 = tk.Tk()
        self.win0.title("TeimEdit")
        #self.win0.rowconfigure(0, weight=1)
        #self.win0.columnconfigure(0, weight=1)
        self.win0.geometry('%dx%d+%d+%d' % (w0_w, w0_h, w0_x, w0_y))
        self.win0.config(background=BG_WIN, pady=2)
        #
        self.text_edit = TextLineNumbers(self.win0)
        self.text_edit.focus_set()
        self.win0.protocol("WM_DELETE_WINDOW", lambda: False)
        #
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
        #
        mv_file = tk.Menu(menu_bar, tearoff=0)
        mv_file.config(
            font=FONT_MENU,
            bg=BG_MENU,
            fg=FG_MENU,
            activebackground=BG2_MENU,
            activeforeground=FG2_MENU,
            relief="raised")
        mv_file.add_command(
            label='Reload', command=self.reload_text, underline=0)
        mv_file.add_command(label='Import text',
                            command=self.import_text, underline=0)
        mv_file.add_separator()
        mv_file.add_command(label='Open  Ctrl+O', command=self.open_text)
        mv_file.add_separator()
        mv_file.add_command(label='Save  Ctrl+S', command=self.save_text)
        mv_file.add_command(label='Save As.. Ctl-Shift-S',
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
        self.text_edit.bind("<Control-q>", sys.exit)
        #
        mv_edit = tk.Menu(menu_bar, tearoff=0)
        mv_edit.config(font=FONT_MENU,
                       bg=BG_MENU,
                       fg=FG_MENU,
                       activebackground=BG2_MENU,
                       activeforeground=FG2_MENU,
                       relief=tk.RAISED)
        mv_edit.add_command(label="Undo     Ctrl-Z")
        mv_edit.add_command(label="Redo     Ctrl-Shift-Z",
                            command=self.text_edit.on_redo)
        mv_edit.add_separator()
        mv_edit.add_command(label="Cut      Ctrl-X")
        mv_edit.add_command(label="Copy     Ctrl-C")
        mv_edit.add_command(label="Paste    Ctrl-V")
        #
        mv_check = tk.Menu(menu_bar, tearoff=0)
        mv_check.config(font=FONT_MENU,
                        bg=BG_MENU,
                        fg=FG_MENU,
                        activebackground=BG2_MENU,
                        activeforeground=FG2_MENU,
                        relief=tk.RAISED)
        mv_check.add_command(label='Check Entity', command=self.elab_checktxt)
        mv_check.add_command(label='Check Overflow',
                             command=self.elab_checkover)
        #
        mv_elab = tk.Menu(menu_bar, tearoff=0)
        mv_elab.config(font=FONT_MENU,
                       bg=BG_MENU,
                       fg=FG_MENU,
                       activebackground=BG2_MENU,
                       activeforeground=FG2_MENU,
                       relief=tk.RAISED)
        mv_elab.add_command(label='Elab. Entity', command=self.elab_teimxml)
        mv_elab.add_command(label='Elab. Set id', command=self.elab_teimsetid)
        mv_elab.add_command(label='Elab. Overflow', command=self.elab_teimover)
        mv_elab.add_command(label='Elab. Note', command=self.elab_teimnote)
        mv_elab.add_separator()
        mv_elab.add_command(label='XML => text', command=self.elab_xml2txt)
        #
        mv_log = tk.Menu(menu_bar, tearoff=0)
        mv_log.config(font=FONT_MENU,
                      bg=BG_MENU,
                      fg=FG_MENU,
                      activebackground=BG2_MENU,
                      activeforeground=FG2_MENU,
                      relief=tk.RAISED)
        mv_log.add_command(label='Check Txt Err.', command=self.show_check_txt)
        mv_log.add_command(label='Check Over Err.',
                           command=self.show_check_over)
        mv_log.add_separator()
        mv_log.add_command(label='Entity Log.', command=self.show_entity_log)
        mv_log.add_command(label='Entity Err.', command=self.show_entity_err)
        mv_log.add_separator()
        mv_log.add_command(label='Set id Log.', command=self.show_setwid_log)
        mv_log.add_command(label='set id Err.', command=self.show_setwid_err)
        mv_log.add_separator()
        mv_log.add_command(label='Over Log.', command=self.show_over_log)
        mv_log.add_command(label='Over Err.', command=self.show_over_err)
        mv_log.add_separator()
        mv_log.add_command(label='*_text_.txt', command=self.show_text_txt)
        mv_log.add_command(label='XML => text ERR',
                           command=self.show_text_txt_err)
        mv_log.add_separator()
        mv_log.add_command(label='Read Log.', command=self.open_log)
        #
        mv_del = tk.Menu(menu_bar, tearoff=0)
        mv_del.config(font=FONT_MENU,
                      bg=BG_MENU,
                      fg=FG_MENU,
                      activebackground=BG2_MENU,
                      activeforeground=FG2_MENU,
                      relief=tk.RAISED)
        mv_del.add_command(label='Entity', command=self.delete_txt1)
        mv_del.add_command(label='XML', command=self.delete_txt2)
        mv_del.add_command(label='Log.', command=self.delete_txt3)
        mv_del.add_command(label='All', command=self.delete_txt_all)
        mv_del.add_separator()
        mv_del.add_command(label='Remove log file', command=self.remove_log)
        #
        mv_help = tk.Menu(menu_bar, tearoff=0)
        mv_help.config(font=FONT_MENU,
                       bg=BG_MENU,
                       fg=FG_MENU,
                       activebackground=BG2_MENU,
                       activeforeground=FG2_MENU,
                       relief=tk.RAISED)
        mv_help.add_command(label='Progect', command=self.show_info)
        mv_help.add_command(label='options', command=self.show_options)
        # orizontale
        menu_bar.add_cascade(label='File', menu=mv_file, underline=0)
        menu_bar.add_cascade(label='Edit', menu=mv_edit, underline=0)
        menu_bar.add_cascade(label='Check', menu=mv_check, underline=0)
        menu_bar.add_cascade(label='Elab.', menu=mv_elab, underline=1)
        menu_bar.add_cascade(label='Log.', menu=mv_log, underline=0)
        menu_bar.add_cascade(label='Del.', menu=mv_del, underline=0)
        menu_bar.add_command(label='    1-2-3-4 ', command=self.top_order)
        menu_bar.add_command(label=' 1 ', command=self.top_w0)
        menu_bar.add_command(label=' 2 ', command=self.top_w1)
        menu_bar.add_command(label=' 3 ', command=self.top_w2)
        menu_bar.add_command(label=' 4 ', command=self.top_w3)
        menu_bar.add_command(label="                ",
                             activebackground=BG_MENU),
        menu_bar.add_cascade(label='Help', menu=mv_help)
        #text = self.config['text_name']
        self.show_win1("")
        self.show_win2("")
        self.show_win3("")
        ############
        # invoca
        # set_file_path
        # read_text_file
        self.find_path_text(self.path_text)
        # self.set_path_files(self.path_text)
        # self.read_text_file()
        ############

        ##############
        tk.mainloop()
        ##############

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
        self.top_not()
        self.win3.attributes("-topmost", True)

    def top_not(self):
        self.win0.attributes("-topmost", False)
        self.win1.attributes("-topmost", False)
        self.win2.attributes("-topmost", False)
        self.win3.attributes("-topmost", False)

    def top_order(self):
        self.top_not()
        return
        # self.win0.attributes("-topmost", 1)
        # self.win1.attributes("-topmost", 2)
        # self.win2.attributes("-topmost", 3)
        # self.win3.attributes("-topmost", 4)

    ##########################
    # mv_file
    ########################
    def reload_text(self):
        self.read_text_file()

    def import_text(self):
        self.top_order()
        wrk_dir = os.getcwd()
        path_read = fdialog.askopenfilename(
            title=' file',
            initialdir=wrk_dir,
            filetypes=[("text", "*.txt")])
        if len(path_read) < 1:
            return
        s = open(path_read, "r").read()
        self.text_edit.insert_text(s)

    def open_text(self, *args):
        self.top_order()
        path = fdialog.askopenfilename(
            title=' file',
            initialdir=self.text_dir,
            filetypes=[("text", "*.txt"),
                       ("*.*", "*.*")])
        if len(path) < 1:
            return
        # if not os.path.exists(path):
        if not pth.Path(path).exists:
            return
        self.set_path_files(path)
        self.read_text_file()

    def save_text(self, *args):
        s = self.get_text()
        self.write_file(self.path_text, s)

    def save_text_as(self, *args):
        self.top_order()
        path = fdialog.asksaveasfilename(title='Salva as Name',
                                         initialdir=self.text_dir)
        if len(path) < 1:
            return ""
        text = self.get_text()
        self.set_path_files(path)
        self.write_file(self.path_text, text)
        title = f"TEXT: {path} "
        self.win0.title(title)

    def app_quit(self):
        self.top_not()
        yn = mbox.askyesno("", "Quit ?", parent=self.win0)
        if not yn:
            return
        self.win0.quit()
        if self.win1 is not None:
            self.win1.quit()
        if self.win2 is not None:
            self.win2.quit()
        if self.win3 is not None:
            self.win3.quit()

    ##########################
    # mv_edit su editore
    ##########################

    #################
    # mv_check
    ################
    def elab_checktxt(self):
        s = self.get_text()
        self.write_file(self.path_tmp, s)
        # def do_main(path_src, path_out):
        do_main_checktxt(self.path2str(self.path_tmp),
                         self.path2str(self.path_check_txt))
        self.chmod(self.path_check_txt)
        s = self.read_file(self.path_check_txt)
        self.show_win3(s)

    def elab_checkover(self):
        s = self.get_text()
        self.write_file(self.path_tmp, s)
        # def do_main(path_src, path_csv, path_out):
        do_main_checkover(self.path2str(self.path_tmp),
                          self.path2str(self.path_over_csv),
                          self.path2str(self.path_check_over))
        self.chmod(self.path_check_over)
        s = self.read_file(self.path_check_over)
        self.show_win3(s)

    #############
    # mv_elab
    #############
    def elab_teimxml(self):
        s = self.get_text()
        self.write_file(self.path_text, s)
        try:
            do_main_xml(self.path2str(self.path_text),
                        self.path2str(self.path_entity_csv),
                        self.path2str(self.path_entity_txt))
        except SystemExit as e:
            logediterr.log(str(e))
            s = f"ERROR Elab entity{str(e)} {os.linesep}"
            self.show_log(s, True)
            #self.top_w3()
            mbox.showerror("", "In elab. entity")
            return
        self.chmod(self.path_entity_txt)
        s = self.read_file(self.path_entity_txt)
        self.show_win1(s)
        ls = ["    Elab. entity",
              f"{self.path_text}",
              f"{self.path_entity_csv}",
              f"{self.path_entity_txt}"]
        self.show_log(os.linesep.join(ls), True)

    def elab_teimsetid(self):
        if not self.path_entity_txt.exists():
            self.show_log("Call Elab. Entity")
            #self.top_w3()
            mbox.showwarning("", "Elab. Entity")
            return
        # path_txt_1 => path_xml_1
        try:
            do_main_setid(self.path2str(self.path_entity_txt),
                          self.path2str(self.path_setid_xml),
                          self.text_sign)
        except SystemExit as e:
            logediterr.log(str(e))
            s = f"Errro in set id{str(e)} {os.linesep}"
            self.show_log(s, True)
            #self.top_w3()
            mbox.showerror("", f" set id {str(e)}")
            return
        self.chmod(self.path_setid_xml)
        ls = ["    Elab. Set id",
              f"{self.path_entity_txt}",
              f"{self.path_setid_xml}",
              f"{self.text_sign}"]
        self.show_log(os.linesep.join(ls), True)

    def elab_teimover(self):
        if not self.path_setid_xml.exists():
            mbox.showwarning("", f"Call Elab. set_id")
            #self.top_w3()
            self.show_log("Elaborare Set id o vi è stato un errore")
            return
        # path_xml_1 => path_xml_2
        try:
            # def do_main(src_path, out_path, csv_path):
            do_main_over(self.path2str(self.path_setid_xml),
                         self.path2str(self.path_over_xml),
                         self.path2str(self.path_over_csv))
        except SystemExit as e:
            logediterr.log(str(e))
            s = f"Elaborare overflow {str(e)} {os.linesep}"
            self.show_log(s, True)
            #self.top_w3()
            mbox.showerror("", f"Elab. overflow")
            return
        self.chmod(self.path_over_xml)
        ls = ["    Eelab. overflow",
              f"{self.path_setid_xml}",
              f"{self.path_over_xml}",
              f"{self.path_over_csv}"]
        self.show_log(os.linesep.join(ls), True)

    def elab_teimnote(self):
        if not self.path_over_xml.exists():
            self.show_log("Elaborare Over id o vi è stato un errore")
            mbox.showwarning("", f"Call Elab. overflow")
            #self.top_w3()
            return
        # path_xml_2 => path_xml
        try:
            # def do_main(src_path, out_path, note_path):
            do_main_note(self.path2str(self.path_over_xml),
                         self.path2str(self.path_xml),
                         self.path2str(self.path_note_csv))
        except SystemExit as e:
            logediterr.log(str(e))
            s = f"Elaborare note {str(e)} {os.linesep}"
            self.show_log(s, True)
            #self.top_w3()
            mbox.showerror("", f"Elab. note")
            return
        self.chmod(self.path_xml)
        ls = ["    Elab. Note",
              f"{self.path_over_xml}",
              f"{self.path_xml}",
              f"{self.path_note_csv}"]
        self.show_log(os.linesep.join(ls), True)
        self.format_xml()

    def elab_xml2txt(self):
        if not self.path_xml.exists():
            self.show_log("Elaborare XML")
            #self.top_w3()
            mbox.showwarning("", f"Call Elab. XML")
            return
        # path_xml => path_text_txt
        try:
            do_main_xml2txt(self.path2str(self.path_xml),
                            self.path2str(self.path_text_txt))
        except SystemExit as e:
            logediterr.log(str(e))
            s = f"ERROR Elab. note {str(e)} {os.linesep}"
            self.show_log(s, True)
            #self.top_w3()
            mbox.showerror("", f"Elab. XML")
            return
        self.chmod(self.path_xml)
        ls = ["    XML => text",
              f"{self.path_xml}",
              f"{self.path_text_txt}"]
        self.show_log(os.linesep.join(ls), True)

    def format_xml(self):
        s = self.read_file(self.path_xml)
        xml = '<div>'+s+'</div>'
        self.write_file(self.path_tmp, xml)
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            path = self.path2str(self.path_tmp)
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
            s = f"ERROR.  XML {os.linesep}{str(e)}"
            self.show_log(s)
            #self.top_w3()
            mbox.showerror("", f"parser XML")

    ##############
    # mv_del
    ##############
    def delete_txt_all(self):
        # self.txt0.delete('1.0', tk.END)
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
        for f in self.log_dir.iterdir():
            absp = f.absolute()
            print(absp)
            os.remove(absp)

    ##############
    # mv_log
    ##############

    # teim/log/teimCHECK_TXT.txt
    def show_check_txt(self):
        self.read_log_file(self.path_check_txt)

    # teim/log/teimCHECK_OVER.txt
    def show_check_over(self):
        self.read_log_file(self.path_over_xml)

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

    # teim/log/teim_text.txt
    def show_text_txt(self):
        self.read_log_file(self.path_text_txt)

    # TODO teim/log/teim_text.ERR.log
    def show_text_txt_err(self):
        self.read_log_file(self.path_text_err)

    def open_log(self):
        self.top_order()
        path = fdialog.askopenfilename(
            title='log',
            initialdir=self.log_dir,
            filetypes=[("all", "*.*"),
                       ("log", "*.log"),
                       ("text", "*.txt"),
                       ("xml", "*.xml")])
        if len(path) < 0:
            return
        # if not os.path.exists(path):
        path = pth.Path(path)
        if not path.exists:
            s = self.read_file(path)
        else:
            s = "Not Found."
        self.top_w3()
        self.txt3.delete('1.0', tk.END)
        self.txt3.insert('1.0', s)

    #############
    # menu_bar
    ############
    def show_info(self):
        #abs_cfg = os.path.abspath(str(self.cfg_dir))
        #abs_text = os.path.abspath(str(self.text_dir))
        wrk_dir = self.pwd
        info = [
            "---------------------------",
            f"work dir  : {wrk_dir}  ",
            "---------------------------",
            f" tei_tags : {self.path_entity_csv}",
            f" over_tags: {self.path_over_csv}",
            f" text dir : {self.text_dir}",
            f" text     : {self.path_text}",
            f" sigla    : {self.text_sign}",
            f" note     : {self.path_note_csv}",
            "---------------------------",
            "Lof",
            "---------------------------",
            f"chek  txt   : {self.path_check_txt}",
            f"check over  : {self.path_check_over}",
            f"elab  entity: {self.path_entity_txt}",
            f"elab  set id: {self.path_setid_xml}",
            f"elab  over  : {self.path_over_xml}",
            f"elab  note  : {self.path_xml}",
            "---------------------------",
            " ",
        ]
        s = os.linesep.join(info)
        self.show_win3(s)
        self.top_w3()

    def show_options(self):
        s = HELP_OPS()
        self.show_win3(s)
        self.top_w3()

    ############

    def get_text(self):
        s = self.text_edit.get('1.0', 'end')
        return s.strip()

    def read_text_file(self):
        if self.path_text.exists():
            #s = self.read_file(self.path_text)
            s = self.read_file(self.path_text)
        else:
            self.write_file(self.path_text, "Empty")
            r = ["", f"File  {self.path_text} Not Found.",
                 "", f"Crated {self.path_text} empyt."]
            s = os.linesep.join(r)
        self.text_edit.insert_text(s)
        # show_title
        title = f"TEXT: {self.path_text} "
        self.win0.title(title)

    def read_log_file(self, path):
        if path.exists():
            #s = path.read_text()
            s = self.read_file(path)
        else:
            s = f"{path}   Not Found."
        self.top_w3()
        self.txt3.delete('1.0', tk.END)
        self.txt3.insert('1.0', s)

    def show_log(self, msg, append=False):
        if append:
            x = self.txt3.get('1.0', 'end')
            msg = f"{x}{msg}{os.linesep}"
        else:
            msg = f"{msg}{os.linesep}"
        self.txt3.delete('1.0', tk.END)
        self.txt3.insert('1.0', msg)

   #########################

    def open_win1(self):
        if self.win1 is not None:
            return
        self.win1 = tk.Tk()
        self.win1.title('ENTITY')
        self.win1.protocol("WM_DELETE_WINDOW", lambda: False)
        self.win1.rowconfigure(0, weight=1)
        self.win1.columnconfigure(0, weight=1)
        self.win1.geometry('%dx%d+%d+%d' % (w1_w, w1_h, w1_x, w1_y))
        self.txt1 = TextPad(self.win1)
        self.txt1.grid(sticky='nsew')

    def open_win2(self):
        if self.win2 is not None:
            return
        self.win2 = tk.Tk()
        self.win2.title('XML')
        self.win2.protocol("WM_DELETE_WINDOW", lambda: False)
        self.win2.rowconfigure(0, weight=1)
        self.win2.columnconfigure(0, weight=1)
        self.win2.geometry('%dx%d+%d+%d' % (w2_w, w2_h, w2_x, w2_y))
        self.txt2 = TextPad(self.win2)
        self.txt2.grid(sticky='nsew')

    def open_win3(self):
        if self.win3 is not None:
            return
        self.win3 = tk.Tk()
        self.win3.protocol("WM_DELETE_WINDOW", lambda: False)
        self.win3.title('LOG')
        self.win3.rowconfigure(0, weight=1)
        self.win3.columnconfigure(0, weight=1)
        self.win3.geometry('%dx%d+%d+%d' % (w3_w, w3_h, w3_x, w3_y))
        self.txt3 = TextPad(self.win3)
        self.txt3.grid(sticky='nsew')
        self.txt3.configure(font=FONT_LOG, bg=BG_LOG, fg=FG_LOG)

    def quit1(self):
        self.win1.destroy()
        self.win1 = None

    def show_win1(self, s):
        self.open_win1()
        self.txt1.delete('1.0', tk.END)
        self.txt1.insert('1.0', s)

    def quit2(self):
        self.win2.destroy()
        self.win2 = None

    def show_win2(self, s):
        self.open_win2()
        self.txt2.delete('1.0', tk.END)
        self.txt2.insert('1.0', s)

    def quit3(self):
        self.win3.destroy()
        self.win3 = None

    def show_win3(self, s):
        self.open_win3()
        self.txt3.delete('1.0', tk.END)
        self.txt3.insert('1.0', s)


def do_main(cfg_dir, dir_search, path_text, sign):
    tme = TeimEdit(cfg_dir, dir_search, path_text, sign)
    tme.open_win0()


def prn_help():
    print(HELP_OPS())

# if __name__ == "__main__":
#     do_main("cfg", None, "txt/par1/txt/prol1.txt", "K")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    le = len(sys.argv)
    if le == 1:
        print("")
        print(f"author: {__author__}")
        print(f"release: {__version__} { __date__}")
        print("")
        # parser.print_help()
        sys.exit()
    parser.add_argument('-c',
                        dest="cfg",
                        required=False,
                        default="cfg",
                        metavar="directory cfg",
                        help="[-c <cfg>]")
    parser.add_argument('-d',
                        dest="dsearch",
                        required=False,
                        default=None,
                        metavar="direcory text search",
                        help="[-d <search_dir>]")
    parser.add_argument('-t',
                        dest="txt",
                        required=True,
                        default="",
                        metavar="text name",
                        help="[-t <file>.txt]")
    parser.add_argument('-s',
                        dest="sign",
                        required=False,
                        default="K",
                        metavar="text_sign",
                        help="[-s <sign>]")
    parser.add_argument('-e',
                        action="store_true",
                        required=False,
                        help="[-e  print examples]")
    args = parser.parse_args()
    if args.e:
        prn_help()
        sys.exit()
    do_main(args.cfg, args.dsearch, args.txt, args.sign)
