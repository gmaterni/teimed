#!/usr/bin/env python3
# coding: utf-8

from pdb import set_trace

from teimlib.teimstyle import *
from teimlib.textlinenumbers import TextLineNumbers
from teimlib.textpad import TextPad

import argparse
from teimxml import do_main as do_main_xml
from teimsetid import do_main as do_main_setid
from teimover import do_main as do_main_over
from teimnote import do_main as do_main_note
from checktxt import do_main as do_main_checktxt
from checkover import do_main as do_main_checkover
import os
import tkinter as tk
#from tkinter.font import Font
import tkinter.filedialog as fdialog
from ualog import Log
import json
from lxml import etree
import stat
import sys 
import pprint

__date__ = "13-04-2021"
__version__ = "0.145.0"
__author__ = "Marta Materni"


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
TEIMED_CFG = "teim.json"
CFG = {
    "base_dir": "",

    "text_dir": "teim",
    "text_src": "teim.txt",
    "text_sign": "K",
    "text_note": "note.csv",

    "log_dir": "log",
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


def pp(data,w=60):
    return pprint.pformat(data,width=w)

logediterr = Log("w")

class TeimEdit(object):

    def __init__(self,
                 json_name="",
                 new_json_name="",
                 text_dir="",
                 text_src="",
                 text_sign=""):
        logediterr.open("log/teimedit.log", 1)
        self.base_dir = ""

        self.json_name = json_name
        self.new_json_name = new_json_name
        self.text_dir = text_dir
        self.text_src = text_src
        self.text_sign = text_sign

        self.cfg_dir = ""
        self.log_dir = ""
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
        self.text_edit=None
        self.win1 = None
        self.txt1 = None
        self.win2 = None
        self.txt2 = None
        self.win3 = None
        self.txt3 = None
        self.config_json = None
        self.init_config()

    def check_config_name(self):
        p = self.json_name.find('.json')
        if p < 0:
            print("")
            print("Error!")
            print("file config NOT json")
            sys.exit()

    def customize_config(self):
        if self.text_dir != "":
            self.config_json['text_dir'] = self.text_dir
        if self.text_src != "":
            self.config_json['text_src'] = self.text_src
        if self.text_sign != "":
            self.config_json['text_sign'] = self.text_sign
            
    def chek_config_exists(self):
        if not os.path.exists(self.json_name):
            print("")
            print(f"{self.json_name} Not Found.")
            sys.exit()

    def init_config(self):
        if self.new_json_name!='':
            self.config_json = CFG
            self.json_name = self.new_json_name
            self.check_config_name()
            self.customize_config()
            self.write_config()
            self.chmod(self.json_name)
        self.check_config_name()
        self.chek_config_exists()
        self.read_config()
        self.customize_config()
        self.set_config()

    def read_config(self):
        print(self.json_name)
        try:
            s=open(self.json_name, "r").read()
            self.config_json = json.loads(s)
        except Exception as e:
            print(f"ERROR in {self.json_name}")
            print(e)
            sys.exit(1)

    def write_config(self):
        js = self.config_json
        s = json.dumps(js, indent=2)
        with open(self.json_name, "w+") as f:
            f.write(s)
        self.chmod(self.json_name)

    def update_config(self, text_src):
        self.json_name = text_src.replace(".txt", ".json")
        self.config_json["text_src"] = text_src
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

    def chmod(self, path):
        if os.path.exists(path)is False:
            self.write_log(f"File {path} Not Exists")
            return
        try:
            os.chmod(path, stat.S_IRWXG + stat.S_IRWXU + stat.S_IRWXO)
        except Exception as e:
            logediterr.log(f"ERROR. File Not Found.")
            logediterr.log(str(e))
            self.write_log(f"File {path} Not Exists")
            self.top_w3()

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
        s=open(path, 'rt').read()
        return s

    def set_config(self):
        js = self.config_json
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
            logediterr.log(f"ERROR in {self.json_name}")
            logediterr.log(s)
            print(pp(self.config_json))
            sys.exit(1)

    def set_path_files(self, text_src):
        self.path_text = self.get_text_path(text_src)

        name = text_src.replace(".txt", ".xml")
        self.path_xml = self.get_text_path(name)

        name = text_src.replace(".txt", "_F.xml")
        self.path_xml_format = self.get_text_path(name)
        #
        name = text_src.replace(".txt", "_MED.txt")
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

    
    def open_win0(self):
        self.win0 = tk.Tk()
        self.win0.title("TeiMed Edit")
        self.win0.rowconfigure(0, weight=1)
        self.win0.columnconfigure(0, weight=1)
        self.win0.geometry('%dx%d+%d+%d' % (w0_w, w0_h, w0_x, w0_y))
        self.win0.config(background=BG_WIN)
        #
        self.text_edit=TextLineNumbers(self.win0)          
        self.text_edit.configure(bg=BG_TXT,fg=FG_TXT,font=FONT_EDIT)
        self.text_edit.lnumbers.config(background=BG_LNUM)
        self.text_edit.config(cursor='arrow')   
        self.text_edit.config(insertbackground=BG_CURS)
        ##self.text_pad.config(insertborderwidth=1)
        self.text_edit.config(insertofftime=300)
        self.text_edit.config(insertwidth=3)
        
        self.text_edit.focus_set()

        self.win0.protocol("WM_DELETE_WINDOW",lambda  : False)
        #
        menu_bar = tk.Menu(self.win0,tearoff=0)
        menu_bar.config(
            font=FONT_MENU,
            bg=FG_MENU,
            fg=MENU_FG,
            activebackground=BG2_MENU,
            activeforeground=FG2_MENU,
            bd=1,
            relief="raised")
        self.win0.config(menu=menu_bar)
        #
        mv_file = tk.Menu(menu_bar,tearoff=0)
        mv_file.config(
            font=FONT_MENU,
            bg=FG_MENU,
            fg=MENU_FG,
            activebackground=BG2_MENU,
            activeforeground=FG2_MENU,
            relief="raised")
        mv_file.add_command(label='Reload',command=self.reload_text,underline=0)
        mv_file.add_separator()
        mv_file.add_command(label='Open  Ctrl+o', command=self.open_text)
        mv_file.add_command(label='Save  Ctrl+s', command=self.save_text)
        mv_file.add_command(label='Save As.. Ctl-Shift-S', command=self.save_text_as)
        mv_file.add_separator()
        mv_file.add_command(label='Exit', command=self.quit,underline=0)
        self.text_edit.bind("<Control-s>", self.save_text)
        self.text_edit.bind("<Control-o>", self.open_text)
        self.text_edit.bind("<Control-Shift-S>", self.save_text_as)
        #
        mv_edit = tk.Menu(menu_bar,tearoff=0)
        mv_edit.config(font=FONT_MENU,
                        bg=FG_MENU,
                        fg=MENU_FG,
                        activebackground=BG2_MENU,
                        activeforeground=FG2_MENU,
                        relief=tk.RAISED)
        mv_edit.add_command(label="Undo     Ctrl-Z", command=self.text_edit.on_undo )
        #mv_edit.add_command(label="Redo     Ctrl-Y", command=self.text_pad.edit_redo)
        mv_edit.add_separator() 
        mv_edit.add_command(label="Cut      Ctrl-X", command=self.text_edit.on_cut) 
        mv_edit.add_command(label="Copy     Ctrl-C", command=self.text_edit.on_copy)
        mv_edit.add_command(label="Paste    Ctrl-V", command=self.text_edit.on_paste)
        #
        mv_check = tk.Menu(menu_bar,tearoff=0)
        mv_check.config(font=FONT_MENU,
                        bg=FG_MENU,
                        fg=MENU_FG,
                        activebackground=BG2_MENU,
                        activeforeground=FG2_MENU,
                        relief=tk.RAISED)
        mv_check.add_command(label='Check Entity', command=self.elab_checktxt)
        mv_check.add_command(label='Check Overflow', command=self.elab_checkover)
        #
        mv_elab = tk.Menu(menu_bar,tearoff=0)
        mv_elab.config(font=FONT_MENU,
                        bg=FG_MENU,
                        fg=MENU_FG,
                        activebackground=BG2_MENU,
                        activeforeground=FG2_MENU,
                        relief=tk.RAISED)
        mv_elab.add_command(label='Elab. Entity', command=self.elab_teimxml)
        mv_elab.add_command(label='Elab. Set id', command=self.elab_teimlw)
        mv_elab.add_command(label='Elab. Overflow', command=self.elab_teimover)
        mv_elab.add_command(label='Elab. Note', command=self.elab_teimnote)
        #
        mv_log = tk.Menu(menu_bar,tearoff=0)
        mv_log.config(font=FONT_MENU,
                      bg=FG_MENU,
                      fg=MENU_FG,
                      activebackground=BG2_MENU,
                      activeforeground=FG2_MENU,
                      relief=tk.RAISED)
        mv_log.add_command(label='Check Txt Err.', command=self.show_check_txt)
        mv_log.add_command(label='Check Over Err.', command=self.show_check_over)
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
        mv_log.add_command(label='Read Log.', command=self.open_log)
        #
        mv_del = tk.Menu(menu_bar,tearoff=0)
        mv_del.config(font=FONT_MENU,
                      bg=FG_MENU,
                      fg=MENU_FG,
                      activebackground=BG2_MENU,
                      activeforeground=FG2_MENU,
                      relief=tk.RAISED)
        mv_del.add_command(label='Entity', command=self.delete_txt1)
        mv_del.add_command(label='XML', command=self.delete_txt2)
        mv_del.add_command(label='Log', command=self.delete_txt3)
        mv_del.add_separator()
        mv_del.add_command(label='Remove log file', command=self.remove_log)
        # orizontale
        menu_bar.add_cascade(label='File', menu=mv_file,underline=0)
        menu_bar.add_cascade(label='Edit', menu=mv_edit,underline=0)
        menu_bar.add_cascade(label='Check', menu=mv_check,underline=0)
        menu_bar.add_cascade(label='Elab.', menu=mv_elab,underline=1)
        menu_bar.add_cascade(label='Log. ', menu=mv_log,underline=0)
        menu_bar.add_cascade(label='Del.', menu=mv_del,underline=0)
        menu_bar.add_separator(background='#ff0000')
        menu_bar.add_command(label='Info', command=self.show_info,underline=0)
        menu_bar.add_command(label='  Window 1-2-3-4 ', command=self.top_order)
        menu_bar.add_command(label='  1  ', command=self.top_w0)
        menu_bar.add_command(label='  2  ', command=self.top_w1)
        menu_bar.add_command(label='  3  ', command=self.top_w2)
        menu_bar.add_command(label='  4  ', command=self.top_w3)
        #############
        #text = self.config['text_src']
        self.show_win1("")
        self.show_win2("")
        self.show_win3("")
        s = self.get_path_lst_log()
        self.write_log(s)
        self.read_text_file()
        ##############
        tk.mainloop()
        ##############

    def top_w0(self):
        self.top_not()
        self.win0.attributes("-topmost",True)

    def top_w1(self):
        self.top_not()
        self.win1.attributes("-topmost",True)

    def top_w2(self):
        self.top_not()
        self.win2.attributes("-topmost",True)

    def top_w3(self):
        self.top_not()
        self.win3.attributes("-topmost",True)

    def top_not(self):
        self.win0.attributes("-topmost",False)
        self.win1.attributes("-topmost",False)
        self.win2.attributes("-topmost",False)
        self.win3.attributes("-topmost",False)

    def top_order(self):
        self.top_not()
        return
        self.win0.attributes("-topmost",1)
        self.win1.attributes("-topmost",2)
        self.win2.attributes("-topmost",3)
        self.win3.attributes("-topmost",4)

    ##########################
    # mv_file
    ########################
    def reload_text(self):
        self.read_text_file()

    def open_text(self, *args):
        self.top_order()
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
        self.read_text_file()

    def save_text(self, *args):
        s = self.get_text()
        self.write_file(self.path_text, s)

    def save_text_as(self,*args):
        self.top_order()
        path = fdialog.asksaveasfilename(title='Dove Salvare')
        if len(path) < 1:
            return
        s = self.get_text()
        name = os.path.basename(path)
        self.update_config(name)
        self.set_path_files(name)
        self.write_file(self.path_text, s)

    def quit(self):
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
        do_main_checktxt(self.path_tmp,
                         self.path_check_txt)
        self.chmod(self.path_check_txt)
        s = self.read_file(self.path_check_txt)
        self.show_win3(s)

    def elab_checkover(self):
        s = self.get_text()
        self.write_file(self.path_tmp, s)
        do_main_checkover(self.path_tmp,
                          self.path_over_tag,
                          self.path_check_over)
        self.chmod(self.path_check_over)
        s = self.read_file(self.path_check_over)
        self.show_win3(s)

    #############
    # mv_elab
    #############    
    def elab_teimxml(self):
        s = self.get_text()
        self.write_file(self.path_text, s)
        do_main_xml(self.path_text,
                    self.path_teimed_tag,
                    self.path_entity_txt)
        self.chmod(self.path_entity_txt)
        s = self.read_file(self.path_entity_txt)
        self.show_win1(s)
        print("===========")
        print("     elab_entity")
        print(self.path_text)
        print(self.path_teimed_tag)
        print(self.path_entity_txt)
        ls=["", 
        "      Elab entity",
        f"{self.path_text}",
        f"{self.path_teimed_tag}",
        f"{self.path_entity_txt}"]
        self.write_log(os.linesep.join(ls),True)

    def elab_teimlw(self):
        if not self.file_exists(self.path_entity_txt):
            self.write_log("Elaborare Entity")
            self.top_w3()
            return
        # path_txt_1 => path_xml_1
        do_main_setid(self.path_entity_txt,
                      self.path_id_xml,
                      self.text_sign)
        self.chmod(self.path_id_xml)
        print("")
        print("     elab set id")
        print(self.path_entity_txt)
        print(self.path_id_xml)
        print(self.text_sign)
        ls=["", 
        "      Elab Set id",
        f"{self.path_entity_txt}",
        f"{self.path_id_xml}",
        f"{self.text_sign}"]
        self.write_log(os.linesep.join(ls),True)

    def elab_teimover(self):
        if not self.file_exists(self.path_id_xml):
            self.write_log("Elaborare Set id o vi è stato un errore")
            self.top_w3()
            return
        # path_xml_1 => path_xml_2
        do_main_over(self.path_id_xml,
                     self.path_fromto_xml,
                     self.path_over_tag)
        self.chmod(self.path_fromto_xml)
        print("")
        print("     elab over")
        print(self.path_id_xml)
        print(self.path_fromto_xml)
        print(self.path_over_tag)
        ls=["", 
        "      Eelab over",
        f"{self.path_id_xml}",
        f"{self.path_fromto_xml}",
        f"{self.path_over_tag}"]
        self.write_log(os.linesep.join(ls),True)

    def elab_teimnote(self):
        if not self.file_exists(self.path_fromto_xml):
            self.write_log("Elaborare Over id o vi è stato un errore")
            self.top_w3()
            return
        # path_xml_2 => path_xml
        do_main_note(self.path_fromto_xml,
                     self.path_xml,
                     self.path_text_note)
        self.chmod(self.path_xml)
        print("")
        print("     elab note")
        print(self.path_fromto_xml)
        print(self.path_xml)
        print(self.path_text_note)
        ls=["", 
        "      Elab Note",
        f"{self.path_fromto_xml}",
        f"{self.path_xml}",
        f"{self.path_text_note}"]
        self.write_log(os.linesep.join(ls),True)

        # s = self.read_file(self.path_xml)
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
            print("")
            print("format_xml")
            print(self.path_xml)
            print(self.path_xml_format)

        except etree.Error as e:
            s = str(e)
            print(s)
            msg = "ERROR XML"+os.linesep+s
            self.write_log(msg)
            self.top_w3()

    ##############
    # mv_del
    ##############
    """
    def delete_text_all(self):
        # self.txt0.delete('1.0', tk.END)
        self.delete_txt1()
        self.delete_txt2()
        self.delete_txt3()
    """
    def delete_txt1(self):
        if self.txt1 is not None:
            self.txt1.delete('1.0', tk.END)
        self.delete_txt2()

    def delete_txt2(self):
        if self.txt2 is not None:
            self.txt2.delete('1.0', tk.END)

    def delete_txt3(self):
        if self.txt3 is not None:
            self.txt3.delete('1.0', tk.END)

    def remove_log(self):
        files = os.listdir(self.log_dir)
        for f in files:
            path = os.path.join(self.log_dir, f)
            absp = os.path.abspath(path)
            print(absp)
            os.remove(absp)

    ##############
    # mv_log
    ##############

    # teim/log/teimCHECK_TXT.txt
    def show_check_txt(self):
        name = self.text_src.replace(".txt", "CHECK_TXT.txt")
        path = self.get_log_path(name)
        self.read_log_file(path)

    # teim/log/teimCHECK_OVER.txt
    def show_check_over(self):
        name = self.text_src.replace(".txt", "CHECK_OVER.txt")
        path = self.get_log_path(name)
        self.read_log_file(path)

    # teim/log/teim_MED.txt
    # teim/log/teim_MED.log
    # teim/log/teim_MED.ERR.log
    def show_entity_log(self):
        name = self.text_src.replace(".txt", "_MED.log")
        path = self.get_log_path(name)
        self.read_log_file(path)

    def show_entity_err(self):
        name = self.text_src.replace(".txt", "_MED.ERR.log")
        path = self.get_log_path(name)
        self.read_log_file(path)

    #teim/log/teim_WID.log
    #teim/log/teim_WID.ERR.log        
    #teim/log/teim_WID.xml
    def show_setwid_log(self):
        name = self.text_src.replace(".txt", "_WID.log")
        path = self.get_log_path(name)
        self.read_log_file(path)

    def show_setwid_err(self):
        name = self.text_src.replace(".txt", "_WID.ERR.log")
        path = self.get_log_path(name)
        self.read_log_file(path)

    # teim/log/teim_OVER.xml
    # teim/log/teim_OVER.log
    # teim/log/teim_OVER.ERR.log
    def show_over_log(self):
        name = self.text_src.replace(".txt", "_OVER.log")
        path = self.get_log_path(name)
        self.read_log_file(path)

    def show_over_err(self):
        name = self.text_src.replace(".txt", "_OVER.ERR.log")
        path = self.get_log_path(name)
        self.read_log_file(path)

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
        if self.file_exists(path):
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
        s = self.get_path_lst_log()
        self.show_win3(s)
        self.top_w3()

    ############

    def get_text(self):
        s = self.text_edit.get('1.0', 'end')
        return s.strip()

    def read_text_file(self):
        if self.file_exists(self.path_text):
            s = self.read_file(self.path_text)
        else:
            self.write_file(self.path_text, "Empty")
            self.chmod(self.path_text)
            r = ["", f"File  {self.text_src} Not Found.",
                 "", f"Crated {self.text_src} empyt."]
            s = os.linesep.join(r)
        self.text_edit.insert_text(s)
        # show_title
        text_src = os.path.basename(self.path_text)
        title = f"TEXT: {text_src} "
        self.win0.title(title)

    def read_log_file(self,path):
        if self.file_exists(path):
            s = self.read_file(path)
        else:
            s = f"{path}   Not Found."
        self.top_w3()
        self.txt3.delete('1.0', tk.END)
        self.txt3.insert('1.0', s)
    
    def get_path_lst_log(self):
        abs_cfg = os.path.abspath(self.cfg_dir)
        abs_text = os.path.abspath(str(self.text_dir))
        wrk_dir = os.getcwd()
        logs = [
            "  ",
            "---------------------------",
            f"CONFIG: {self.json_name}",
            "---------------------------",
            "Directory",
            "---------------------------",
            f" work dir : {wrk_dir}",
            f" cfg  dir : {abs_cfg}",
            f" text dir : {abs_text}",
            "---------------------------",
            "Path",
            "---------------------------",
            f" text      : {self.path_text}",
            f" sigla.    : {self.text_sign}",
            f" note      : {self.path_text_note}",
            f" tei_tags  : {self.path_teimed_tag}",
            f" over_tags : {self.path_over_tag}",
            "---------------------------",
            "Check",
            "---------------------------",
            f"txt: {self.path_check_txt}",
            f"over: {self.path_check_over}",
            "---------------------------",
            "Log",
            "---------------------------",
            f"entity: {self.path_entity_txt}",
            f"id: {self.path_id_xml}",
            f"over: {self.path_fromto_xml}",
            f"note: {self.path_xml}",
            "---------------------------",
            " ",
        ]
        s = os.linesep.join(logs)
        return s

    def write_log(self, s, append=False):
        if append:
            x = self.txt3.get('1.0', 'end')
            s = x+os.linesep+s
        else:
            s=os.linesep+os.linesep+s
        self.txt3.delete('1.0', tk.END)
        self.txt3.insert('1.0', s)

   #########################

    def open_win1(self):
        if self.win1 is not None:
            return
        self.win1 = tk.Tk()
        self.win1.title('ENTITY')
        self.win1.protocol("WM_DELETE_WINDOW",lambda  : False)
        self.win1.rowconfigure(0, weight=1)
        self.win1.columnconfigure(0, weight=1)
        self.win1.geometry('%dx%d+%d+%d' % (w1_w, w1_h, w1_x, w1_y))
        #self.txt1 = tk.Text(self.win1,wrap=tk.NONE)
        self.txt1 = TextPad(self.win1)
        self.txt1.grid(sticky='nsew')
        self.txt1.configure(font=FONT_EDIT, bg=BG_TXT, fg=FG_TXT)
        self.txt1.vbar.config(background=BG_BAR,activebackground=BG2_BAR)

    def open_win2(self):
        if self.win2 is not None:
            return
        self.win2 = tk.Tk()
        self.win2.title('XML')
        self.win1.protocol("WM_DELETE_WINDOW",lambda  : False)
        self.win2.rowconfigure(0, weight=1)
        self.win2.columnconfigure(0, weight=1)
        self.win2.geometry('%dx%d+%d+%d' % (w2_w, w2_h, w2_x, w2_y))
        #self.txt2 = tk.Text(self.win2,wrap=tk.NONE)
        self.txt2 = TextPad(self.win2)
        self.txt2.grid(sticky='nsew')
        self.txt2.configure(font=FONT_EDIT, bg=BG_TXT, fg=FG_TXT)
        self.txt2.vbar.config(background=BG_BAR,activebackground=BG2_BAR)

    def open_win3(self):
        if self.win3 is not None:
            return
        self.win3 = tk.Tk()
        self.win3.protocol("WM_DELETE_WINDOW", lambda:False)
        self.win3.title('LOG')
        self.win3.rowconfigure(0, weight=1)
        self.win3.columnconfigure(0, weight=1)
        self.win3.geometry('%dx%d+%d+%d' % (w3_w, w3_h, w3_x, w3_y))
        #self.txt3 = tk.Text(self.win3,wrap=tk.NONE)
        self.txt3 = TextPad(self.win3)
        self.txt3.grid(sticky='nsew')
        self.txt3.configure(font=FONT_LOG, bg=BG_LOG, fg=FG_LOG)
        self.txt3.vbar.config(background=BG_BAR,activebackground=BG2_BAR)

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

def do_main(json_name="", new_json_name="", dir_name="", txt_name="", sign=""):
    tme = TeimEdit(json_name, new_json_name, dir_name, txt_name, sign)
    tme.open_win0()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print(f"author: {__author__}")
        print(f"release: {__version__} { __date__}")
        parser.print_help()
        h = """
        """
        sys.exit()

    parser.add_argument('-r',
                        dest="json",
                        required=False,
                        default="",
                        metavar="",
                        help=f"[-r read <file>.json] default:{TEIMED_CFG}")
    parser.add_argument('-c',
                        dest="newname",
                        required=False,
                        default="",
                        metavar="",
                        help="[-c create <file>.json]")
    parser.add_argument('-t',
                        dest="txt",
                        required=False,
                        default="",
                        metavar="",
                        help="[-t <file>.txt]")
    parser.add_argument('-d',
                        dest="dir",
                        required=False,
                        default="",
                        metavar="",
                        help="[-d <directory>]")
    parser.add_argument('-s',
                        dest="sign",
                        required=False,
                        default="",
                        metavar="",
                        help="[-s <sign>]")
    args = parser.parse_args()
    do_main(args.json, args.newname, args.dir, args.txt, args.sign)
