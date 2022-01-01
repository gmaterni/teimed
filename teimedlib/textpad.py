#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from teimedlib.edit_constants import *
from teimedlib.findreplace import find_replace_new

class TextPad(tk.Text):
    
    def __init__(self, master=None, **kw):
        self.frame = tk.Frame(master)
        self.vbar = tk.Scrollbar(self.frame,orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)     
        self.hbar = tk.Scrollbar(self.frame,orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM,fill=tk.X)

        kw.update({'yscrollcommand': self.vbar.set})
        kw.update({'xscrollcommand': self.hbar.set})
        tk.Text.__init__(self, self.frame, **kw)
        self.configure(wrap=tk.NONE)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.vbar['command'] = self.yview
        self.hbar['command'] = self.xview
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))
        self.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.configure(bg=BG_TXT,fg=FG_TXT,font=FONT_TXT)
        #self.config(undo=True)
        self.config(insertbackground=BG_CURSOR, insertofftime=300, insertwidth=3)
        self.vbar.config(background=BG_BAR, activebackground=BG2_BAR, )
        self.hbar.config(background=BG_BAR, activebackground=BG2_BAR, )
        self.config(cursor=CURSOR_TEXT)   
        self.bind("<Control-f>", self.find_replace)

    def find_replace(self,rgs=None):
        find_replace_new(self)

    def __str__(self):
        return str(self.frame)

    def insert_text(self,txt):
        self.delete("1.0",tk.END)
        self.insert("1.0", txt)
        #self.edit_reset()
