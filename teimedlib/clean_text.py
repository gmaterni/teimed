#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os


def clean_rows_(rows):
    BL = " "
    lst = []
    for row in rows:
        row = row.replace('\t', BL, -1)
        # elimina i commenti
        pc = row.find('<!')
        if pc > -1:
            row = row[0:pc - 1].strip()
        row = row.replace('\ufeff', '', -1)
        if row.strip() != '':
            lst.append(row)
    return lst


def clean_text(text=''):
    """
    rimuove i commenti e gli spazi doppi
    """    
    BL = " "
    try:
        rows = text.split(os.linesep)
        rows = clean_rows_(rows)
        text = os.linesep.join(rows)
        text = text.replace(os.linesep, BL)
        text = re.sub(r"[ ]{2,}", BL,text)
        return text
    except Exception as e:
        raise(Exception(f"ERROR clen_text() {os.linesep}{e}"))


