#!/usr/bin/env python3
# coding: utf-8

from pdb import set_trace

import argparse
import os
#import pathlib as pth
import pprint
import sys
import tkinter as tk
import tkinter.filedialog as fdialog
import tkinter.messagebox as mbox

from lxml import etree

from checkover import do_main as do_main_checkover
from checktxt import do_main as do_main_checktxt

from teimedlib.edit_constants import *
from teimedlib.listbox import open_listbox
from teimedlib.textedit import TextEdit
from teimedlib.textpad import TextPad

from teimedlib.teim_constants import *
from teimedlib.ualog import Log
from teimedlib.findfile import find_match_files
import teimedlib.pathutils as pthu
import teimedlib.check_teimed as ckte

from teimnote import do_main as do_main_note
from teimover import do_main as do_main_over
from teimsetid import do_main as do_main_setid
from teimxml import do_main as do_main_xml
from teixml2txt import do_main as do_main_xml2txt

__date__ = "26-04-2021"
__version__ = "0.20.2"
__author__ = "Marta Materni"


def HELP_RUN_OPS():
    s = """
teimedit.py -c florimont -d paris -t eps*.txt -s K 

-c florimont (facoltativo)
cerca a partire dalla dir "florimont" "teimcfg"
se ne trova pià di uno mostra una lista per selezionare
se ne trova uno lo seleziona e procede
se non ne trova nessuno esce dall'applicazione

-d paris (facoltativo)
cerca a partire dalla direcorty "paris" tutti i testi 
che corrisondono al nome o alla wilcard dell'opzione -t
se ne trova pià di uno mostra una lista per selezionare
se ne trova un lo seleziona e procede
se non ne trova nessuno mosta un messaggio ed procede

-t eps*.txt 
nome del file o wilcrad dei files di testo da elaborare
i files sono cercati a partire dalla directory dell'opzione -d
se non é stata seleziona la ricerca parte dalla directory corrente.

-s K
sigla del manoscritto
        """
    return s


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
w3_x = w2_x+dx+100
w3_y = w2_y+dy

def pp(data, w=60):
    return pprint.pformat(data, width=w)

logediterr = Log("w")

class TeimEdit(object):

    def __init__(self,
                 dir_parent_teimcfg=None,
                 dir_parent_text=None,
                 path_text=None,
                 text_sign="",):
        """
        Args:
            dir_parent_teimcfg (str, optional): dir parent di teimcfg "".
            dir_parent_text (str, optional): dir parent del/dei file di testo.
            path_text ([type], optional): wilcard file/i di testo.
            text_sign (str, optional): sigla del manoscritto.
        """
        self.path_edit_err = pthu.str2path("log/teimedit.lo")
        logediterr.open(pthu.path2str(self.path_edit_err), 1)
        self.dir_parent_teimcfg = pthu.str2path(dir_parent_teimcfg)
        self.dir_parent_text = pthu.str2path(dir_parent_text)
        self.path_text = path_text
        self.text_sign = text_sign

        self.path_teimcfg = ""
        self.text_dir = None
        self.log_dir = None

        self.pwd = pthu.cwd()
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
        # variabili per gestione chek edit        
        self.tag_names = ['a', 'b']
        self.tag_num_debug = 0
        # TODO verificare se può essere chiamatio dopol lettutr cfg
        self.ptr_over = ckte.build_pattern_over()

        self.win0 = None
        self.text_edit = None
        self.win1 = None
        self.txt1 = None
        self.win2 = None
        self.txt2 = None
        self.win3 = None
        self.txt3 = None

    def find_teimtag(self):
        try:
            path_lst = find_match_files(self.dir_parent_teimcfg, TEIMCFG)
            name_lst = pthu.pathlist2strlist(path_lst)
            le = len(path_lst)
            if le == 0:
                self.iconify()
                mbox.showerror("", f"{TEIMCFG}  Not Foud")
                sys.exit()
            elif le == 1:
                self.path_teimcfg = path_lst[0]
                self.set_teimcfg_paths()
                self.find_file_text(self.path_text)
                self.win0.after(20, self.show_info())
            else:
                def on_select(n):
                    self.path_teimcfg = path_lst[n]
                    self.set_teimcfg_paths()
                    self.find_file_text(self.path_text)
                    self.win0.after(20, self.show_info())

                #open_listbox(self.win0, name_lst, on_select)
                open_listbox(name_lst, on_select)
            return
        except Exception as e:
            print(f"ERRO find_teimtags_cfg()s  {os.linesep}{e}")
            sys.exit()

    def find_file_text(self, path):
        try:
            match = f"{path}"
            path_lst = find_match_files(self.dir_parent_text, match)
            name_lst = pthu.pathlist2strlist(path_lst)
            le = len(path_lst)
            if le == 0:
                mbox.showinfo("", f"{match}  Not Foud")
            elif le == 1:
                self.path_text = path_lst[0]
                self.set_path_files(self.path_text)
                self.read_text_file()
                self.win0.after(20, self.show_info)
            else:
                def on_select(n):
                    self.path_text = path_lst[n]
                    self.set_path_files(self.path_text)
                    self.read_text_file()
                    self.show_info()

                #open_listbox(self.win0, name_lst, on_select)
                open_listbox(name_lst, on_select)
            return
        except Exception as e:
            s=f"{path} Not Found.{os.linesep}{e}"
            logediterr.log(s)
            print(s)
            sys.exit()

    def set_teimcfg_paths(self):
        try:
            self.path_entity_csv = pthu.join(self.path_teimcfg, TEIMTAGS_CSV)
            self.path_over_csv = pthu.join(self.path_teimcfg, TEIMOVERFLOW_CSV)
        except Exception as e:
            logediterr.log(f"ERROR set_teimcfg_paths. {e}")
            sys.exit(1)

    def set_path_files(self, path_text):
        try:
            self.path_text = pthu.str2path(path_text)
            self.text_dir = self.path_text.parent
            self.log_dir = pthu.join(self.text_dir, "log")
            pthu.make_dir(self.log_dir)
            self.path_teimnote = pthu.join(self.text_dir, TEIMNOTE_CSV)

            # teim/teim.xml
            self.path_xml = pthu.update_path_name(path_text, ".txt", ".xml")

            # teim/teim_format.xml
            self.path_xml_format = pthu.update_path_name(
                path_text, ".txt", "_format.xml")

            # temporaneo  per la gestione dei lfiles mella dir og
            t_name = self.path_text.name
            path_log = pthu.join(self.log_dir, t_name)

            # teim/log/teim_MED.txt
            # teim/log/teim_MED.log
            # teim/log/teim_MED.ERR.log
            self.path_entity_txt = pthu.update_path_name(
                path_log, ".txt", "_MED.txt")
            self.path_entity_log = pthu.update_path_name(
                path_log, ".txt", "_MED.log")
            self.path_entity_err = pthu.update_path_name(
                path_log, ".txt", "_MED.ERR.log")

            # teim/log/teim_WID.xml
            # teim/log/teim_WID.log
            # teim/log/teim_WID.ERR.log
            self.path_setid_xml = pthu.update_path_name(
                path_log, ".txt", "_WID.xml")
            self.path_setid_log = pthu.update_path_name(
                path_log, ".txt", "_WID.log")
            self.path_setid_err = pthu.update_path_name(
                path_log, ".txt", "_WID.ERR.log")

            # teim/log/teim_OVER.xml
            # teim/log/teim_OVER.log
            # teim/log/teim_OVER.ERR.log
            self.path_over_xml = pthu.update_path_name(
                path_log, ".txt", "_OVER.xml")
            self.path_over_log = pthu.update_path_name(
                path_log, ".txt", "_OVER.log")
            self.path_over_err = pthu.update_path_name(
                path_log, ".txt", "_OVER.ERR.log")

            # teim/log/teim_note.ERR.log
            self.path_note_err = pthu.update_path_name(
                path_log, ".txt", "_note.ERR.log")

            # teim/log/teimCHECK_TXT.txt
            self.path_check_txt = pthu.update_path_name(
                path_log, ".txt", "_CHECK_TXT.log")

            # teim/log/teimCHECK_OVER.txt
            self.path_check_over = pthu.update_path_name(
                path_log, ".txt", "_CHECK_OVER.log")

            # teim/teim_text.txt
            # teim/log/teim_text.ERR.log
            self.path_text_txt = pthu.update_path_name(
                path_text, ".txt", "_text.txt")
            self.path_text_err = pthu.update_path_name(
                path_log, ".txt", "_text.ERR..log")

            self.path_tmp = pthu.join(self.log_dir, 'tmp')
        except Exception as e:
            logediterr.log(f"ERROR set_path_fies.{e}")
            sys.exit(1)

    def chmod(self, path):
        try:
            pthu.chmod(path)
        except Exception as e:
            logediterr.log(f"File {path} Not Found.{os.linesep}{e}")
            self.show_log_top(f"File {path} Not Found.",True)

    def write_file(self, path, text):
        path.write_text(text)
        self.chmod(path)

    def read_file(self, path):
        if not path.exists():
            s = pthu.path2str(path)
            self.show_log_lift(f"{s} Not Found.",True)
            return
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
        self.text_edit = TextEdit(self.win0)
        self.text_edit.focus_set()
        self.win0.protocol("WM_DELETE_WINDOW", lambda: False)
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
        mv_file.add_command(label='Quit', command=self.app_quit_yn,
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

        mv_check = tk.Menu(menu_bar, tearoff=0)
        mv_check.config(font=FONT_MENU,
                        bg=BG_MENU,
                        fg=FG_MENU,
                        activebackground=BG2_MENU,
                        activeforeground=FG2_MENU,
                        relief=tk.RAISED)
        mv_check.add_command(label='Check Entity Log', command=self.elab_checktxt)
        mv_check.add_command(label='Check Overflow Log', command=self.elab_checkover)
        mv_check.add_separator()
        mv_check.add_command(label='Clean', command=self.del_tags)
        mv_check.add_separator()    
        mv_check.add_command(label='Entity Comma', command=self.fin_entity_comma)
        mv_check.add_command(label='Entity Brackets', command=self.find_entity_brackets)
        mv_check.add_separator()
        name,lbl=self.over_name_label('agglutination')
        mv_check.add_command(label=lbl, command=lambda n=name :self.find_over(n))
        name,lbl=self.over_name_label('agglutination_uncert')
        mv_check.add_command(label=lbl, command=lambda n=name:self.find_over(n))
        mv_check.add_separator()
        name,lbl=self.over_name_label('damage_low')
        mv_check.add_command(label=lbl, command=lambda n=name:self.find_form_to(n))
        name,lbl=self.over_name_label('damage_medium')
        mv_check.add_command(label=lbl, command=lambda n=name:self.find_form_to(n))
        name,lbl=self.over_name_label('damage_high')
        mv_check.add_command(label=lbl, command=lambda n=name:self.find_form_to(n))
        mv_check.add_separator()
        name,lbl=self.over_name_label('directspeech')
        mv_check.add_command(label=lbl, command=lambda n=name:self.find_form_to(n))
        name,lbl=self.over_name_label('monologue')
        mv_check.add_command(label=lbl, command=lambda n=name:self.find_form_to(n))

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
        mv_elab.add_separator()
        mv_elab.add_command(label='Reload XML', command=self.reload_xml)

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
        mv_log.add_command(label='Note Err.', command=self.show_note_err)
        mv_log.add_separator()
        mv_log.add_command(label='*_text_.txt', command=self.show_text_txt)
        mv_log.add_command(label='XML => text ERR',
                           command=self.show_text_txt_err)
        mv_log.add_separator()
        mv_log.add_command(label='TeimEdit Err.', command=self.show_edit_err)
        mv_log.add_separator()
        mv_log.add_command(label='Read Log.', command=self.open_log)

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

        mv_help = tk.Menu(menu_bar, tearoff=0)
        mv_help.config(font=FONT_MENU,
                       bg=BG_MENU,
                       fg=FG_MENU,
                       activebackground=BG2_MENU,
                       activeforeground=FG2_MENU,
                       relief=tk.RAISED)
        mv_help.add_command(label='Files & Direcory', command=self.show_info)
        mv_help.add_command(label='run options', command=self.show_options)
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
        self.show_win1("")
        self.show_win2("")
        self.show_win3("")
        ############
        # cerca la dir teimcfg_dir partendo da teimcfg_die
        # teimcfg_dir is None parte da pwd
        # se non la trova exit
        # invoca
        # set_file_path
        # read_text_file
        # self.find_file_text(self.path_text)
        self.find_teimtag()
        ############
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
        return
        # self.win0.attributes("-topmost", 1)
        # self.win1.attributes("-topmost", 2)
        # self.win2.attributes("-topmost", 3)
        # self.win3.attributes("-topmost", 4)

    def iconify(self):
        self.win0.iconify()
        self.win1.iconify()
        self.win2.iconify()
        self.win3.iconify()

    ########################
    # mv_file
    ########################
    def reload_text(self):
        self.read_text_file()

    def import_text(self):
        self.top_order()
        wrk_dir = os.getcwd()
        path_read = fdialog.askopenfilename(
            parnet=self.win0,
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
            title='file',

            initialdir=self.text_dir,
            filetypes=[("text", "*.txt"),
                       ("*.*", "*.*")])
        if len(path) < 1:
            return
        if not pthu(path).exists():
            return
        self.set_path_files(path)
        self.read_text_file()

    def save_text(self, *args):
        s = self.get_text()
        self.write_file(self.path_text, s)

    def save_text_as(self, *args):
        self.top_order()
        path = fdialog.asksaveasfilename(title='Salva as Name',
                                         nitialdir=self.text_dir)
        if len(path) < 1:
            return ""
        text = self.get_text()
        self.set_path_files(path)
        self.write_file(self.path_text, text)
        title = f"TEXT: {path} "
        self.win0.title(title)

    def app_quit_yn(self):
        self.top_not()
        self.app_quit()
        return
        # TODO
        yn = mbox.askyesno("", "Quit ?", parent=self.win0)
        if yn:
            self.app_quit()

    def app_quit(self, *args):
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
        do_main_checktxt(pthu.path2str(self.path_tmp),
                         pthu.path2str(self.path_check_txt))
        self.chmod(self.path_check_txt)
        s = self.read_file(self.path_check_txt)
        self.show_log_top(s,True)

    def elab_checkover(self):
        s = self.get_text()
        self.write_file(self.path_tmp, s)
        # def do_main(path_src, path_csv, path_out):
        do_main_checkover(pthu.path2str(self.path_tmp),
                          pthu.path2str(self.path_over_csv),
                          pthu.path2str(self.path_check_over))
        self.chmod(self.path_check_over)
        s = self.read_file(self.path_check_over)
        self.show_log_top(s,True)

    ##########################################
    #chek edit funizoni di controllo su teimed
    ###########################################
    def over_name_label(self,name):
        js=self.ptr_over[name]
        o = js['o']
        c = js['c']
        return name, f'{name} {o }  {c}'

    def over_po_pc(self,name):
        js=self.ptr_over[name]
        po = js['po']
        pc = js['pc']
        return po,pc

    def del_tags(self):
        self.text_edit.tag_delete(self.tag_names[0])
        self.text_edit.tag_delete(self.tag_names[1])

    def config_tags(self):
        self.text_edit.tag_config(self.tag_names[0],
                                  background=BG_TAG,
                                  foreground=FG_TAG)
        self.text_edit.tag_config(self.tag_names[1],
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
            self.text_edit.tag_add(self.tag_names[t], idx, idx_end)
            idx = idx_end
            self.tag_num_debug += 1
        self.config_tags()
        # usa la prima rag per spostrae il teso alla sua posiziione
        tag_lst = self.text_edit.tag_ranges(self.tag_names[0])
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
            self.text_edit.tag_add(self.tag_names[t], idxo, idx_end)
            idxo = idx_end
            #print(f"A5 {idxo}  {idx_end} {t}  {so}  {sc}")
        self.config_tags()
        # usa la prima rag per spostrae il teso alla sua posiziione
        tag_lst = self.text_edit.tag_ranges(self.tag_names[0])
        t0 = tag_lst[0] if len(tag_lst) > 0 else "1.0"
        self.text_edit.see(t0)
        ###############
        # TODO controllo tags
        #print(f"tag a:{t0}  {len(tag_lst)}")
        n = len(m_lst)
        if self.tag_num_debug != n:
            print("error")
            for x in m_lst:
                print(f"{x['t']} {x['s']}")
            print(self.tag_num_debug)

    def fin_entity_comma(self):
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = ckte.clean_text(text)
        m_lst = ckte.check_entitys(txt_wrk)
        self.add_tags(m_lst)

    def find_entity_brackets(self):
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = ckte.clean_text(text)
        m_lst = ckte.check_entity_brackets(txt_wrk)
        self.add_tags(m_lst)

    def find_over(self, name,*args):
        po,pc=self.over_po_pc(name)
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = ckte.clean_text(text)
        m_lst = ckte.check_overflow(txt_wrk, po, pc)
        self.add_tags(m_lst)

    def find_form_to(self, name):
        po,pc=self.over_po_pc(name)
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = ckte.clean_text(text)
        m_lst = ckte.check_overflow(txt_wrk, po, pc)
        self.add_tags_from_to(m_lst)

    #############
    # mv_elab
    #############
    def elab_teimxml(self):
        s = self.get_text()
        self.write_file(self.path_text, s)
        try:
            do_main_xml(pthu.path2str(self.path_text),
                        pthu.path2str(self.path_entity_csv),
                        pthu.path2str(self.path_entity_txt))
        except SystemExit as e:
            s = f"ERROR Elab entity {os.linesep}{e}"
            logediterr.log(s)
            self.show_log_top(s, True)
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
            self.show_log_top("Call Elab. Entity",True)
            return
        # path_txt_1 => path_xml_1
        try:
           # def do_main(path_src, path_out, sigla_scrp, ids_start=""):
            do_main_setid(pthu.path2str(self.path_entity_txt),
                          pthu.path2str(self.path_setid_xml),
                          self.text_sign)
        except SystemExit as e:
            s = f"Errro in set id{os.linesep} {e}"
            logediterr.log(s)
            self.show_log_top(s, True)
            return
        self.chmod(self.path_setid_xml)
        ls = ["    Elab. Set id",
              f"{self.path_entity_txt}",
              f"{self.path_setid_xml}",
              f"{self.text_sign}"]
        self.show_log(os.linesep.join(ls), True)

    def elab_teimover(self):
        if not self.path_setid_xml.exists():
            self.show_log_top("Cal Elab. Set id ",True)
            return
        # path_xml_1 => path_xml_2
        try:
            # def do_main(src_path, out_path, csv_path):
            do_main_over(pthu.path2str(self.path_setid_xml),
                         pthu.path2str(self.path_over_xml),
                         pthu.path2str(self.path_over_csv))
        except SystemExit as e:
            s = f"Elaborare overflow {os.linesep} {e}"
            logediterr.log(s)
            self.show_log_top(s, True)
            return
        self.chmod(self.path_over_xml)
        ls = ["    Eelab. overflow",
              f"{self.path_setid_xml}",
              f"{self.path_over_xml}",
              f"{self.path_over_csv}"]
        self.show_log(os.linesep.join(ls), True)

    def elab_teimnote(self):
        if not self.path_over_xml.exists():
            self.show_log_top("Call Elab. Over",True)
            return
        # path_xml_2 => path_xml
        try:
            # def do_main(src_path, out_path, note_path):
            do_main_note(pthu.path2str(self.path_over_xml),
                         pthu.path2str(self.path_xml),
                         pthu.path2str(self.path_teimnote))
        except SystemExit as e:
            s = f"Elab. note {os.linesep} {e}"
            logediterr.log(s)
            self.show_log_top(s, True)
            return
        self.chmod(self.path_xml)
        ls = ["    Elab. Note",
              f"{self.path_over_xml}",
              f"{self.path_xml}",
              f"{self.path_teimnote}"]
        self.show_log(os.linesep.join(ls), True)
        self.format_xml()

    def elab_xml2txt(self):
        if not self.path_xml.exists():
            self.show_log_top("Call Elab. XML",True)
            return
        # path_xml => path_text_txt
        try:
            do_main_xml2txt(pthu.path2str(self.path_xml_format),
                            pthu.path2str(self.path_text_txt))
        except SystemExit as e:
            s = f"ERROR Elab. note {os.linesep}{e} "
            logediterr.log(s)
            self.show_log_top(s, True)
            return
        self.chmod(self.path_xml)
        ls = ["    XML => text",
              f"{self.path_xml}",
              f"{self.path_text_txt}"]
        self.show_log(os.linesep.join(ls), True)

    def format_xml(self):
        s = self.read_file(self.path_xml)
        # TODO
        s=str(s)
        xml = '<div>'+s+'</div>'
        self.write_file(self.path_tmp, xml)
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            path = pthu.path2str(self.path_tmp)
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
            self.show_log_top(s,True)

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
        path_lst=pthu.list_path(self.log_dir)
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
        path = pthu.str2path(path)
        if path.exists():
            s = self.read_file(path)
        else:
            s = "Not Found."
        self.show_log_top(s)

    #############
    # menu_bar
    ############
    def show_info(self):
        #abs_teimcfg = os.path.abspath(str(self.teimcfg_dir))
        #abs_text = os.path.abspath(str(self.text_dir))
        wrk_dir = self.pwd
        info = [
            "---------------------------",
            f"work dir       : {wrk_dir}  ",
            f"parent text    : {self.dir_parent_text}",
            f"parent teimcfg : {self.dir_parent_teimcfg}",
            f"teimed tags    : {self.path_entity_csv}",
            f"overflow tags  : {self.path_over_csv}",
            "---------------------------",
            f"text dir : {self.text_dir}",
            f"text     : {self.path_text}",
            f"sigla    : {self.text_sign}",
            f"note     : {self.path_teimnote}",
            "---------------------------",
            f"chek  txt   : {self.path_check_txt}",
            f"check over  : {self.path_check_over}",
            "",
            f"elab  entity: {self.path_entity_txt}",
            f"log   entity: {self.path_entity_log}",
            f"ERR   entity: {self.path_entity_err}",
            "",
            f"elab  set id: {self.path_setid_xml}",
            f"log   set id: {self.path_setid_log}",
            f"err   set id: {self.path_setid_err}",
            "",
            f"elab  over  : {self.path_over_xml}",
            f"log   over  : {self.path_over_log}",
            f"err   over  : {self.path_over_err}",
            "",
            f"elab  note  : {self.path_xml}",
            f"err   note  : {self.path_note_err}",
            "",
            f"elab  text  : {self.path_text_txt}",
            f"err   text  : {self.path_text_err}",
            "---------------------------",
        ]
        s = os.linesep.join(info)
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
        else:
            self.write_file(self.path_text, "Empty")
            r = ["", f"File  {self.path_text} Not Found.",
                 "", f"Crated {self.path_text} empyt."]
            s = os.linesep.join(r)
        self.text_edit.insert_text(s)
        title = f"TEXT: {self.path_text} "
        self.win0.title(title)

    def read_log_file(self, path):
        if path.exists():
            s = self.read_file(path)
        else:
            s = f"{path}   Not Found."
        self.show_log_top(s)

    def show_log_top(self, msg, append=False):
        self.show_log(msg, append)
        self.top_w3()

    def show_log_lift(self, msg, append=False):
        self.show_log(msg, append)
        self.win3.lift()

    def show_log(self, msg, append=False):
        msg = "" if msg is None else msg
        if append:
            r = os.linesep.join(["","",msg])
            self.txt3.insert(tk.END, r)
            self.txt3.see(tk.END)
        else:
            r = os.linesep.join(["",msg])
            self.txt3.delete('1.0', tk.END)
            self.txt3.insert('1.0', r)

    # def xshow_log(self, msg, append=False):
    #     msg = "" if msg is None else msg
    #     if append:
    #         x = self.txt3.get('1.0', 'end')
    #         msg = f"{x}{msg}{os.linesep}"
    #     else:
    #         msg = f" {os.linesep}{msg}{os.linesep}"
    #     self.txt3.delete('1.0', tk.END)
    #     self.txt3.insert('1.0', msg)

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
        s = '' if s is None else s
        self.open_win1()
        self.txt1.delete('1.0', tk.END)
        self.txt1.insert('1.0', s)

    def quit2(self):
        self.win2.destroy()
        self.win2 = None

    def show_win2(self, s):
        s = '' if s is None else s
        self.open_win2()
        self.txt2.delete('1.0', tk.END)
        self.txt2.insert('1.0', s)

    def quit3(self):
        self.win3.destroy()
        self.win3 = None

    def show_win3(self, s):
        s = '' if s is None else s
        self.open_win3()
        self.txt3.delete('1.0', tk.END)
        self.txt3.insert('1.0', s)


def do_main(dir_parent_teimcfg,
            dir_parent_text,
            path_text,
            sign):
    tme = TeimEdit(dir_parent_teimcfg,
                   dir_parent_text,
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
                        metavar="dir search teimcfg",
                        help="[-c <teimcfg>]")
    parser.add_argument('-d',
                        dest="parenttext",
                        required=False,
                        default=None,
                        metavar="dir search text",
                        help="[-d <search_dir>]")
    parser.add_argument('-t',
                        dest="txt",
                        required=False,
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
    do_main(args.parentcfg,
            args.parenttext,
            args.txt,
            args.sign)
