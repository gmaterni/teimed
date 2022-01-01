#!/usr/bin/env python3
import tkinter as tk
from teimedlib.edit_constants import *


def open_listbox(lst, fn_load_file, title=""):
    top = tk.Toplevel()
    top.update_idletasks()
    # top.transient(master)
    #top.protocol("WM_DELETE_WINDOW", lambda: False)
    top.resizable(True, False)
    top.title(title)

    lb_height = len(lst)
    lb_width = max([len(x) for x in lst])

    ws = top.winfo_screenwidth()
    x = int((ws - lb_width) / 2)

    hs = top.winfo_screenheight()
    y = int((hs - lb_height) / 2)-200

    top.geometry(f"+{x}+{y}")
    top.attributes("-topmost", True)
    lb = tk.Listbox(top, width=lb_width, height=lb_height)
    lb.pack(side='top', fill="both")
    lb.config(font=FONT_LIST,
              # selectmode=tk.SINGLE,
              activestyle=tk.UNDERLINE,
              exportselection=False,
              selectforeground=FG2_BLIST,
              selectbackground=BG2_BLIST,
              selectborderwidth=0,
              highlightthickness="0",
              bg=BG_BLIST,
              fg=FG_BLIST)
    for i in lst:
        lb.insert(tk.END, i)
    lb.focus_force()
    lb.select_set(0, 0)

    def on_select(n):
        fn_load_file(n)
        top.destroy()

    lb.bind("<Return>", lambda e: on_select(lb.curselection()[0]))
    lb.bind("<Double-Button-1>", lambda e: on_select(lb.curselection()[0]))
    lb.bind("<Escape>", lambda e: on_select(-1))
