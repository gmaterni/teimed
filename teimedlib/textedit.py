#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from teimedlib.edit_constants import *
from teimedlib.findreplace import find_replace_new

class TextEdit(tk.Text):

    def __init__(self, master=None, **kw):
        self.frame = tk.Frame(master)
        self.vbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.lnumbers = tk.Canvas(self.frame)
        self.lnumbers.pack(side=tk.LEFT, fill=tk.Y)
        self.lnumbers.configure(width=50)

        kw.update({'yscrollcommand': self.vbar.set})
        kw.update({'xscrollcommand': self.hbar.set})
        tk.Text.__init__(self, self.frame, **kw)
        self.configure(wrap=tk.NONE)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.vbar['command'] = self.yview
        self.hbar['command'] = self.xview

        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(
            tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))
        self.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.configure(bg=BG_TXT, fg=FG_TXT, font=FONT_EDIT)
        self.config(undo=True)
        self.config(insertbackground=BG_CURSOR,
                    insertofftime=300,
                    insertwidth=3,
                    cursor=CURSOR_EDIT)
        self.vbar.config(background=BG_BAR,
                         activebackground=BG2_BAR, )
        self.hbar.config(background=BG_BAR,
                         activebackground=BG2_BAR, )
        self.lnumbers.config(background=BG_LNUM)

        def __str__(self):
            return str(self.frame)

        def redraw(*args):
            self.lnumbers.delete("all")
            i = self.index("@0,0")
            while True:
                dline = self.dlineinfo(i)
                if dline is None:
                    break
                y = dline[1]
                linenum = i.split(".")[0]
                self.lnumbers.create_text(2, y,
                                          anchor="nw",
                                          font=FONT_LNUM,
                                          text=linenum,
                                          fill=FG_LNUM)
                i = self.index(f"{i}+1line")

        def redraw_delay(args=None):
            self.after(20, redraw)
            self.edit_separator()


        self.vbar.bind("<B1-Motion>", redraw)
        self.bind("<FocusIn>", redraw)
        self.bind("<Enter>", redraw)
        self.bind("<Expose>", redraw)
        self.bind("<Key>", redraw_delay)
        self.bind("<MouseWheel>", redraw_delay)
        self.bind("<Button-4>", redraw_delay)
        self.bind("<Button-5>", redraw_delay)
        self.bind("<Control-KeyPress-z>", self.on_undo)
        self.bind("<Control-Shift-Z>", self. on_redo)
        self.bind("<Control-f>", self.find_replace)

    def insert_text(self, txt):
        self.delete("1.0", tk.END)
        self.insert("1.0", txt)
        self.edit_reset()

    def on_undo(self, *args):
        try:
            self.edit_undo()
        except Exception:
            pass

    def on_redo(self, *args):
        try:
            self.edit_redo()
        except Exception:
            pass

    def find_replace(self,rgs=None):
        find_replace_new(self)
