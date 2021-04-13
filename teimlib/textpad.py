#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk

BG_BAR="#00ff00"
BG2_BAR="#FF0000"

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
        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))
        self.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    def __str__(self):
        return str(self.frame)

def do_main(txt):
    root=tk.Tk()
    root.geometry('%dx%d+%d+%d' % (600,700, 100,100))
    tp = TextPad(root)   
    tp.configure(bg='#333333',fg='#ffffff')
    
    tp.vbar.config(background=BG_BAR, activebackground=BG2_BAR, )
    tp.hbar.config(background=BG_BAR, activebackground=BG2_BAR, )

    tp.insert(tk.END, s)
    tp.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
    tp.config(cursor='arrow')   
    tp.config(insertbackground="#ff0000")
    tp.config(insertborderwidth=1)
    tp.config(insertofftime=300)
    tp.config(insertwidth=3)
    tp.focus_set()
    
    #stext.mainloop()
    root.mainloop()

if __name__ == "__main__":
    s=open("./README.txt","r").read()
    do_main(s)

