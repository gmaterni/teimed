#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from teimedlib.edit_constants import *

def open_listbox(root,lst,on_select,dx=100,dy=100):
    on_select=on_select
    root.update_idletasks()
    x=root.winfo_rootx()+dx
    y=root.winfo_rooty()+dy
    wnd=tk.Tk()
    wnd.protocol("WM_DELETE_WINDOW", lambda: False)
    wnd.attributes("-topmost", True)
    #wnd.grab_set()
    wnd.geometry(f"+{x}+{y}")
    wnd.title("")
    wnd.rowconfigure(0, weight=1)
    wnd.columnconfigure(0, weight=1)
    lb = tk.Listbox(wnd)
    ls=[len(x) for x in lst]
    w = max(ls)
    lb.config(width=w)
    lb.grid(row=0,column=0,sticky="nswe")
    height=len(lst)
    lb.config(font=FONT_LIST,
                #selectmode=tk.SINGLE,
                activestyle=tk.UNDERLINE,
                exportselection=False,
                height=height,
                selectforeground=FG2_BLIST,
                selectbackground=BG2_BLIST,
                selectborderwidth=0,
                highlightthickness="0",
                bg=BG_BLIST,
                fg=FG_BLIST)
    for i in lst:
        lb.insert(tk.END, i)
    lb.focus_force()
    lb.select_set(0,0)

    def select_(n):
        on_select(n)
        wnd.destroy()

    lb.bind("<Return>", lambda e:select_(lb.curselection()[0]))
    lb.bind("<Double-Button-1>",lambda e: select_(lb.curselection()[0]))
