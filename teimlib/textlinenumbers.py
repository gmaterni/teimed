#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk

from teimlib.teimstyle import *

class TextLineNumbers(tk.Text):
    
    def __init__(self, master=None, **kw):
        self.frame = tk.Frame(master)
        self.vbar = tk.Scrollbar(self.frame,orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)     
        self.hbar = tk.Scrollbar(self.frame,orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM,fill=tk.X)
        
        self.lnumbers=tk.Canvas(self.frame)
        self.lnumbers.pack(side=tk.LEFT, fill=tk.Y)     
        self.lnumbers.configure(width=40)

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

        def redraw_delay(*args):
            self.after(2, redraw)

        self.vbar.bind("<B1-Motion>", redraw)
        self.bind("<Expose>", redraw)
        self.bind("<Key>", redraw_delay)
        self.bind("<MouseWheel>", redraw_delay)
        self.bind("<Button-4>", redraw_delay)
        self.bind("<Button-5>", redraw_delay)

    def on_undo(self,*args):
        pass
    
    def on_copy(self,*args):
        pass
    
    def on_cut(self,*args):
        pass
    
    def on_paste(self,*args):
        pass

    def insert_text(self,txt):
        self.delete("1.0",tk.END)
        self.insert("1.0", txt)


def do_main(txt):
    root=tk.Tk()
    root.geometry('%dx%d+%d+%d' % (600,700, 100,100))
    tpn = TextLineNumbers(root)   
    tpn.configure(bg=BG_TXT,fg=FG_TXT,font=FONT_EDIT)
    tpn.vbar.config(background=BG_BAR, activebackground=BG2_BAR, )
    tpn.hbar.config(background=BG_BAR, activebackground=BG2_BAR, )
    tpn.lnumbers.config(background=BG_LNUM)
    tpn.insert_text(txt)
    tpn.focus_set()
    #stext.mainloop()
    root.mainloop()

if __name__ == "__main__":
    txt=open("./README.txt","r").read()
    print(txt)
    do_main(txt)

