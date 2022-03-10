#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import sys
import re
import os
import io
from teimedlib.ualog import Log
from teimedlib.teim_paths import *

__date__ = "25-07-2021"
__version__ = "1.1.12"
__author__ = "Marta Materni"

"""
read_text_rows
add_spc2punct
join_words_wrap
clean_brackets
"""


class TeimTxtRead(object):
    SP = ' '
    WRP = '='
    LB_TMP='XXXX'

    def __init__(self, path_text, log_err=None):
        self.path_text = path_text
        if log_err is None:
            path_err = set_path_teim_err(path_text)
            self.log_errr = Log('w').open(path_err, 1).log
        else:
            self.log_err = log_err

    def join_words_wrap(self, rows):
        """ unisce l'ultima word di una riga che 
        termia con = con la prima della successiva

        riga di prova, vedia=
        mo come va

        riga di prova, vediaXXXXmo
        come va

        Nuova versione
        riga di prova, vedia=mo 
        come va

        riga di prova, vediaXXXXmo
        come va

        il flag XXXX serve per gestire <lb> che
        non verra' inserito all'inizio della riga successiva

        """
        for i in range(0, len(rows)):
            try:
                # if rows[i].find(self.WRP) > -1:
                #     words = rows[i+1].split(' ')
                #     word0 = words[0]
                #     # elimina la prima word dalla riga successiva
                #     words = words[1:]
                #     rows[i+1] = self.SP.join(words)
                #     # AAA aggiunge la prima word dela riga successiva alla
                #     # fine della riga corrente
                #     # sostituisce '=' con LB_TMP 'XXXX'
                #     #rows[i] = rows[i].replace(self.WRP, word0)
                #     # rows[i] = rows[i].replace(self.WRP,f"{self.LB_TMP}{word0}")
                #     # Nuova versione
                #     rows[i] = rows[i].replace(self.WRP,self.LB_TMP)

                if rows[i].find(self.WRP) > -1:
                    words_next = rows[i+1].split(' ')
                    if rows[i][-1:]==self.WRP:
                        word0 = words_next[0]
                        rows[i+1] = self.SP.join(words_next[1:])
                        rows[i] = rows[i].replace(self.WRP,f"{self.LB_TMP}{word0}")
                    else:
                        rows[i] = rows[i].replace(self.WRP,self.LB_TMP)


            except Exception as e:
                self.log_err(f'ERROR 1 join_words_wrap().')
                self.log_err(f'row num:{i+1}')
        return rows

    def clean_brackets(self, rows):
        """
            rimuove blk allintero delle parentesi ()
        """
        out = io.StringIO("")
        for n, row in enumerate(rows):
            np = 0
            for c in row:
                if c == '(':
                    np += 1
                elif c == ')':
                    np -= 1
                if c == self.SP and np > 0:
                    continue
                out.write(c)
            out.write(os.linesep)
            if np != 0:
                self.log_err(f"ERROR 2 parentesi '()' non bilanciate")
                self.log_err(f"row num:{n+1}")
                self.log_err(f"{row}")
        out.seek(0)
        rs = out.readlines()
        out.close()
        rows = [r.strip() for r in rs]
        return rows

    def text_add_spc_to_punct(self, text):
        """
        aggiunge spazi a ddestra e sinistra della punteggiatura
        al di fuori delle () e non considerando &abc;
        """
        ent = False
        p_oc = 0
        f = io.StringIO("")
        for c in text:
            sp = False
            if c in ".:!?":
                sp = True
            elif c == ',':
                if p_oc == 0:
                    sp = True
            elif c == ';':
                if p_oc == 0 and ent is False:
                    sp = True
                if ent:
                    ent = False
            elif c == '&':
                ent = True
            elif c == ' ':
                ent = False
            elif c == '(':
                p_oc += 1
            elif c == ')':
                p_oc -= 1
            if sp:
                f.write(self.SP)
                f.write(c)
                f.write(self.SP)
            else:
                f.write(c)
        f.seek(0)
        text = f.read()
        f.close()
        text = re.sub(r"[ ]{2,}", self.SP, text)
        return text

    def add_spc_to_punct(self, rows):
        for i, row in enumerate(rows):
            rows[i] = self.text_add_spc_to_punct(row)
        return rows

    # AAA  flag id per per inizio numeraione
    def read_flags_id(self):
        """
        legge flags id  per numerazione in testa al 
        file sorgente
        """
        rows = []
        try:
            fr = open(self.path_text, "r")
            print(self.path_text)
            # HEACK while (row := fr.readline()) != '':
            while True:
                row = fr.readline()
                if not row:
                    break
                row = row.replace('\t', self.SP, -1)
                # flag @abc;....
                m = re.search(r'@[\w]+:', row)
                if m is not None:
                    g = m.group()
                    m_end = m.end()
                    tag = g.replace('@', '')
                    src = row[m_end:].strip()
                    s = f'{tag}{src}'
                    s = s.replace(self.SP, '')
                    rows.append(s)
            fr.close()
        except Exception as e:
            msg = f"ERROR 3 read_flag_id() \n{e}"
            sys.exit(msg)
        else:
            return rows

    def read_text_rows(self):
        """
        Elimina commenti e flag id

        """
        rows = []
        try:
            fr = open(self.path_text, "r")
            # HEACK while (row := fr.readline()) != '':
            while True:
                row = fr.readline()
                if not row:
                    break
                row = row.replace('\t', self.SP, -1)

                # elimina i commenti
                p_comment = row.find('<!')
                if p_comment > 0:
                    row = row[0:p_comment-1].strip()
                elif p_comment == 0:
                    row = ''

                # flag id  @abc;....
                if re.search(r'@[\w]+:', row) is not None:
                    row = ''

                row = row.replace('\ufeff', '', -1)
                row = row.strip()
                row = re.sub(r"[ ]{2,}", self.SP, row)
                rows.append(row)
            fr.close()
        except Exception as e:
            msg = f"ERROR 4 read_text_rows() \n{e}"
            sys.exit(msg)
        else:
            return rows
