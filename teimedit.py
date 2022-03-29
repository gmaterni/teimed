#!/usr/bin/env python3
# coding: utf-8
from pdb import set_trace
import platform
import argparse
import os
import pprint
import sys
import re
import tkinter as tk
import tkinter.filedialog as fdialog
import tkinter.messagebox as mbox

from lxml import etree

import teimedlib.check_teimed as chk
import teimedlib.pathutils as ptu
import teimedlib.teim_paths as tpth
from teimedlib.clean_text import clean_text
from teimedlib.edit_constants import *
from teimedlib.findfile import *
from teimedlib.listbox import open_listbox
from teimedlib.readovertags import read_over_tags
from teimedlib.teim_constants import *
from teimedlib.textedit import TextEdit
from teimedlib.textpad import TextPad
from teimedlib.ualog import Log
from teimedlib.uarc import UaRc
from teimedlib.tei_head import add_tei_head
from checkover import do_main as do_main_checkover
from checktxt import do_main as do_main_checktxt
from teimnote import do_main as do_main_note
from teimover import do_main as do_main_over
from teimsetid import do_main as do_main_setid
from teimxml import do_main as do_main_xml
from teixml2txt import do_main as do_main_xml2txt

__date__ = "10-03-2022"
__version__ = "1.2.3"
__author__ = "Marta Materni"


# -d paris (facoltativo)
# cerca a partire dalla directory "paris" tutti i testi
# che corrispondono al nome o alla wilcard dell'opzione -t
# se ne trova più di uno. mostra una lista per selezionare
# se ne trova uno, lo seleziona e procede
# se non ne trova nessuno, mostra un messaggio e procede

def HELP_RUN_OPS():
    s = """
teimedit.py -c ancestor_teimfcg -t <file_text -e
Lancio dell'applicazionw

teimedit.py -h
lista delle opzioni

teimedit.py -x
Visualizza istruzioni

-c ancestor_teimfcg (facoltativo)
cerca a partire dalla directory "acncestor_teimfcg" la directory "teimcfg"
se ne trova più di una, mostra la lista per selezionarne una.
se ne trova una, lo seleziona e procede
se non ne trova nessuna, esce dall'applicazione
se non è settata cerca la dir "teimcfg" a partirre dalla dir corente

-t testo.txt 
nome del file o wilcard dei files di testo da elaborare
se si utilizza la wilcard, usare apici o virgolette:
es.
teimedit.py -t "a*.txt" 
restituisce tutti i file che iniziano in "a" e terminano in ".txt"
E' possibile usare "$" senza gli apici.
es:
teimedit.py -t a$.txt

- e <facoltativo>
cancella la storia delle precedenti sessioni

L' applicativo salva i parametri con  i qualei
è stato lanciato e posizioni e dimensioni delle finestre
al momento della chiusura.
Qundi lanciandolo sucessivamente senza alcun parametro usa 
quelli memorizzati.
Il flag -e cancella la storia dela sessione.
es. 
teimedit.py -c florimontr  -t 'paris/*.txt'
Cerca "teimfcg" nella dir florimont e visualizza una lista
dir tutti i file della dir 'paris/' con estensione '.txt'. 

teimedit -t 'paris/e*.txt'
Utilizza per 'teimfcg' la dir precedentemente settata 
visualizzate la lsita dei file nella dir 'paris'/ che iniziando
con 'e' e terminano con '.txt'

teimedit-py -t 'paris/e*.txt' -e
Ceca i file di testo come nel caso precedente, ma cterca 'teimfcg' 
a partire dalla dir corrente e visualizza le finestre nelle
posizioni e con le dimension iniziali.

Tasti di controllo:

Ctrl-q 
esce dall'applicazione.E' abilitato solo dalla finestra 
con la barra di menu.

Ctrl-w
quando ci si tova su una fieìnestra selezionata sopra a tutte
le altre ristabilisce l'ordine di default permettendo l'accesso
al menu e quindi a Ctrl-q.
        """
    return s


g_win0 = '1000x600+50+50'
g_win1 = '1000x600+150+150'
g_win2 = '1000x600+250+250'
g_win3 = '1000x600+350+350'


def pp(data, w=60):
    return pprint.pformat(data, width=w)


RC_PARENT_TEIMCFG = "parent_teimcfg"
# RC_ROOT_DIR = "root_dir"
# RC_PATH_MATCH = "path_match"
RC_PATH_LAST = "path_last"
RC_RECENTI = "recenti"
###############
PATH_ROOT_DIR = "."
PARENT_TEIMCFG = "."
TEIMEDIT_LOG = "log/teimedit.log"
rc = UaRc('.teimeditrc')
log_err = Log("w")
os_name = platform.system().lower()


class TeimEdit(object):

    def __init__(self,
                 parent_teimcfg,
                 root_dir,
                 path_match):
        """
            parent_teimcfg (str, optional): dir parent di teimcfg "".
            root_dir (str, optional): dir parent del/dei file di testo.
            path_match (str, optional): wilcard file/i di testo.
        """
        # log_err
        self.path_edit_err_p = ptu.str2path(TEIMEDIT_LOG)
        self.path_edit_err_s = ptu.path2str(self.path_edit_err_p)
        log_err.open(self.path_edit_err_s, 1)
        log_err.log('')
        # rc init
        self.parent_teimcfg_s = rc.upd(
            RC_PARENT_TEIMCFG, parent_teimcfg, PARENT_TEIMCFG)
        # x = rc.upd(RC_ROOT_DIR, root_dir)
        # self.root_dir_p = ptu.str2path(x)
        # self.path_match_s = rc.upd(RC_PATH_MATCH, path_match)
        self.path_match_s = path_match
        # rc.prn('init')
        ########################
        self.pwd = ptu.cwd()

        self.path_text_s = ''
        self.text_dir_s = ''
        self.path_note_csv_s = ''

        self.path_teim_in_s = ''
        self.path_teim_out_s = ''
        self.path_teim_log_s = ''
        self.path_teim_err_s = ''

        self.path_id_in_s = ''
        self.path_id_out_s = ''
        self.path_id_log_s = ''
        self.path_id_err_s = ''

        self.path_over_in_s = ''
        self.path_over_out_s = ''
        self.path_over_log_s = ''
        self.path_over_err_s = ''

        self.path_note_in_s = ''
        self.path_note_out_s = ''
        # self.path_note_log_s = ''
        self.path_note_err_s = ''

        self.path_xml_in_s = ''
        self.path_xml_out_s = ''
        self.path_xml_err_s = ''

        self.path_tei_in_s = ''
        self.path_tei_out_s = ''
        self.path_tei_err_s = ''

        self.path_xml2txt_in_s = ''
        self.path_xml2txt_out_s = ''
        self.path_xml2txt_err_s = ''

        self.path_checktxt_in_s = ''
        self.path_checktxt_out_s = ''

        self.path_checkover_in_s = ''
        self.path_checkover_out_s = ''

        ####################

        # var per il controllo del check
        self.tag_num_debug = 0

        # dopo la lettutr cfg
        self.tag_over_lst = []
        self.text_edit = None
        self.win0 = None
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
        self.mv_check = None
        self.mv_check_filled = False

    ####################################
    # UA gestione files
    ####################################

    def write_file(self, path, text):
        if isinstance(path, str):
            path = ptu.str2path(path)
        path.write_text(text)
        self.chmod(path)

    def read_file(self, path):
        if isinstance(path, str):
            path = ptu.str2path(path)
        if not path.exists():
            s = ptu.path2str(path)
            self.show_log_lift(f"File:{s} Not Found.A1", True)
            return ''
        with path.open('r', encoding='utf-8') as f:
            s = f.read()
        return s

    def chmod(self, path):
        if isinstance(path, str):
            path = ptu.str2path(path)
        try:
            ptu.chmod(path)
        except Exception as e:
            log_err.log(f"ERROR chmod() {path}\n{e}")
            self.top_free()
            mbox.showerror("", f"ERROR {path}")

    def read_text_file(self):
        if self.path_text_s == '':
            return
        if not self.path_text_p.exists():
            msg = f"{self.path_text_s} Not Found"
            self.top_free()
            mbox.showerror("", msg)
            return
        try:
            s = self.read_file(self.path_text_p)
        except Exception as e:
            msg = f"{self.path_text_s} Not Found"
            log_err.log(f'read_text_file()\n{msg}')
            self.top_free()
            mbox.showerror("", msg)
        else:
            self.text_edit.insert_text(s)
            self.show_psths()
            self.win0.lift()
            self.text_edit.focus_set()
            self.rc_update()

    def read_log_file(self, path):
        if isinstance(path, str):
            path = ptu.str2path(path)
        if path.exists():
            s = self.read_file(path)
            self.show_log_top(s)
        else:
            self.top_free()
            mbox.showinfo("", f"{path} Not Foud", parent=self.win0)

    def rfind_teimcfg(self):
        """
        cerca in modalità ricorsiva la dir teimgcfg a partire
        dal parametro parent_teimcfg se settato,
        altrimenti dalla dir corrente.
        Se esiste invoca:
        set_teimcfg_paths()
        find_file_text()

        """
        try:
            if self.parent_teimcfg_s is None:
                dir_s = PARENT_TEIMCFG
            else:
                dir_s = self.parent_teimcfg_s
            dir_p = ptu.str2path(dir_s)
            dir_p_lst = rfind_dir_lst(dir_p, TEIMCFG)
            dir_s_lst = ptu.pathlist2strlist(dir_p_lst)
            le = len(dir_p_lst)
            if le == 0:
                self.iconify()
                msg = f"{TEIMCFG} Not Foud"
                mbox.showerror("", msg)
                sys.exit(msg)
            elif le == 1:
                path_teimcfg_s = dir_s_lst[0]
                self.set_teimcfg_paths(path_teimcfg_s)
                self.find_file_text()
            else:
                def on_select(n):
                    if n < 0:
                        return
                    path_teimcfg_s = dir_s_lst[n]
                    self.set_teimcfg_paths(path_teimcfg_s)
                    self.find_file_text()
                open_listbox(dir_s_lst, on_select, "find teimcfg")
            return
        except Exception as e:
            msg = f"ERROR find_teimfcg()\n{e}"
            log_err.log(msg)
            self.iconify()
            mbox.showerror("", f"{TEIMCFG}\nNot Foud")
            sys.exit(msg)

    def find_file_text(self):
        """
            se si usa una wilcard cerca nalla root_dir
        """
        match_file = self.path_match_s
        if match_file is None:
            return
        # NON è una vwil card
        if ptu.exists(match_file):
            # if self.is_path(match_file):
            self.set_paths(match_file)
            self.read_text_file()
            return
        # match_file è una wilcard
        try:
            file_p_lst = find_file_lst(None, match_file)
            file_s_lst = ptu.pathlist2strlist(file_p_lst)
            le = len(file_p_lst)
            if le == 0:
                self.top_free()
                msg = f"File: {match_file}\nNot Found"
                mbox.showinfo("", msg, parent=self.win0)
            elif le == 1:
                path_text_s = file_s_lst[0]
                self.set_paths(path_text_s)
                self.read_text_file()
            else:
                def load_file(n):
                    if n < 0:
                        return
                    path_text_s = file_s_lst[n]
                    self.set_paths(path_text_s)
                    self.read_text_file()
                open_listbox(file_s_lst, load_file, "find text")
        except Exception as e:
            msg = f"ERROR find_file_text()\n{match_file}\n{e}"
            log_err.log(msg)
            self.show_log_top(msg)

    def get_edit_text(self):
        s = self.text_edit.get('1.0', 'end')
        return s.strip()

    ####################################
    # UA gestione path
    ####################################

    def set_teimcfg_paths(self, path_s):
        self.path_teimcfg_s = path_s
        try:
            path_p = ptu.str2path(path_s)
            self.path_teimcfg_p = path_p
            self.parent_teimcfg_p = path_p.parent
            self.parent_teimcfg_s = ptu.path2str(path_p.parent)

            self.path_entity_csv_p = ptu.join(path_p, TEIMTAGS_CSV)
            self.path_over_csv_p = ptu.join(path_p, TEIMOVERFLOW_CSV)
            self.path_xmlid_csv_p = ptu.join(path_p, TEIMXMLID_CSV)
            self.path_tei_head_p = ptu.join(path_p, TEI_HEAD)

            self.path_entity_csv_s = ptu.path2str(self.path_entity_csv_p)
            self.path_over_csv_s = ptu.path2str(self.path_over_csv_p)
            self.path_xmlid_csv_s = ptu.path2str(self.path_xmlid_csv_p)
            self.path_tei_head_s = ptu.path2str(self.path_tei_head_p)

            if not self.path_over_csv_p.exists():
                self.iconify()
                msg = f"overflow.csv:{self.path_over_csv_p} Not Found"
                mbox.showerror("", msg)
                sys.exit(msg)

            if not self.path_entity_csv_p.exists():
                self.iconify()
                msg = f"teimtags.csv:{self.path_entity_csv_p} Not Found"
                mbox.showerror("", msg)
                # self.show_log_top(msg)
                sys.exit(msg)

            if not self.path_xmlid_csv_p.exists():
                self.iconify()
                msg = f"teimxmlid.csv:{self.path_xmlid_csv_p} Not Found"
                mbox.showerror("", msg)
                sys.exit(msg)

            if not self.path_tei_head_p.exists():
                self.iconify()
                msg = f"tei.xml:{self.path_tei_head_p} Not Found"
                mbox.showerror("", msg)
                sys.exit(msg)

            # legge la tabbella per overflow
            lst = read_over_tags(self.path_over_csv_p)
            # prepara la tabella per la gestione del menu
            self.tag_over_lst = chk.fill_tag_over_lst(lst)
            self.add_mv_check()

        except Exception as e:
            msg = f"ERROR set_teimcfg_paths()\n {e}"
            log_err.log(msg)
            self.iconify()
            mbox.showerror("", f"ERROR \nset_teimcfg_paths() ")
            sys.exit(msg)

    def set_paths(self, path_text_s):
        try:
            self.path_text_s = path_text_s
            self.path_text_p = ptu.str2path(path_text_s)

            # definizioni path di pathlib
            self.text_dir_p = self.path_text_p.parent
            self.text_dir_s = ptu.path2str(self.text_dir_p)
            self.log_dir_p = ptu.join(self.text_dir_p, "log")
            ptu.make_dir(self.log_dir_p)

            path_note_csv_p = ptu.join(self.text_dir_p, TEIMNOTE_CSV)
            self.path_note_csv_s = ptu.path2str(path_note_csv_p)

            # test.txt => ./log/testo_teim.txt
            self.path_teim_in_s = path_text_s
            self.path_teim_out_s = tpth.set_path_teim_out(path_text_s)
            self.path_teim_log_s = tpth.set_path_teim_log(path_text_s)
            self.path_teim_err_s = tpth.set_path_teim_err(path_text_s)

            # test.txt => ./log/testo_id.xml
            self.path_id_in_s = path_text_s
            self.path_id_out_s = tpth.set_path_id_out(path_text_s)
            self.path_id_log_s = tpth.set_path_id_log(path_text_s)
            self.path_id_err_s = tpth.set_path_id_err(path_text_s)

            # test.txt => ./lg/testo_id_over.xml
            self.path_over_in_s = path_text_s
            self.path_over_out_s = tpth.set_path_over_out(path_text_s)
            self.path_over_log_s = tpth.set_path_over_log(path_text_s)
            self.path_over_err_s = tpth.set_path_over_err(path_text_s)

            # test.txt => ./log/testo_id_over_note.xml
            # test.txt => testo.xml
            self.path_note_in_s = path_text_s
            self.path_note_out_s = tpth.set_path_note_out(path_text_s)
            # self.path_note_log_s = tpth.set_path_note_log(path_text_s)
            self.path_note_err_s = tpth.set_path_note_err(path_text_s)

            # ./log/testo_id_over_note.xml => testo.xml
            self.path_xml_in_s = tpth.set_path_xml_in(path_text_s)
            self.path_xml_out_s = tpth.set_path_xml_out(path_text_s)
            self.path_xml_err_s = tpth.set_path_xml_err(path_text_s)

            self.path_tei_in_s = tpth.set_path_tei_in(path_text_s)
            self.path_tei_out_s = tpth.set_path_tei_out(path_text_s)
            self.path_tei_err_s = tpth.set_path_tei_err(path_text_s)

            # log/testo_id_over_note.xml => testo_text.txt
            self.path_xml2txt_in_s = self.path_xml_out_s
            path_xml2txt_out_s = path_text_s.replace('.txt', '_text.txt')
            self.path_xml2txt_out_s = path_xml2txt_out_s
            path_xml2txt_err_s = path_text_s.replace('.txt', '_text.ERR.log')
            self.path_xml2txt_err_s = path_xml2txt_err_s

            # test.txt => ./log/testo_checktxt.log
            self.path_checktxt_in_s = path_text_s
            self.path_checktxt_out_s = tpth.set_path_checktxt_out(path_text_s)
            # self.path_checktxt_err_s = tpth.set_path_checktxt_err( path_text_s)

            # test.txt => ./log/testo_checkover.log
            self.path_checkover_in_s = path_text_s
            self.path_checkover_out_s = tpth.set_path_checkover_out(
                path_text_s)
            # self.path_checkover_err_s = tpth.set_path_checkover_err( path_text_s)
        except Exception as e:
            msg = f"ERROR set_paths()\n{e}"
            log_err.log(msg)
            self.iconify()
            mbox.showerror("", f"ERROR set_paths ")
            sys.exit(msg)

   ###############################################
    # UA GUI start
    ##############################################

    def add_mv_check(self):
        # lst.append([func_type,name,so,sc,po,pc])
        lst = self.tag_over_lst
        if lst is None:
            return
        if self.mv_check_filled:
            return
        # self.mv_check.delete(9,20)
        for item in lst:
            t, name, so, sc, po, pc = item
            lbl = f'{name}:  {so}   {sc}'
            if t == 0:
                self.mv_check.add_command(
                    label=lbl,
                    command=lambda x=po, y=pc, : self.find_form_to(x, y))
            else:
                self.mv_check.add_command(
                    label=lbl,
                    command=lambda x=po, y=pc: self.find_over(x, y))
        self.mv_check.add_separator()
        self.mv_check_filled = True

    def open_win0(self):

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
        # self.win0.withdraw()
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
        mv_file.add_command(label='Quit',
                            command=self.app_quit,
                            underline=0,
                            background=BG_MENU_LBL,
                            foreground=FG_MENU_LBL,
                            activebackground=BG2_MENU_LBL,
                            activeforeground=FG2_MENU_LBL)
        mv_file.add_separator()
        self.text_edit.bind("<Control-o>", self.open_text)
        self.text_edit.bind("<Control-s>", self.save_text)
        self.text_edit.bind("<Control-Shift-S>", self.save_text_as)
        mv_edit = new_mv()
        mv_edit.add_command(label="Undo     Ctrl-Z")
        mv_edit.add_command(label="Redo     Ctrl-Shift-Z",
                            command=self.text_edit.on_redo)
        mv_edit.add_separator()
        mv_edit.add_command(label="Cut", accelerator="Ctrl+X",
                            command=lambda: self.text_edit.event_generate('<Control-x>'))
        mv_edit.add_command(label="Copy", accelerator="Ctrl+C",
                            command=lambda: self.text_edit.event_generate('<Control-c>'))
        mv_edit.add_command(label="Paste", accelerator="Ctrl+V",
                            command=lambda: self.text_edit.event_generate('<Control-v>'))
        mv_edit.add_separator()
        mv_edit.add_command(label="Find&Replace  Ctrl-F",
                            command=self.text_edit.find_replace)
        #########################################
        self.mv_check = new_mv()
        self.mv_check.add_command(label='Check Entities Log',
                                  command=self.elab_checktxt)
        self.mv_check.add_command(label='Check Overflow Log',
                                  command=self.elab_checkover)
        self.mv_check.add_separator()
        self.mv_check.add_command(label='Entities Comma',
                                  command=self.fin_entity_comma)
        self.mv_check.add_command(label='Entities Brackets',
                                  command=self.find_entity_brackets)
        self.mv_check.add_command(label='Entities Undefined',
                                  command=self.find_entity_undefined)
        self.mv_check.add_command(label='Clean', command=self.del_tags)
        self.mv_check.add_separator()
        #########################################
        mv_elab = new_mv()
        mv_elab.add_command(label='Elab. Entities', command=self.elab_teimxml)
        mv_elab.add_command(label='Elab. Set ID', command=self.elab_teimsetid)
        mv_elab.add_command(label='Elab. Overflow', command=self.elab_teimover)
        mv_elab.add_command(label='Elab. Note', command=self.elab_teimnote)
        mv_elab.add_command(label='Elab. TEI', command=self.elab_tei)
        mv_elab.add_separator()
        mv_elab.add_command(label='XML => text', command=self.elab_xml2txt)
        mv_elab.add_separator()
        mv_elab.add_command(label='Elab. All', command=self.elab_all)

        mv_log = new_mv()
        mv_log.add_command(label='Check Text Err.', command=self.show_checktxt)
        mv_log.add_command(label='Check Over Err.',
                           command=self.show_checkover)
        mv_log.add_separator()
        mv_log.add_command(label='Entity Out', command=self.show_entity_out)
        mv_log.add_command(label='Entity Log.', command=self.show_entity_log)
        mv_log.add_command(label='Entity Err.', command=self.show_entity_err)
        mv_log.add_separator()
        mv_log.add_command(label='Set ID Out', command=self.show_setwid_out)
        mv_log.add_command(label='Set ID Log.', command=self.show_setwid_log)
        mv_log.add_command(label='Set ID Err.', command=self.show_setwid_err)
        mv_log.add_separator()
        mv_log.add_command(label='Overflow Out', command=self.show_over_out)
        mv_log.add_command(label='Overflow Log.', command=self.show_over_log)
        mv_log.add_command(label='Overflow Err.', command=self.show_over_err)
        mv_log.add_separator()
        mv_log.add_command(label='Note Out', command=self.show_note_out)
        # mv_log.add_command(label='Note Log.', command=self.show_note_log)
        mv_log.add_command(label='Note Err.', command=self.show_note_err)
        mv_log.add_separator()
        mv_log.add_command(label='XML ', command=self.show_xml_out)
        mv_log.add_command(label='XML Err.', command=self.show_xml_err)
        mv_log.add_command(label='XML-TEI', command=self.show_tei_out)
        mv_log.add_command(label='XML-TEI Err.', command=self.show_tei_err)
        mv_log.add_separator()
        mv_log.add_command(label='xml2text Out', command=self.show_xml2txt_out)
        mv_log.add_command(label='xml2text Err.',
                           command=self.show_xml2txt_err)
        mv_log.add_separator()
        mv_log.add_command(label='TeimEdit Err.', command=self.show_edit_err)
        mv_log.add_separator()
        mv_log.add_command(label='Read Log', command=self.open_log)

        mv_del = new_mv()
        mv_del.add_command(label='Entities', command=self.delete_txt1)
        mv_del.add_command(label='XML', command=self.delete_txt2)
        mv_del.add_command(label='Log', command=self.delete_txt3)
        mv_del.add_command(label='All', command=self.delete_txt_all)
        mv_del.add_separator()
        mv_del.add_command(label='Remove log files', command=self.remove_log)

        mv_help = new_mv()
        mv_help.add_command(label='Files & Directory', command=self.help_paths)
        mv_help.add_command(label='run options', command=self.help_options)

        # orizontale
        menu_bar.add_cascade(label='File', menu=mv_file, underline=0)
        menu_bar.add_cascade(label='Edit', menu=mv_edit, underline=0)
        menu_bar.add_cascade(label='Check', menu=self.mv_check, underline=0)
        menu_bar.add_cascade(label='Elab.', menu=mv_elab, underline=1)
        menu_bar.add_cascade(label='Log', menu=mv_log, underline=0)
        menu_bar.add_cascade(label='Del.', menu=mv_del, underline=0)

        s = f"W:"
        menu_bar.add_command(label=s, activeforeground=FG_MENU,
                             activebackground=BG_MENU),
        menu_bar.add_command(label=' 1', command=self.top_w0,)
        menu_bar.add_command(label=' 2', command=self.top_w1)
        menu_bar.add_command(label=' 3', command=self.top_w2)
        menu_bar.add_command(label=' 4 ', command=self.top_w3)
        menu_bar.add_command(label='1234 ', command=self.top_free)
        menu_bar.add_command(label='Tidy', command=self.top_order)
        s = f"                      "
        menu_bar.add_command(label=s, activeforeground=FG_MENU,
                             activebackground=BG_MENU),
        menu_bar.add_cascade(label='Help', menu=mv_help)
        s = f" {__version__} "
        menu_bar.add_command(label=s, activeforeground=FG_MENU,
                             activebackground=BG_MENU),

        self.open_win1()
        self.open_win2()
        self.open_win3()

        # UA tasti di conrollo globali
        self.text_edit.bind("<Control-q>", self.app_quit)
        # self.txt1.bind("<Control-q>", self.app_quit)
        # self.txt2.bind("<Control-q>", self.app_quit)
        # self.txt3.bind("<Control-q>", self.app_quit)
        self.txt1.bind("<Control-w>", lambda x: self.top_free())
        self.txt2.bind("<Control-w>", lambda x: self.top_free())
        self.txt3.bind("<Control-w>", lambda x: self.top_free())

        self.show_win1("")
        self.show_win2("")
        self.show_win3("")
        ################################
        # cerca la dir teimcfg_dir partendo
        # -c teimcfg_dir od dalla dir corrente se non è settata
        # se non la trova exit
        # invoca:
        # set_file_path
        # read_over_tags
        self.rfind_teimcfg()
        ##################################
        self.add_mv_check()
        self.top_free()
        self.text_edit.focus()
        tk.mainloop()
        ###############################

    def open_win1(self):
        self.win1 = tk.Toplevel(self.win0)
        self.win1.title('ENTITY')
        self.win1.protocol("WM_DELETE_WINDOW", lambda: False)
        self.win1.rowconfigure(0, weight=1)
        self.win1.columnconfigure(0, weight=1)
        self.win1.geometry(self.geometry_win1)
        self.txt1 = TextPad(self.win1)
        self.txt1.config(spacing1=2, spacing3=2)
        self.txt1.grid(sticky='nsew')

    def open_win2(self):
        self.win2 = tk.Toplevel(self.win0)
        self.win2.title('XML')
        self.win2.protocol("WM_DELETE_WINDOW", lambda: False)
        self.win2.rowconfigure(0, weight=1)
        self.win2.columnconfigure(0, weight=1)
        self.win2.geometry(self.geometry_win2)
        self.txt2 = TextPad(self.win2)
        self.txt2.config(spacing1=2, spacing3=2)
        self.txt2.grid(sticky='nsew')

    def open_win3(self):
        self.win3 = tk.Toplevel(self.win0)
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
        # self.win0.deiconify()
        self.rc_save()
        self.win0.quit()
        # sys.exit(0)

   ########################
   # UA manu mgr
   ########################

    def top_order(self):
        self.top_not()
        self.win0.geometry(g_win0)
        self.win1.geometry(g_win1)
        self.win2.geometry(g_win2)
        self.win3.geometry(g_win3)
        self.win3.lift()
        self.win2.lift()
        self.win1.lift()
        self.win0.lift()

    def top_free(self):
        self.top_not()
        self.win3.lower(self.win2)
        self.win2.lower(self.win1)
        self.win1.lower(self.win0)
        self.win0.lift()

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

    def iconify(self):
        self.win0.iconify()
        self.win1.iconify()
        self.win2.iconify()
        self.win3.iconify()

    ########################
    # UA menu file
    ########################

    def open_text(self, *args):
        self.top_free()
        path_text_s = fdialog.askopenfilename(title='file',
                                              initialdir=self.text_dir_s,
                                              filetypes=[("text", "*.txt"),
                                                         ("*.*", "*.*")])
        if len(path_text_s) < 1:
            return
        if not ptu.exists(path_text_s):
            return
        path_text_s = ptu.relative_to(path_text_s, self.pwd)
        self.set_paths(path_text_s)
        self.read_text_file()

    def open_recenti(self):
        try:
            file_lst_s = self.rc_get_recenti()
            if len(file_lst_s) < 1:
                return
            self.top_free()

            def load_file(n):
                if n < 0:
                    return
                path_text_s = file_lst_s[n]
                self.set_paths(path_text_s)
                self.read_text_file()
            open_listbox(file_lst_s, load_file, "find text")
        except Exception as e:
            log_err.log(f"ERROR oepen_recenti() \n{e}")
            self.top_free()
            mbox.showerror("", f"ERROR open_recenti() ")

    def save_text(self, *args):
        s = self.get_edit_text()
        self.write_file(self.path_text_p, s)
        self.rc_update()

    def save_text_as(self, *args):
        self.top_free()
        init_dir = self.text_dir_s
        path_text_s = fdialog.asksaveasfilename(title='Save as Name',
                                                initialdir=init_dir)
        if path_text_s is None or len(path_text_s) < 1:
            return ""
        text = self.get_edit_text()
        path_text_s = ptu.relative_to(path_text_s, self.pwd)
        self.set_paths(path_text_s)
        self.write_file(self.path_text_p, text)
        self.rc_update()
        title = f"TEXT: {path_text_s} "
        self.win0.title(title)

    ##########################
    # menu edit
    ##########################

    #################
    # UA menu check
    ################
    def elab_checktxt(self):
        s = self.get_edit_text()
        self.write_file(self.path_checktxt_in_s, s)
        do_main_checktxt(self.path_checktxt_in_s)
        s = self.read_file(self.path_checktxt_out_s)
        self.show_log_top(s, True)

    def elab_checkover(self):
        s = self.get_edit_text()
        self.write_file(self.path_checkover_in_s, s)
        do_main_checkover(self.path_checkover_in_s,
                          self.path_over_csv_s)
        s = self.read_file(self.path_checkover_out_s)
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
            # print(f"A5 {idxo}  {idx_end} {t}  {so}  {sc}")
        self.config_tags()
        # usa la prima rag per spostrae il teso alla sua posiziione
        tag_lst = self.text_edit.tag_ranges(FIND_TAGS[0])
        t0 = tag_lst[0] if len(tag_lst) > 0 else "1.0"
        self.text_edit.see(t0)
        ###############
        #  controllo tags
        # print(f"tag a:{t0}  {len(tag_lst)}")
        n = len(m_lst)
        if self.tag_num_debug != n:
            log_err.log("Error")
            for x in m_lst:
                log_err.log(f"{x['t']} {x['s']}")
                self.show_log_top(f"{x['t']} {x['s']}")
            log_err.log(self.tag_num_debug)
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

    def read_teimtags_set(self):
        """Lettura set di tags da teimtag.csv 
        """
        DELIMITER = '|'
        lst = []
        rows = self.path_entity_csv_p.open().readlines()
        for row in rows:
            if row.strip() == '':
                continue
            if row[0] == '#':
                continue
            cols = row.split(DELIMITER)
            if len(cols) < 3:
                continue
            tag_name = cols[1].strip()
            lst.append(tag_name)
        tag_set = set(lst)
        return tag_set

    def find_entity_undefined(self):
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = clean_text(text)
        m_lst = chk.check_entitys(txt_wrk)
        tag_set = self.read_teimtags_set()
        err_lst = []
        for item in m_lst:
            tag = item.get('s', '').replace('&', '').replace(';', '').strip()
            if tag in tag_set:
                continue
            item['t'] = 1
            err_lst.append(item)
        self.add_tags(err_lst)

    def find_over(self, po, pc, *args):
        # FIXME  controlla tag [] e [_ _]
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = clean_text(text)
        m_lst = chk.check_overflow(txt_wrk, po, pc)
        self.add_tags(m_lst)

    def find_form_to(self, po, pc):
        # contolla tags di tipo overflow
        text = self.text_edit.get('1.0', tk.END)
        txt_wrk = clean_text(text)
        m_lst = chk.check_overflow(txt_wrk, po, pc)
        self.add_tags_from_to(m_lst)

    #############
    # UA menu elab
    #############
    def elab_teimxml(self):
        msg = self.get_edit_text()
        self.write_file(self.path_teim_in_s, msg)
        try:
            do_main_xml(self.path_teim_in_s,
                        self.path_entity_csv_s)
        except SystemExit as e:
            msg = f"ERROR Elab entities\n{e}"
            log_err.log(msg)
            self.show_log_top(msg, True)
            return
        msg = self.read_file(self.path_teim_log_s)
        self.show_win1(msg)

        ls = ["Elab. entity",
              f"{self.path_teim_in_s}",
              f"{self.path_teim_out_s}",
              f"{self.path_entity_csv_s}"]
        self.show_log_lift(os.linesep.join(ls), True)

    def elab_teimsetid(self):
        if not ptu.exists(self.path_id_in_s):
            self.top_free()
            mbox.showinfo("", f"Before Elab. Entity", parent=self.win0)
            return
        try:
            last = do_main_setid(self.path_id_in_s,
                                 self.path_xmlid_csv_s)
        except SystemExit as e:
            s = f"Errro in set id{os.linesep} {e}"
            log_err.log(s)
            self.show_log_top(s, True)
            return
        ls = ["Elab. Set id",
              f"{self.path_id_in_s}",
              f"{self.path_id_out_s}",
              f"{self.path_xmlid_csv_s}",
              last]
        self.show_log_lift(os.linesep.join(ls), True)

    def elab_teimover(self):
        if not ptu.exists(self.path_over_in_s):
            self.top_free()
            mbox.showinfo("", f"Before Elab. Set id", parent=self.win0)
            return
        try:
            do_main_over(self.path_over_in_s,
                         self.path_over_csv_s)
        except SystemExit as e:
            msg = f"Elaborazione overflow {os.linesep} {e}"
            log_err.log(msg)
            self.show_log_top(msg, True)
            return
        ls = ["Elab. overflow",
              f"{self.path_over_in_s}",
              f"{self.path_over_out_s}",
              f"{self.path_over_csv_s}"]
        self.show_log_lift(os.linesep.join(ls), True)

    def elab_teimnote(self):
        if not ptu.exists(self.path_note_in_s):
            self.top_free()
            mbox.showinfo("", f"Before Elab. Overflow", parent=self.win0)
            return
        try:
            do_main_note(self.path_note_in_s,
                         self.path_note_csv_s)
        except SystemExit as e:
            msg = f"Elab. note {os.linesep} {e}"
            log_err.log(msg)
            self.show_log_top(msg, True)
            return
        ls = ["    Elab. Note",
              f"{self.path_note_in_s}",
              f"{self.path_note_out_s}",
              f"{self.path_note_csv_s}"]
        self.show_log_lift(os.linesep.join(ls), True)
        # format xml
        if not ptu.exists(self.path_xml_in_s):
            self.top_free()
            mbox.showinfo("", f"Error Elab. Note", parent=self.win0)
            return
        src = self.read_file(self.path_xml_in_s)
        self.format_xml(src,
                        self.path_xml_out_s,
                        self.path_xml_err_s,
                        True)

    def elab_tei(self):
        if not ptu.exists(self.path_tei_in_s):
            self.top_free()
            mbox.showinfo("", f"Before Elab. Note", parent=self.win0)
            return
        try:
            # tei_head = self.read_file(self.path_tei_head_s)
            xml = self.read_file(self.path_tei_in_s)
            # src_xml_tei = tei_head.replace(XML_MANO, xml)
            xml_tei = add_tei_head(xml)
        except SystemExit as e:
            msg = f"Elab. XML-TEI {os.linesep} {e}"
            log_err.log(msg)
            self.show_log_top(msg, True)
            return
        ls = ["    Elab. XML-TEI",
              f"{self.path_tei_in_s}",
              f"{self.path_tei_out_s}"]
        self.show_log_lift(os.linesep.join(ls), True)
        # self.write_file(self.path_tei_out_s,xml_tei)
        self.format_xml(xml_tei,
                        self.path_tei_out_s,
                        self.path_tei_err_s,
                        False)

    def format_xml(self, src, path_out, path_err, add_div=True):

        def make_xml_err(xml, err):
            m = re.search(r'(line )([0-9]+)(,)', err)
            if m is not None:
                s = m.group(2)
                n = int(s)
            else:
                n = -1
            rows = xml.split(os.linesep)
            for i, row in enumerate(rows):
                rows[i] = f'{i+1}){row}'
                if i+1 == n:
                    rows[i] = f'\nERRROR\n{rows[i]}\n{err}\n'
            xml_num = os.linesep.join(rows)
            xml_err = "ERROR xml\n"+err+"\n\n"+xml_num
            return xml_err

        try:
            if add_div:
                src = f'<div>{src}</div>'
            src_bytes = src.encode(encoding='utf-8')
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.XML(src_bytes, parser)
            xml = etree.tostring(root,
                                 method='xml',
                                 xml_declaration=False,
                                 encoding='unicode',
                                 with_tail=True,
                                 pretty_print=True,
                                 standalone=None,
                                 doctype=None,
                                 exclusive=False,
                                 inclusive_ns_prefixes=None,
                                 strip_text=False)
        except etree.ParseError as e:
            msg = f"ParseError format_xml()\n{e}"
            set_trace
            log_err.log(msg)
            xml_err = make_xml_err(src, str(e))
            self.show_log_top(xml_err, False)
            self.write_file(path_err, xml_err)
            return
        except Exception as e:
            msg = f"ERROR format_xml()\n{e}"
            log_err.log(msg)
            self.show_log_top(msg, False)
            return
        self.show_win2(xml)
        self.write_file(path_out, xml)

    def elab_xml2txt(self):
        if not ptu.exists(self.path_xml2txt_in_s):
            self.top_free()
            mbox.showinfo("", f"Before Elab. Note", parent=self.win0)
            return
        try:
            do_main_xml2txt(self.path_xml2txt_in_s,
                            self.path_xml2txt_out_s)
        except SystemExit as e:
            msg = f"ERROR Elab. xml2txt()\n{e} "
            log_err.log(msg)
            self.show_log_top(msg, True)
            return
        ls = ["XML => text",
              f"{self.path_xml2txt_in_s}",
              f"{self.path_xml2txt_out_s}"]
        self.show_log_lift(os.linesep.join(ls), True)

        #text = self.read_file(self.path_xml2txt_out_s)
        # self.show_win2(text)

    def elab_all(self):
        self.remove_log()
        self.elab_teimxml()
        self.elab_teimsetid()
        self.elab_teimover()
        self.elab_teimnote()
        self.elab_tei()
        self.elab_xml2txt()

    ##############
    # UA menu del
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
        path_lst = ptu.list_path(self.log_dir_p)
        for p in path_lst:
            p.unlink()

    ##############
    # UA menu log
    ##############

    def show_checktxt(self):
        self.read_log_file(self.path_checktxt_out_s)

    def show_checkover(self):
        self.read_log_file(self.path_checkover_out_s)
    #

    def show_entity_out(self):
        self.read_log_file(self.path_teim_out_s)

    def show_entity_log(self):
        self.read_log_file(self.path_teim_log_s)

    def show_entity_err(self):
        self.read_log_file(self.path_teim_err_s)
    #

    def show_setwid_out(self):
        format_path=self.path_id_out_s.replace("_id.xml","_id_format.xml")
        #AAA self.read_log_file(self.path_id_out_s)
        self.read_log_file(format_path)

    def show_setwid_log(self):
        self.read_log_file(self.path_id_log_s)

    def show_setwid_err(self):
        self.read_log_file(self.path_id_err_s)
    #

    def show_over_out(self):
        format_path=self.path_over_out_s.replace("_over.xml","_over_format.xml")
        #AAA self.read_log_file(self.path_over_out_s)
        self.read_log_file(format_path)

    def show_over_log(self):
        self.read_log_file(self.path_over_log_s)

    def show_over_err(self):
        self.read_log_file(self.path_over_err_s)
    #

    def show_note_out(self):
        format_path=self.path_over_note_s.replace("_note.xml","_note_format.xml")
        #AAA self.read_log_file(self.path_note_out_s)
        self.read_log_file(format_path)

    # def show_note_log(self):
    #     self.read_log_file(self.path_note_log_s)

    def show_note_err(self):
        self.read_log_file(self.path_note_err_s)
    #

    def show_xml_out(self):
        self.read_log_file(self.path_xml_out_s)

    def show_xml_err(self):
        self.read_log_file(self.path_xml_err_s)
    #

    def show_tei_out(self):
        self.read_log_file(self.path_tei_out_s)

    def show_tei_err(self):
        self.read_log_file(self.path_tei_err_s)
    #

    def show_xml2txt_out(self):
        self.read_log_file(self.path_xml2txt_out_s)

    def show_xml2txt_err(self):
        self.read_log_file(self.path_xml2txt_err_s)
    #

    def show_edit_err(self):
        self.read_log_file(self.path_edit_err_s)

    def open_log(self):
        self.top_free()
        path = fdialog.askopenfilename(
            parent=self.win0,
            title='log',
            initialdir=self.log_dir_p,
            filetypes=[("all", "*.*"),
                       ("log", "*.log"),
                       ("text", "*.txt"),
                       ("xml", "*.xml")])
        if len(path) < 1:
            return
        # controllo probabilmente inutile
        path = ptu.str2path(path)
        if path.exists():
            s = self.read_file(path)
            self.show_log_top(s)
        else:
            self.top_free()
            mbox.showinfo("", f"Not Foud", parent=self.win0)

    #############
    # UA menu help
    ############
    def help_paths(self):
        self.show_psths()
        self.top_w3()

    def show_psths(self):
        try:
            wrk_dir = ptu.path2str(self.pwd)
            # parent_teimcfg = self.parent_teimcfg_p.absolute()
            teimcfg = ptu.path2str(self.path_teimcfg_p.absolute())
            # root_dir = self.root_dir_p.absolute()
            info = [
                "===========================",
                f"FILE TEXT      : {self.path_text_s}",
                "===========================",
                f"match          : {self.path_match_s}",
                f"work dir       : {wrk_dir}  ",
                f"teimcfg        : {teimcfg}",
                "---------------------------",
                f"teimed tags    : {self.path_entity_csv_s}",
                f"overflow tags  : {self.path_over_csv_s}",
                f"xmlid tags     : {self.path_xmlid_csv_s}",
                f"note           : {self.path_note_csv_s}",
                "---------------------------",
                f"chek  txt      : {self.path_checktxt_out_s}",
                f"check over     : {self.path_checkover_out_s}",
                "",
                f"elab  entity   : {self.path_teim_out_s}",
                f"log   entity   : {self.path_teim_log_s}",
                f"ERR   entity   : {self.path_teim_err_s}",
                "",
                f"elab  set id   : {self.path_id_out_s}",
                f"log   set id   : {self.path_id_log_s}",
                f"ERR   set id   : {self.path_id_err_s}",
                "",
                f"elab  over     : {self.path_over_out_s}",
                f"log   over     : {self.path_over_log_s}",
                f"ERR   over     : {self.path_over_err_s}",
                "",
                f"elab  note     : {self.path_note_out_s}",
                f"ERR   note     : {self.path_note_err_s}",
                "",
                f"elab  XML      : {self.path_xml_out_s}",
                f"ERR   XML      : {self.path_xml_err_s}",
                "===========================",
                f"elab  XML-TEI  : {self.path_tei_out_s}",
                f"ERR   XML-TEI  : {self.path_tei_err_s}",
                "===========================",
                f"elab  text     : {self.path_xml2txt_out_s}",
                f"err   text     : {self.path_xml2txt_err_s}",
                "---------------------------",
            ]
            s = os.linesep.join(info)
            self.show_log(s)
        except Exception as e:
            log_err.log(e)
            raise(Exception(f"ERROR show_paths()\{e}"))

    def help_options(self):
        s = HELP_RUN_OPS()
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
            r = os.linesep.join(["", "", msg])
            self.txt3.insert(tk.END, r)
            self.txt3.see(tk.END)
        else:
            r = os.linesep.join(["", msg])
            self.txt3.delete('1.0', tk.END)
            self.txt3.insert('1.0', r)

    #################################
    # UA rc
    ################################

    def rc_get_recenti(self):
        lst = rc.get(RC_RECENTI, [])
        return lst

    def rc_update(self):
        path = self.path_text_s
        lst = rc.get(RC_RECENTI, [])
        lst.append(path)
        lst = list(set(lst))
        rc.set('recenti', lst)
        rc.set(RC_PATH_LAST, self.path_text_s)
        # rc.prn('update')

    def rc_save(self):
        # 3 73
        # 1000x600+56+196",
        # 1000  500+50+196
        # widthxheight*X*Y
        def geometry(win):
            wg = win.winfo_geometry()
            wd, hxy = wg.split('x')
            he, x, y = hxy.split('+')
            if os_name == 'linux':
                x = str(int(x)-3)
                y = str(int(y)-73)
            return f'{wd}x{he}+{x}+{y}'

        rc.set('win0', geometry(self.win0))
        rc.set('win1', geometry(self.win1))
        rc.set('win2', geometry(self.win2))
        rc.set('win3', geometry(self.win3))
        rc.set(RC_PARENT_TEIMCFG, self.parent_teimcfg_s)
        self.rc_update()
        rc.save()
        # rc.prn("save")


def do_main(parent_teimcfg, root_dir, path_match):
    rc.load()
    # rc.prn("rc.load")
    if parent_teimcfg is None:
        parent_teimcfg = rc.get_val(RC_PARENT_TEIMCFG)
    if path_match is None:
        path_match = rc.get_val(RC_PATH_LAST)
    if path_match is None and parent_teimcfg is None:
        return
    tme = TeimEdit(parent_teimcfg, root_dir, path_match)
    tme.open_win0()


def prn_help():
    print(HELP_RUN_OPS())


if __name__ == "__main__":
    le = len(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',
                        dest="parent_cfg",
                        required=False,
                        default=None,
                        type=str,
                        metavar="teimcfg ancestor",
                        help="-c <dir_ancestor_of_teimcfg>")
    parser.add_argument('-t',
                        dest="path_match",
                        required=False,
                        default=None,
                        type=str,
                        metavar="files match",
                        help="-t <file>.txt / <files_ match>")
    parser.add_argument('-x',
                        action="store_true",
                        required=False,
                        help="-x => print Help")
    parser.add_argument('-e',
                        action="store_true",
                        required=False,
                        help="-e => delete history")
    args = parser.parse_args()
    # set_trace()
    if le == 1:
        if rc.is_empty():
            print(f"\nauthor: {__author__}")
            print(f"{__date__} { __version__}")
            parser.print_help()
            sys.exit()
        # do_main(None, PATH_ROOT_DIR, None)
    if args.x:
        prn_help()
        sys.exit()
    if args.e:
        rc.remove()
    if args.path_match:
        args.path_match = args.path_match.replace('$', '*')

    print(f"{__date__} { __version__}")
    do_main(args.parent_cfg, PATH_ROOT_DIR, args.path_match)
