#!/usr/bin/env python3
# coding: utf-8

from pdb import set_trace
from teimxml import do_main as do_main_xml
from teimsetid import do_main as do_main_setid
from teimover import do_main as do_main_over
from teimnote import do_main as do_main_note
from checktxt import do_main as do_main_checktxt
from checkover import do_main as do_main_checkover
import os
import tkinter as tk
from tkinter.font import Font
import tkinter.filedialog as fdialog
from tkinter import END
from ualog import Log
import sys
import json
from lxml import etree
import stat

__date__ = "30-03-2021"
__version__ = "0.11.0"
__author__ = "Marta Materni"

logediterr = Log("w")

help = """
base_dir/text_dir/teim.txt
base_dir/text_dir/note.csv
base_dir/text_dir/teim.xml

base_di/cfg/teimed.csv
base_dir/cfg/overflow.csv

base_dir/text_dir/log_dir/teim_1.txt
base_dir/text_dir/log_dir/teim_2.xml
base_dir/text_dir/teim.xml

"""
TEIMED_CFG = "teimedit.json"
CFG = {
    "base_dir": "",

    "text_dir": "teim",
    "text_src": "teim.txt",
    "text_sign": "K",
    "text_note": "note.csv",

    "log_dir": "txt",
    "cfg_dir": "cfg",
    "teimed_tag": "teimed.csv",
    "overflow_tag": "overflow.csv"
}

dx = 100
dy = 50
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

BG_WIN = "#000000"
FG_WIN = "#00FF00"

BG_MENU = "#333333"
FG_MENU = "#00ff00"
BG2_MENU = "#555555"
FG2_MENU = "#ffff00"

# BG_CMD = "#333333"
# FG_CMD = "#0000ff"

BG_SEP = "#111111"
FG_SEP = "#FFFFFF"

BG_TEXT = "#333333"
FG_TEXT = "#ffffff"
CURS_TEXT = "#00ff00"

BG_LOG = "#000000"
FG_LOG = "#ffff00"

FONT_GENERAL = ('Arial', 14, 'normal')
FONT_EDIT = ('Arial', 14, 'normal')
# FONT_MENU = Font(family="Arial", size=12)
FONT_MENU = ('Arial', 16, 'normal')


class TeimEdit(object):

    def __init__(self, config_name):
        logediterr.open("log/teimedit.log", 1)
        self.base_dir = ""
        self.text_dir = ""
        self.cfg_dir = ""
        self.log_dir = ""
        self.ext_src = None
        self.text_sign = None
        #
        self.path_teimed_tag = ""
        self.path_over_tag = None
        self.path_text_note = None
        self.path_text = ""
        self.path_xml = None
        self.path_xml_format = None
        self.path_entity_txt = None
        self.path_id_xml = None
        self.path_fromto_xml = None
        self.path_check_txt = None
        self.path_check_over = None
        self.path_tmp = None
        #
        self.win0 = None
        self.txt0 = None
        self.win1 = None
        self.txt1 = None
        self.win2 = None
        self.txt2 = None
        self.win3 = None
        self.txt3 = None
        if config_name is None:
            self.config_name = TEIMED_CFG
        else:
            self.config_name = config_name
        self.config = None
        self.init_config()

    def init_config(self):
        """ se il config noin esiste:
        setta self.config=CFG
        e salva il file config con il nome self.config_name
        """
        if not os.path.exists(self.config_name):
            self.config = CFG
            self.write_config()
        self.chmod(self.config_name)
        self.read_config()
        self.set_config()

    def read_config(self):
        try:
            with open(self.config_name, "r") as f:
                txt = f.read()
            self.config = json.loads(txt)
        except Exception as e:
            print(f"ERROR rtead_config {self.config_name}")
            print(e)
            sys.exit(1)

    def write_config(self):
        js = self.config
        s = json.dumps(js, indent=2)
        with open(self.config_name, "w+") as f:
            f.write(s)
        self.chmod(self.config_name)

    def update_config(self, text_src):
        self.config_name = text_src.replace(".txt", ".json")
        self.config["text_src"] = text_src
        self.write_config()

    def make_dirs(self):
        self.make_dir(self.base_dir)
        self.make_dir(self.text_dir)
        self.make_dir(self.cfg_dir)
        self.make_dir(self.log_dir)

    def make_dir(self, dirname):
        if len(dirname.strip()) == 0:
            return
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        self.chmod(dirname)

    def file_exists(self, path):
        return os.path.exists(path)

    def chmod(self, parh):
        os.chmod(parh, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)

    def get_text_path(self, name):
        text_path = os.path.join(self.text_dir, name)
        return text_path

    def get_cfg_path(self, name):
        cfg_path = os.path.join(self.cfg_dir, name)
        return cfg_path

    def get_log_path(self, name):
        log_path = os.path.join(self.log_dir, name)
        return log_path

    def write_file(self, path, s):
        with open(path, 'w') as f:
            f.write(s)
        self.chmod(path)

    def read_file(self, path):
        with open(path, 'rt') as f:
            s = f.read()
        return s

    def set_config(self):
        js = self.config
        try:
            self.base_dir = js["base_dir"]
            text_dir = js["text_dir"]
            cfg_dir = js["cfg_dir"]
            log_dir = js["log_dir"]
            text_sign = js["text_sign"]
            text_src = js["text_src"]
            text_note = js["text_note"]
            teimed_tag = js["teimed_tag"]
            overflow_tag = js["overflow_tag"]
            #
            self.text_src = text_src
            self.text_dir = os.path.join(self.base_dir, text_dir)
            self.cfg_dir = os.path.join(self.base_dir, cfg_dir)
            self.log_dir = os.path.join(self.text_dir, log_dir)
            self.make_dirs()
            #
            self.path_teimed_tag = self.get_cfg_path(teimed_tag)
            self.path_over_tag = self.get_cfg_path(overflow_tag)
            #
            self.path_text_note = self.get_text_path(text_note)
            self.text_sign = text_sign
            self.set_path_files(text_src)
        except Exception as e:
            s = str(e)
            logediterr.log(f"ERROR  config {self.config_name}")
            logediterr.log(s)
            sys.exit(1)

    def set_path_files(self, text_src):
        self.path_text = self.get_text_path(text_src)

        name = text_src.replace(".txt", ".xml")
        self.path_xml = self.get_text_path(name)

        name = text_src.replace(".txt", "_F.xml")
        self.path_xml_format = self.get_text_path(name)
        #
        name = text_src.replace(".txt", "_MED_.txt")
        self.path_entity_txt = self.get_log_path(name)

        name = text_src.replace(".txt", "_WID.xml")
        self.path_id_xml = self.get_log_path(name)

        name = text_src.replace(".txt", "_OVER.xml")
        self.path_fromto_xml = self.get_log_path(name)

        self.path_tmp = self.get_log_path('tmp')
        #
        name = self.text_src.replace(".txt", "CHECK_TXT.txt")
        self.path_check_txt = self.get_log_path(name)

        name = self.text_src.replace(".txt", "CHECK_OVER.txt")
        self.path_check_over = self.get_log_path(name)

    #####################################################

    def open_win0(self):
        # win0
        self.win0 = tk.Tk()
        self.show_title()
        self.win0.option_add('*Font', FONT_GENERAL)
        self.win0.rowconfigure(0, weight=1)
        self.win0.columnconfigure(0, weight=1)
        self.win0.geometry('%dx%d+%d+%d' % (w0_w, w0_h, w0_x, w0_y))
        self.win0.protocol("WM_DELETE_WINDOW", self.quit)
        self.win0.config(background=BG_WIN)
       #
        self.txt0 = tk.Text(self.win0)
        self.txt0.grid(sticky='nsew')
        self.txt0.configure(
            insertbackground=CURS_TEXT,
            font=FONT_EDIT,
            bg=BG_TEXT,
            fg=FG_TEXT)
        #
        menu_bar = tk.Menu(self.win0)
        menu_bar.config(
            font=FONT_MENU,
            bg=BG_MENU,
            fg=FG_MENU,
            activebackground=BG2_MENU,
            activeforeground=FG2_MENU,
            relief="raised")
        self.win0.config(menu=menu_bar)

        mv_file = tk.Menu(menu_bar)
        mv_file.config(
            font=FONT_MENU,
            bg=BG_MENU,
            fg=FG_MENU,
            activebackground=BG2_MENU,
            activeforeground=FG2_MENU,
            relief="raised")
        mv_file.add_command(label='Open', command=self.open_text)
        mv_file.add_command(label='Save', command=self.save_text)
        mv_file.add_command(label='Save As...', command=self.save_text_as)
        mv_file.add_separator()
        mv_file.add_command(label='Exit', command=self.quit)

        mv_check = tk.Menu(menu_bar)
        mv_check.config(
            font=FONT_MENU,
            bg=BG_MENU,
            fg=FG_MENU,
            activebackground=BG2_MENU,
            activeforeground=FG2_MENU,
            relief="raised")
        mv_check.add_command(label='Check Entity',
                             command=self.elab_checktxt)
        mv_check.add_command(label='Check Overflow',
                             command=self.elab_checkover)

        mv_elab = tk.Menu(menu_bar)
        mv_elab.config(
            font=FONT_MENU,
            bg=BG_MENU,
            fg=FG_MENU,
            activebackground=BG2_MENU,
            activeforeground=FG2_MENU,
            relief="raised")
        mv_elab.add_command(label='Elab. Entity', command=self.elab_teimxml)
        mv_elab.add_command(label='Elab. XML', command=self.elab_teimlw)

        mv_del = tk.Menu(menu_bar)
        mv_del.config(
            font=FONT_MENU,
            bg=BG_MENU,
            fg=FG_MENU,
            activebackground=BG2_MENU,
            activeforeground=FG2_MENU,
            relief="raised")
        mv_del.add_command(label='Entity', command=self.delete_txt1)
        mv_del.add_command(label='XML', command=self.delete_txt2)
        mv_del.add_command(label='Log', command=self.delete_txt3)
        mv_del.add_separator()
        mv_del.add_command(label='Remove log file', command=self.remove_log)
        # orizontale
        menu_bar.add_cascade(label='File', menu=mv_file)
        menu_bar.add_command(
            background=BG_SEP, activeforeground=FG_SEP, label=' ')

        menu_bar.add_cascade(label='Check', menu=mv_check)
        menu_bar.add_command(
            background=BG_SEP, activeforeground=FG_SEP, label=' ')

        menu_bar.add_cascade(label='Elab.', menu=mv_elab)
        menu_bar.add_command(
            background=BG_SEP, activeforeground=FG_SEP, label=' ')

        menu_bar.add_cascade(label='Cancella', menu=mv_del)
        menu_bar.add_command(
            background=BG_SEP, activeforeground=FG_SEP, label='         ')

        menu_bar.add_command(label="SAVE", command=self.save_text)
        menu_bar.add_command(background=BG_SEP,
                             activeforeground=FG_SEP, label=' ')

        menu_bar.add_command(label='RELOAD', command=self.reload_text)
        menu_bar.add_command(
            background=BG_SEP, activeforeground=FG_SEP, label=' ')

        menu_bar.add_command(label='Log', command=self.open_log)
        menu_bar.add_command(
            background=BG_SEP, activeforeground=FG_SEP, label=' ')

        menu_bar.add_command(label='Info', command=self.show_info)

        self.show_win1("")
        self.show_win2("")
        s = self.get_path_lst_log()
        self.write_log(s)
        self.read_text_file()
        tk.mainloop()

    def open_win1(self):
        if self.win1 is not None:
            return
        win = tk.Tk()
        win.title('ENTITY')
        win.rowconfigure(0, weight=1)
        win.columnconfigure(0, weight=1)
        win.geometry('%dx%d+%d+%d' % (w1_w, w1_h, w1_x, w1_y))
        self.win1 = win
        self.win1.protocol("WM_DELETE_WINDOW", self.quit1)
        self.txt1 = tk.Text(self.win1)
        self.txt1.grid(sticky='nsew')
        self.txt1.configure(font=FONT_EDIT, bg=BG_TEXT, fg=FG_TEXT)

    def open_win2(self):
        if self.win2 is not None:
            return
        win = tk.Tk()
        win.title('XML')
        win.rowconfigure(0, weight=1)
        win.columnconfigure(0, weight=1)
        win.geometry('%dx%d+%d+%d' % (w2_w, w2_h, w2_x, w2_y))
        self.win2 = win
        self.win2.protocol("WM_DELETE_WINDOW", self.quit2)
        self.txt2 = tk.Text(self.win2)
        self.txt2.grid(sticky='nsew')
        self.txt2.configure(font=FONT_EDIT, bg=BG_TEXT, fg=FG_TEXT)

    def open_win3(self):
        if self.win3 is not None:
            return
        self.win3 = tk.Tk()
        self.win3.title('LOG')
        self.win3.rowconfigure(0, weight=1)
        self.win3.columnconfigure(0, weight=1)
        self.win3.geometry('%dx%d+%d+%d' % (w3_w, w3_h, w3_x, w3_y))
        self.win3.protocol("WM_DELETE_WINDOW", self.quit3)
        self.txt3 = tk.Text(self.win3)
        self.txt3.grid(sticky='nsew')
        self.txt3.configure(font=FONT_EDIT, bg=BG_LOG, fg=FG_LOG)

    def show_title(self):
        text_src = os.path.basename(self.path_text)
        title = f"TEXT: {text_src} "
        self.win0.title(title)

    def get_path_lst_log(self):
        logs = [
            "  ",
            f" text : {self.path_text}",
            f" sigla.: {self.text_sign}",
            f" note : {self.path_text_note}",
            f" tei_tags : {self.path_teimed_tag}",
            f" over_tags : {self.path_over_tag}",
            "---------"
            " ",
            f"check txt {self.path_check_txt}",
            f"check over {self.path_check_over}",
            "---------"
            " ",
            f"+ entity: {self.path_entity_txt}",
            f"+ id: {self.path_id_xml}",
            f"+ ovver: {self.path_fromto_xml}",
            f"+ note: {self.path_xml}",
            "---------"
            " ",
        ]
        s = os.linesep.join(logs)
        return s

    def elab_teimxml(self):
        s = self.txt0.get('1.0', 'end')
        self.write_file(self.path_text, s)
        do_main_xml(self.path_text,
                    self.path_teimed_tag,
                    self.path_entity_txt)
        self.chmod(self.path_entity_txt)
        s = self.read_file(self.path_entity_txt)
        self.show_win1(s)

    def elab_teimlw(self):
        if not self.file_exists(self.path_entity_txt):
            self.write_log("Elaborare Entity")
            return
        # path_txt_1 => path_xml_1
        do_main_setid(self.path_entity_txt,
                      self.path_id_xml,
                      self.text_sign)
        self.chmod(self.path_id_xml)
        # path_xml_1 => path_xml_2
        do_main_over(self.path_id_xml,
                     self.path_fromto_xml,
                     self.path_over_tag)
        self.chmod(self.path_fromto_xml)
        # path_xml_2 => path_xml
        do_main_note(self.path_fromto_xml,
                     self.path_xml,
                     self.path_text_note)
        self.chmod(self.path_xml)
        s = self.read_file(self.path_xml)
        self.format_xml()

    def format_xml(self):
        s = self.read_file(self.path_xml)
        xml = '<div>'+s+'</div>'
        self.write_file(self.path_tmp, xml)
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.parse(self.path_tmp, parser)
            src = etree.tostring(root,
                                 method='xml',
                                 xml_declaration=None,
                                 encoding='unicode',
                                 with_tail=True,
                                 pretty_print=True)
            self.show_win2(src)
            self.write_file(self.path_xml_format, src)
        except etree.Error as e:
            s = str(e)
            print(s)
            msg = "ERROR XML"+os.linesep+s
            self.write_log(msg)

    def elab_checktxt(self):
        s = self.txt0.get('1.0', 'end')
        self.write_file(self.path_tmp, s)
        do_main_checktxt(self.path_tmp,
                         self.path_check_txt)
        self.chmod(self.path_check_txt)

    def elab_checkover(self):
        s = self.txt0.get('1.0', 'end')
        self.write_file(self.path_tmp, s)
        do_main_checkover(self.path_tmp,
                          self.path_over_tag,
                          self.path_check_over)
        self.chmod(self.path_check_over)

    def quit1(self):
        self.win1.destroy()
        self.win1 = None

    def show_win1(self, s):
        self.open_win1()
        self.txt1.delete('1.0', END)
        self.txt1.insert('1.0', s)

    def quit2(self):
        self.win2.destroy()
        self.win2 = None

    def show_win2(self, s):
        self.open_win2()
        self.txt2.delete('1.0', END)
        self.txt2.insert('1.0', s)

    def quit3(self):
        self.win3.destroy()
        self.win3 = None

    def write_log(self, s, append=False):
        self.open_win3()
        if append:
            x = self.txt3.get('1.0', 'end')
            s = x+os.linesep+s
        self.txt3.delete('1.0', END)
        self.txt3.insert('1.0', s)

    def delete_text_all(self):
        # self.txt0.delete('1.0', END)
        self.delete_txt1()
        self.delete_txt2()
        self.delete_txt3()

    def delete_txt1(self):
        if self.txt1 is not None:
            self.txt1.delete('1.0', END)
        self.delete_txt2()

    def delete_txt2(self):
        if self.txt2 is not None:
            self.txt2.delete('1.0', END)

    def delete_txt3(self):
        if self.txt3 is not None:
            self.txt3.delete('1.0', END)

    def remove_log(self):
        files = os.listdir(self.log_dir)
        for f in files:
            path=os.path.join(self.log_dir,f)
            absp=os.path.abspath(path)
            print(absp)
            os.remove(absp)

    def quit(self):
        self.win0.quit()
        if self.win1 is not None:
            self.win1.quit()
        if self.win2 is not None:
            self.win2.quit()
        if self.win3 is not None:
            self.win3.quit()

    def reload_text(self):
        self.read_text_file()

    def open_text(self):
        path = fdialog.askopenfilename(
            title=' file',
            initialdir=self.text_dir,
            filetypes=[("text", "*.txt"),
                       ("xml", "*.xml")])
        if len(path) < 1:
            return
        text_src = os.path.basename(path)
        if text_src != self.text_src:
            if not self.file_exists(path):
                self.update_config(text_src)
        self.set_path_files(text_src)
        s = self.get_path_lst_log()
        self.write_log(s)
        self.read_text_file()

    def read_text_file(self):
        if self.file_exists(self.path_text):
            s = self.read_file(self.path_text)
        else:
            s = "Not Found."
        self.txt0.delete('1.0', END)
        self.txt0.insert('1.0', s)
        self.show_title()

    def open_log(self):
        path = fdialog.askopenfilename(
            title='log',
            initialdir=self.log_dir,
            filetypes=[("log", "*.log"),
                       ("text", "*.txt"),
                       ("xml", "*.xml")])
        if len(path) > 0:
            self.read_log_file(path)

    def read_log_file(self, path):
        if self.file_exists(path):
            s = self.read_file(path)
        else:
            s = "Not Found."
        self.win3 = None
        self.open_win3()
        self.txt3.delete('1.0', END)
        self.txt3.insert('1.0', s)

    def show_info(self):
        self.win3 = None
        self.open_win3()
        s = self.get_path_lst_log()
        self.write_log(s)

    def save_text_as(self):
        path = fdialog.asksaveasfilename(title='Dove Salvare')
        if len(path) < 1:
            return
        s = self.txt0.get('1.0', 'end')
        name = os.path.basename(path)
        self.update_config(name)
        self.set_path_files(name)
        self.write_file(self.path_text, s)
        s = self.get_path_lst_log()

    def save_text(self):
        s = self.txt0.get('1.0', 'end')
        self.write_file(self.path_text, s)


def do_main(config_name=None):
    tme = TeimEdit(config_name)
    tme.open_win0()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"author: {__author__}")
        print(f"release: {__version__} { __date__}")
        path_config = None
    else:
        path_config = sys.argv[1]
    do_main(path_config)
