#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os

def clean_rows(text):
    BL = " "
    try:
        rows = text.split(os.linesep)
        lst = []
        for row in rows:
            row = row.replace('\t', BL, -1)
            # elimina i commenti
            pc = row.find('<!')
            if pc > -1:
                row = row[0:pc - 1].strip()
            row = row.replace('\ufeff', '', -1)
            row = re.sub(r"[ ]{2,}", BL, row)
            if row.strip() != '':
                lst.append(row)
        return lst
    except Exception as e:
        raise(Exception(f"Error clen_rows() {os.linesep}{e}"))


def clean_text(text):
    BL = " "
    try:
        rows = clean_rows(text)
        text = os.linesep.join(rows)
        text = text.replace(os.linesep, BL)
        # rimuove spazi multipli
        text = re.sub(r"[ ]{2,}", BL, text)
        return text
    except Exception as e:
        raise(Exception(f"Error clen_text() {os.linesep}{e}"))

