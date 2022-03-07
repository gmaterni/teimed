#!/usr/bin/env python3
# coding: utf-8
import tkinter as tk
from teimedlib.edit_constants import *


__date__ = "19-05-2021"
__version__ = "1.2.0"
__author__ = "Marta Materni"

def find_replace_new(master):
    if not FindReplaceBox.is_active:
        FindReplaceBox.is_active = True
        FindReplaceBox(master)
    #master.event_generate("<<Motion>>", x=500, y=500)


class FindReplaceBox(object):

    is_active = False

    def __init__(self, text):
        self.text = text
        top = tk.Toplevel(text.master)
        top.protocol("WM_DELETE_WINDOW", lambda: False)
        top.transient(text.master)
        top.resizable(False, False)
        # top.geometry("500x200+100+100")
        frm = tk.Frame(top)
        frm.pack(fill="both", padx=10, pady=10)
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(0, pad=8)
        frm.rowconfigure(1, pad=8)

        tk.Label(frm, font=FONT_LBL_BOX, text="Find: ").grid(
            row=0, column=0, sticky="nw")
        entry_find = tk.Entry(frm, width=30)
        entry_find.grid(row=0, column=1, sticky="new")
        entry_find.focus()

        tk.Label(frm, font=FONT_LBL_BOX, text="Replace: ").grid(
            row=1, column=0, sticky="nw")
        entry_replace = tk.Entry(frm)
        entry_replace.grid(row=1, column=1, sticky="new")
        self.index_start = tk.INSERT

        #################################
        def set_index_insert(e, *args):
            self.index_start = tk.INSERT

        self.text.bind("<Button-1>", set_index_insert)
        #################################

        def find_next():
            key = entry_find.get()
            case = case_var.get()
            exact = exact_var.get()
            if exact:
                self.find_next_exact(key, case, exact)
            else:
                self.find_next(key, case, exact)

        def replace():
            key = entry_find.get()
            rpl = entry_replace.get()
            case = case_var.get()
            exact = exact_var.get()
            #print(f"key:{key} repl:{rpl}  case:{case} exact:{exact}")
            self.replace(key, rpl, case, exact)

        def replace_all():
            key = entry_find.get()
            rpl = entry_replace.get()
            case = case_var.get()
            exact = exact_var.get()
            #print(f"key:{key} repl:{rpl}  case:{case} exact:{exact}")
            self.replace_all(key, rpl, case, exact)

        def close():
            FindReplaceBox.is_active = False
            self.text.unbind("<Button-1>")
            top.destroy()

        frm_btn = tk.Frame(frm)
        frm_btn.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")

        btn_next = tk.Button(frm_btn,  font=FONT_BTN_BOX,
                             text="Find Next", command=find_next)
        btn_next.grid(row=0, column=0, padx=(0, 6))

        btn_replace = tk.Button(frm_btn, font=FONT_BTN_BOX,
                                text="Replace", command=replace)
        btn_replace.grid(row=0, column=1, padx=(0, 5))

        btn_replace_all = tk.Button(frm_btn, font=FONT_BTN_BOX,
                                    text="Replace All", command=replace_all)
        btn_replace_all.grid(row=0, column=2)

        btn_close = tk.Button(frm_btn, font=FONT_BTN_CLOSE,
                              text="Close", command=close)
        btn_close.grid(row=0, column=3, padx=(0, 5))

        frm_opts = tk.Frame(frm)
        frm_opts.grid(row=3, column=0, sticky="nsew")

        case_var = tk.BooleanVar(top, True)
        case_var.set(False)
        chk_case = tk.Checkbutton(frm_opts, font=FONT_BTN_BOX,
                                  text="Match Case", variable=case_var)
        chk_case.grid(row=0, column=0, sticky="sw")

        exact_var = tk.BooleanVar(top, True)
        exact_var.set(True)
        chk_exact = tk.Checkbutton(frm_opts, font=FONT_BTN_BOX,
                                   text="Exact", variable=exact_var)
        chk_exact.grid(row=0, column=1, sticky="sw")

    def find_next_exact(self, key, case, exact):
        n_pos = 0
        n_parz=0
        n_end=0 # numero tentativi 
        while True:
            pos = self.text.search(key,
                                   self.index_start,
                                   nocase=not case,
                                   exact=exact)
                                   #stopindex=tk.END)
            #print(f"{n_pos}")
            if pos:
                n_pos += 1
                index_end = f'{pos}+{len(key)}c'
                ws = f'{pos} wordstart'
                we = f'{pos} wordend'
                w = self.text.get(ws, we)
                #print(f"{key}   |{w}|")
                if w != key:
                    n_parz+=1
                    x=self.text.compare(self.index_start,'>=',index_end)
                    if x:
                        n_end+=1
                    #print(f"pos:{n_pos} parz:{n_parz} ext:{n_end }   {x}")
                    if (x and n_end > 1) or n_parz >100:
                        if self.text.tag_ranges(tk.SEL):
                            self.text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
                        self.index_start = tk.INSERT
                        #print("brek 2")
                        break
                    self.index_start = index_end
                    continue
                if self.text.tag_ranges(tk.SEL):
                    self.text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
                self.text.tag_add(tk.SEL, pos, index_end)
                #self.text.mark_set(tk.INSERT, index_end)
                self.text.see(index_end)
                self.index_start = index_end
                #print("brek 0")
                break
            else:
                if n_pos==0:
                    if self.text.tag_ranges(tk.SEL):
                        self.text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
                    self.index_start = tk.INSERT
                    #print("brek 1")
                    break

    def find_next(self, key, case, exact):
        pos = self.text.search(key,
                               self.index_start,
                               nocase=not case,
                               exact=exact,
                               regexp=False)
        if pos:
            index_end = f'{pos}+{len(key)}c'
            if self.text.tag_ranges(tk.SEL):
                self.text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            self.text.tag_add(tk.SEL, pos, index_end)
            #self.text.mark_set(tk.INSERT, index_end)
            self.text.see(index_end)
            self.index_start = index_end
        else:
            if self.text.tag_ranges(tk.SEL):
                self.text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)

    def replace(self, key, repl, case, exact):
        sel_range = self.text.tag_ranges(tk.SEL)
        if sel_range:
            selection = self.text.get(sel_range[0], sel_range[1])
            if not case:
                key = key.lower()
                selection = selection.lower()
            if key == selection:
                self.text.delete(sel_range[0], sel_range[1])
                self.text.insert(sel_range[0], repl)
        self.find_next(key, case, exact)

    def replace_all(self, key, repl, case, exact):
        if key.strip()=='':
            return
        start = "1.0"
        while True:
            pos = self.text.search(key,
                                   start,
                                   tk.END,
                                   regexp=False,
                                   exact=exact,
                                   nocase=not case)
            if pos:
                self.text.delete(pos, f"{pos}+{len(key)}c")
                self.text.insert(pos, repl)
                start = f"{pos}+{len(repl)}c"
            else:
                break

    def xx(self, key, repl, case, exact):
        pass
